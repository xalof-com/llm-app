# from pydantic import BaseModel, Field
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Type

from langchain.tools import BaseTool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
# from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.chains.sql_database.query import create_sql_query_chain
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore
from langchain_groq import ChatGroq

from finance.stock import fetch_stock_price
from finance.gold import sjc_gold_price
from datetime import datetime
from ai.rag_db import SingletonRagDB_FF8, SingletonRagDB_PNTT, SingletonRagDB_BDS
from ai.llm import SingletonChatLLM
from database import get_db
from ai.prompt_templates import answer_sql_prompt, write_sql_prompt, sql_few_shot_prompt

import os
import re
import json
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


# Define tool functions

def get_current_time_tool(*args, **kwargs) -> str:
    return datetime.now().strftime("%H:%M")


def get_sjc_gold_price_tool(*args, **kwargs):
    return {'price': sjc_gold_price()}


def get_rag_qa_tool(query, **kwargs):
    
    root_path = os.getenv('LLM_APP_ROOT_PATH')
    rag_db_name = kwargs.get('db_name', 'chromadb_ff8')
    from_url = kwargs.get('from_url', False)
    
    # db_dir = f"{root_path}/ragdb/{rag_db_name.lower()}db_ff8"

    db_dir = os.path.join(root_path, 'ragdb', f"{rag_db_name}")
    embedding_model = os.getenv('HF_EMBEDDING_MODEL_NAME')

    if from_url == False:
        if 'ff8' in rag_db_name:
            ragdb = SingletonRagDB_FF8(db_dir, embedding_model)
        elif 'pntt' in rag_db_name:
            ragdb = SingletonRagDB_PNTT(db_dir, embedding_model)
        else:
            ragdb = SingletonRagDB_BDS(db_dir, embedding_model)

        retriever = ragdb.get_db().as_retriever(search_type='similarity')
    else:
        ragdb = _get_data_from_url_tool(rag_db_name)
        retriever = ragdb.as_retriever(search_type='similarity')

    # retriever = ragdb.get_db().as_retriever(search_type='similarity', search_kwargs={'k': 3})
    # retriever = ragdb.get_db().as_retriever(search_type='similarity_score_threshold',
    #                                search_kwargs={'score_threshold': 0.4})
    # retriever = ragdb.get_db().as_retriever(search_type='similarity')
    # retriever = ragdb.get_db().as_retriever(search_type='mmr')

    chatllm = SingletonChatLLM(llm_name=os.getenv('CHAT_LLM_NAME'))
    llm = chatllm.get_llm()
    
    # # Contextual question prompt
    # # Helps AI figure out that it should refomulate the question based on the chat history
    # aware_retriever_system_messages = [
    #     "Given a chat history and the latest user question ",
    #     "which might be referenced context in the chat history, ",
    #     "produce a standalone question which can be understood without the chat history.",
    #     "DO NOT answer the question, just reformulate it if needed and otherwise return it as is."
    # ]

    # aware_retriever_prompt = ChatPromptTemplate.from_messages([
    #     SystemMessage(content=aware_retriever_system_messages),
    #     MessagesPlaceholder("chat_history"),
    #     ('human', "{input}")
    # ])

    # hist_aware_retriever = create_history_aware_retriever(llm, retriever, aware_retriever_prompt)

    # Answer question prompt
    # Helps AI understand that it should provide concise answers
    qa_system_messages = [
        "You are a good assistant for question-answering tasks by using Vietnamese language only. "
        # "Use the same language as in the question to answer. "
        "You MUST use the following pieces of retrieved context below to answer the question. "
        "If you don't know the answer with the retrieved context, just say that you don't know. "
        "Use 5 to 10 sentences maximum and keep the answer consise. "
        "Additionally, please include the source, page of the documents of retrieved context that related to the anwser."
        
        # "Bạn là trợ lý cho các nhiệm vụ trả lời câu hỏi bằng Tiếng Việt (Vietnamese), "
        # "Không dùng Tiếng Anh (English), chỉ dùng Tiếng Việt (Vietnamese) để trả lời. "
        # "Bạn phải sử dụng các phần ngữ cảnh được truy xuất sau đây để trả lời câu hỏi. "
        # # # "Nếu trong ngữ cảnh không có nội dung cần tìm, "
        # # # "bạn có thể sử dụng kiến thức có sẳn của bạn để trả lời câu hỏi. "
        # # # "Trích dẫn source, page cho câu trả lời. "
        # # # "Không tính nguồn và trang, sử dụng tối đa ba câu đẩ câu trả lời ngắn gọn."
        # "Nếu bạn không biết câu trả lời, chỉ cần nói là bạn không biết. "
        # "Sử dụng tối đa ba câu và giữ câu trả lời ngắn gọn. "
        # "Ngoài ra, vui lòng ghi rõ nguồn, trang của các tài liệu ngữ cảnh được truy xuất có liên quan đến câu trả lời."
        # "Luôn nói 'Cảm ơn bạn đã hỏi nha!' ở cuối câu trả lời."
        "\n\n"
        "{context}"
    ]

    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", "".join(qa_system_messages)),
        # MessagesPlaceholder("chat_history"),
        ("human", "{input}")
        
    ])

    if from_url == False:
        document_combine_prompt = PromptTemplate(
            template="""
                Content: {page_content}\n
                Nguồn: {source} \n
                Trang: {page} \n
            """,
            input_variables=['page_content', 'source', 'page']

        )
    else:
        document_combine_prompt = PromptTemplate(
            template="""
                Content: {page_content}\n
                Nguồn: {source} \n
            """,
            input_variables=['page_content', 'source']

        )

    qa_doc_chain = create_stuff_documents_chain(llm, qa_prompt, document_prompt=document_combine_prompt) # combine_doc_chain
    
    # rag_chain = create_retrieval_chain(hist_aware_retriever, qa_doc_chain)
    rag_chain = create_retrieval_chain(retriever, qa_doc_chain)    
  
    print(f"\n\n.::. Rag Query: {query}")
    
    response = rag_chain.invoke(input={'input': query, "chat_history": kwargs.get("chat_history", [])})

    # for doc in response['context']:
    #     new_metadata = {
    #         'source': doc.metadata.get('source', 'Unknown'),
    #         'page': doc.metadata.get('page', 'Unknown')
    #     }
    #     doc.metadata = new_metadata

    print("\n\n===================================")
    print(f".::. RAG :", response)
    print("===================================")   

    return {'answer': response['answer'].strip("\n\n")}
    

