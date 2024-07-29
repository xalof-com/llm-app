
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings



class SingletonRagDB_FF8:
    _instance = None
    
    def __init__(self, db_dir:str, embedding_model:str):
        self.db:Chroma = None
        self._load_vector_db(db_dir, embedding_model)
        
    def __new__(cls, *args, **kwargs):
        if cls._instance == None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def _load_vector_db(self, db_dir:str, embedding_model:str):
        embedding = HuggingFaceEmbeddings(model_name=embedding_model)
        self.db = Chroma(embedding_function=embedding, persist_directory=db_dir)
    
    def get_db(self):
        return self.db

class SingletonRagDB_PNTT:
    _instance = None
    
    def __init__(self, db_dir:str, embedding_model:str):
        self.db:Chroma = None
        self._load_vector_db(db_dir, embedding_model)
        
    def __new__(cls, *args, **kwargs):
        if cls._instance == None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def _load_vector_db(self, db_dir:str, embedding_model:str):
        embedding = HuggingFaceEmbeddings(model_name=embedding_model)
        self.db = Chroma(embedding_function=embedding, persist_directory=db_dir)
    
    def get_db(self):
        return self.db
    
class SingletonRagDB_BDS:
    _instance = None
    
    def __init__(self, db_dir:str, embedding_model:str):
        self.db:Chroma = None
        self._load_vector_db(db_dir, embedding_model)
        
    def __new__(cls, *args, **kwargs):
        if cls._instance == None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def _load_vector_db(self, db_dir:str, embedding_model:str):
        embedding = HuggingFaceEmbeddings(model_name=embedding_model)
        self.db = Chroma(embedding_function=embedding, persist_directory=db_dir)
    
    def get_db(self):
        return self.db
