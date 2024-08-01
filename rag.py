import os
from dotenv import load_dotenv, find_dotenv
from tqdm import tqdm
from langchain_chroma import Chroma
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings


load_dotenv(find_dotenv())

os.environ['LLM_APP_ROOT_PATH'] = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = os.getenv('LLM_APP_ROOT_PATH')

def _load_pdf_files(src_dir:str):
    list_pages = []
    for file_name in tqdm(os.listdir(src_dir)):
        file_path = f"{src_dir}/{file_name}"
        
        pdf_loader = PyMuPDFLoader(file_path)
        pages = pdf_loader.load()
        for p in pages:
            p.metadata['page'] += 1
                
        list_pages += pages # list_pages.extend(pages)

    return list_pages

def _create_vector_store_db(doc_pages:list, db_dir:str, vector_store:str='chroma', embedding_model:str=None):
    if embedding_model == None:
        embedding_model = 'multi-qa-mpnet-base-cos-v1'

    txt_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = txt_splitter.split_documents(doc_pages)
            
    embedding = HuggingFaceEmbeddings(model_name=embedding_model)
    if vector_store.lower() == 'chroma':
        db = Chroma.from_documents(documents=texts, embedding=embedding, persist_directory=db_dir)
    else:
        db = FAISS.from_documents(documents=texts, embedding=embedding)
        db.save_local(db_dir)
    return db

def _load_vector_store_db(db_dir:str, vector_store:str='chroma', embedding_model:str=None):
    if embedding_model == None:
        embedding_model = 'multi-qa-mpnet-base-cos-v1'

    embedding = HuggingFaceEmbeddings(model_name=embedding_model)
    if vector_store.lower() == 'chroma':
        db = Chroma(embedding_function=embedding, persist_directory=db_dir)
    else:
        db = FAISS.load_local(folder_path=db_dir, embeddings=embedding, allow_dangerous_deserialization=True)
    return db


if __name__ == '__main__':
    
    src_dir = f"{ROOT_PATH}/data_src/LEGAL"
    rag_db_dir = f"{ROOT_PATH}/ragdb"
    if os.path.exists(rag_db_dir) == False:
        os.makedirs(rag_db_dir, exist_ok=True)
    
    vector_store = os.getenv('RAG_DB')
    
    db_dir = f"{rag_db_dir}/{vector_store.lower()}db_bds2023"

    embedding_model = os.getenv('HF_EMBEDDING_MODEL_NAME')
    # embedding_model = 'multi-qa-MiniLM-L6-cos-v1'
    # embedding_model = 'multi-qa-mpnet-base-cos-v1'
    # embedding_model = 'VoVanPhuc/sup-SimCSE-VietNamese-phobert-base'
    rag_db = None
    if os.path.exists(db_dir) == False:
        print(f'.::.The {vector_store} vector store does not exist. Init...')
        pdf_pages = _load_pdf_files(src_dir)
        rag_db = _create_vector_store_db(pdf_pages, db_dir, vector_store=vector_store, embedding_model=embedding_model)
        print(f'.::.Finished creating {vector_store} vector store.')
    else:
        print(f'.::.The {vector_store} vector store already exists. {db_dir}')
        rag_db = _load_vector_store_db(db_dir, vector_store=vector_store, embedding_model=embedding_model)
    
    
    retriever = rag_db.as_retriever(search_type='similarity')   
    # retriever = rag_db.as_retriever(search_type='similarity', search_kwargs={'k': 3})   
    # retriever = rag_db.as_retriever(search_type='mmr')   
    # retriever = rag_db.as_retriever(search_type='similarity_score_threshold',
    #                                search_kwargs={'score_threshold': 0.4})   

    while True:
        try:
            query = input("You: ")
            if query.lower() in ["exit", "quit"]:
                break

            relevant_docs = retriever.invoke(query)
            print(len(relevant_docs))
            for i, doc in enumerate(relevant_docs, 1):
                print(f"\n\n{'='*50}")
                print(f".::.Document {i}:")
                print(f"---Content: {doc.page_content}")
                if doc.metadata:
                    print(f"\n\n---Source: {doc.metadata.get('source', 'Unknown')}")
                    print(f"---Page: {doc.metadata.get('page', 'Unknown')}")

        
        except Exception as err:
            import traceback
            print(traceback.print_exc())
            break



    # q = "Tìm GF Ifrit ở đâu?"

    # relevant_docs = retriever.invoke(q)

    # for i, doc in enumerate(relevant_docs, 1):
    #     print(f".::.Document {i}:")
    #     print(doc.page_content)
    #     if doc.metadata:
    #         print(f"---Source: {doc.metadata.get('source', 'Unknown')}")
    #         print(f"---Page: {doc.metadata.get('page', 'Unknown')}")

    # file_path = f"data_src/PNTT/tom_tat_PNTT_01.pdf"
    # pdf_loader = PyMuPDFLoader(file_path)
    # pages = pdf_loader.load()
    # for page in pages:
    #     page.metadata['page'] += 1
    
    # print(pages)
    

    
    