def get_data_from_mysqldb_tool(query, **kwargs):
    db = get_db()
    if db != None:
        chatllm = SingletonChatLLM(llm_name=os.getenv('CHAT_LLM_NAME'))
        llm = chatllm.get_llm()
        # sql_prompt = write_sql_prompt()

        few_shot_prompt = sql_few_shot_prompt()
        # print(few_shot_prompt.format(input="How many artists are there?", top_k=3, table_info="foo"))

        write_sql_chain = create_sql_query_chain(llm, db, prompt=few_shot_prompt)

        # write_sql_chain = (
        #     RunnablePassthrough.assign(table_info=lambda x: db.get_table_info())
        #     | sql_prompt.partial(top_k=5)
        #     | llm.bind(stop=["\nSQLResult:"])
        #     | StrOutputParser()
        # )

        # sql_response = write_sql_chain.invoke({'question': query})
        # print(sql_response)

        # answer_prompt = answer_sql_prompt()

        answer_chain = (
            # RunnablePassthrough.assign(query=write_sql_chain).assign(result=lambda x: db.run_no_throw(re.findall(r"```sql(.*)```", x['query'].replace('\n', ' ').strip())[0]))
            RunnablePassthrough.assign(query=write_sql_chain).assign(result=lambda x: db.run_no_throw(_clean_sql_string(x['query'])))
            # | answer_prompt
            # | llm
            # | StrOutputParser()
        )

        response = answer_chain.invoke({"question": query})
        print(response)

        return response
    
    return {'result': ""}

