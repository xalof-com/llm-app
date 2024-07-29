from datetime import timezone, timedelta, datetime
import hashlib, time, zlib, os
import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError
from dotenv import find_dotenv, load_dotenv


load_dotenv(find_dotenv())

class Hash:
    
    @staticmethod
    def bcrypt(password:str = None) -> str:
        if password is None:
            password = str(time.time())
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=10))
    
    @staticmethod
    def verify_bcrypt(hashed_password:str, pure_password:str) -> bool:
        return bcrypt.checkpw(pure_password.encode('utf-8'), hashed_password)
    
    @staticmethod
    def md5(secret:str = None) -> str:
        if secret is None:
            secret = str(time.time())
        return hashlib.md5(secret.encode('utf-8')).hexdigest()
    
    @staticmethod
    def crc32(secret:str = None) -> str:
        if secret is None:
            secret = str(time.time())
        return str(zlib.crc32(secret.encode('utf-8')))
    

class JWTToken:

    @staticmethod
    def get_access_token(payload:dict) -> str:
        expires_delta = timedelta(minutes=int(os.getenv("JWT_TOKEN_EXPIRE_MINUTES")))
        payload["exp"] = datetime.now() + expires_delta
        return jwt.encode(payload, key=os.getenv("JWT_KEY"), algorithm=os.getenv("JWT_ALGORITHM"))
        
