import os
from dotenv import load_dotenv, find_dotenv
from langchain_community.utilities import SQLDatabase

load_dotenv(find_dotenv())

def _get_conn_string():
    _db_conn = os.getenv('DB_CONNECTION')
    _username = os.getenv('DB_USERNAME')
    _pass = os.getenv('DB_PASSWORD')
    _db_host = os.getenv('DB_HOST')
    _db_port = os.getenv('DB_PORT')
    _db_name = os.getenv('DB_DATABASE')
    _db_driver = os.getenv('DB_DRIVER')

    # str_conn = f"{_db_conn}+psycopg2://{_username}:{_pass}@{_db_host}:{_db_port}/{_db_name}"
    str_conn = f"{_db_conn}+{_db_driver}://{_username}:{_pass}@{_db_host}:{_db_port}/{_db_name}"
    return str_conn



def get_mysqldb(pool_size:int=5):
    
    try:
        str_conn = _get_conn_string()
        db = SQLDatabase.from_uri(str_conn, engine_args={"pool_size": pool_size, "max_overflow": 0})
        return db
    except Exception as err:
        print(err)
    
    return None