def _clean_sql_string(sql:str):
    for s in ["SQLQuery:", "SQL Query:", "SQLquery:", "SQL query:"]:
        if s in sql:
            sql = sql.replace(s, "")

    sql = sql.strip().replace('\n', ' ')
    if "```sql" in sql:
        sql = re.findall(r"```sql(.*)```", sql)[0]
    return sql

def _get_data_from_url_tool(source_name:str):
    urls_file = f"{os.getenv('LLM_APP_ROOT_PATH')}/data_src/WEB/urls.json"

    cache_dir = f"{os.getenv('LLM_APP_ROOT_PATH')}/cache/web_urls/{source_name}"
    if os.path.exists(cache_dir) == False:
        os.makedirs(cache_dir, exist_ok=True)

    sources = None
    with open(urls_file, mode="r", encoding="utf-8") as f:
        sources = json.load(f)
        f.close()

    loader = WebBaseLoader(sources[source_name]['urls'])
    doc_chunks = loader.load_and_split(RecursiveCharacterTextSplitter())

    store = LocalFileStore(cache_dir)
    embedding_model = HuggingFaceEmbeddings(model_name=os.getenv('HF_EMBEDDING_MODEL_NAME'))

    cached_embedder = CacheBackedEmbeddings.from_bytes_store(
        embedding_model, store, namespace=os.getenv('HF_EMBEDDING_MODEL_NAME')
    )

    chroma_db = Chroma.from_documents(doc_chunks, cached_embedder)
    return chroma_db

#==================================================================================================
# class AnswerWithSource(BaseModel):
#     answer:str = Field(description = "The final answer to respond to the user")
#     source:str = Field(description = "The source file that contain the answer to the question. Only include source file if it contains relevant information")
#     page:int = Field(description = "The page number of source that contain the answer to the question. Only include page file if it contains relevant information")

#*****************************************************************************
class CurrentStockPriceInput(BaseModel):
    ticker:str = Field(description='The ticker symbol of the stock(s) or market index')

class CurrentStockPriceTool(BaseTool):
    name:str = 'stock_price'
    description:str = """
        Useful for when you want to get the current price of stocks or current market index.
    """
    args_schema: Type[BaseModel] = CurrentStockPriceInput

    def _run(self, ticker:str):
        price = fetch_stock_price(ticker)
        return price

#*****************************************************************************
class RAGQuestionAnswerInput(BaseModel):
    query:str = Field(description="The query or input string of the human")

class RAGQuestionAnswerTool(BaseTool):
    name:str = "question_answering"
    db_name:str = "chromadb_ff8"
    from_url:bool = False
    description:str = """
        Hữu ích khi bạn muốn trả lời các câu hỏi liên quan đến game 'Final Fantasy 8'
    """
    args_schema: Type[BaseModel] = RAGQuestionAnswerInput

    def _run(self, query:str):
        response = get_rag_qa_tool(query, db_name=self.db_name, from_url=self.from_url)
        return response

#*****************************************************************************
class SQLTableName(BaseModel):
    name: str = Field(description="Name of table in SQL database.")


class SQLQueryInput(BaseModel):
    query:str = Field(description="The query or input string of the human")

class SQLQueryTool(BaseTool):
    name:str = "sql_query_tool"
    description:str = """
        Hữu ích khi bạn muốn trả lời các câu hỏi liên quan đến truy vấn dữ liệu từ database: kênh bán hàng, sàn giao dịch, sản phẩm
    """
    args_schema: Type[BaseModel] = SQLQueryInput

    def _run(self, query:str):
        response = get_data_from_mysqldb_tool(query)
        return response