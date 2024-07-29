from pydantic import BaseModel, Field
from typing import Type

from langchain.tools import BaseTool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
# from langchain.chains.retrieval_qa.base import RetrievalQA


from finance.stock import fetch_stock_price
from finance.gold import sjc_gold_price
from datetime import datetime
from ai.rag_db import SingletonRagDB_FF8, SingletonRagDB_PNTT, SingletonRagDB_BDS
from ai.llm import SingletonChatLLM

import os
import json
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())



# Define tool functions

def get_current_time_tool(*args, **kwargs) -> str:
    return datetime.now().strftime("%H:%M")

# def get_stock_price_tool(ticker:str) -> dict:
#     payload = fetch_stock_price(ticker)
#     return payload

def get_sjc_gold_price_tool(*args, **kwargs):
    return {'price': sjc_gold_price()}

def get_rag_qa_tool(query, **kwargs):
    
    root_path = os.getenv('LLM_APP_ROOT_PATH')
    rag_db_name = kwargs.get('db_name', 'chromadb_ff8')
    # db_dir = f"{root_path}/ragdb/{rag_db_name.lower()}db_ff8"

    db_dir = os.path.join(root_path, 'ragdb', f"{rag_db_name}")
    embedding_model = os.getenv('HF_EMBEDDING_MODEL_NAME')

    if 'ff8' in rag_db_name:
        ragdb = SingletonRagDB_FF8(db_dir, embedding_model)
    elif 'pntt' in rag_db_name:
        ragdb = SingletonRagDB_PNTT(db_dir, embedding_model)
    else:
        ragdb = SingletonRagDB_BDS(db_dir, embedding_model)

    # retriever = ragdb.get_db().as_retriever(search_type='similarity', search_kwargs={'k': 3})
    # retriever = ragdb.get_db().as_retriever(search_type='similarity_score_threshold',
    #                                search_kwargs={'score_threshold': 0.4})
    retriever = ragdb.get_db().as_retriever(search_type='similarity')
    # retriever = ragdb.get_db().as_retriever(search_type='mmr')

    chatllm = SingletonChatLLM()
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
        "You MUST use the following pieces of retrieved context to answer the question. "
        "If you don't know the answer with the retrieved context, just say that you don't know. "
        "Use 5 sentences maximum and keep the answer consise. "
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
        ("system", qa_system_messages),
        # MessagesPlaceholder("chat_history"),
        ("human", "{input}")
        
    ])

    document_combine_prompt = PromptTemplate(
        template="""
            Content: {page_content}\n
            Nguồn: {source} \n
            Trang: {page} \n
        """,
        input_variables=['page_content', 'source', 'page']

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

    return {'answer': response['answer']}
    

# class AnswerWithSource(BaseModel):
#     answer:str = Field(description = "The final answer to respond to the user")
#     source:str = Field(description = "The source file that contain the answer to the question. Only include source file if it contains relevant information")
#     page:int = Field(description = "The page number of source that contain the answer to the question. Only include page file if it contains relevant information")


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
    
class RAGQuestionAnswerInput(BaseModel):
    query:str = Field(description="The query or input string of the human")

class RAGQuestionAnswerTool(BaseTool):
    name:str = "question_answering"
    db_name:str = "chromadb_ff8"
    description:str = """
        Hữu ích khi bạn muốn trả lời các câu hỏi liên quan đến game 'Final Fantasy 8'
    """
    args_schema: Type[BaseModel] = RAGQuestionAnswerInput

    def _run(self, query:str):
        response = get_rag_qa_tool(query, db_name=self.db_name)
        return response