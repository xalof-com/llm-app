import os
from dotenv import load_dotenv, find_dotenv
from enum import Enum

from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv(find_dotenv())

class SingletonChatLLM:
    _instance = None

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0,
            google_api_key=os.getenv('GOOGLE_AI_API_KEY')
        )
    def __new__(cls, *args, **kwargs):
        if cls._instance == None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_llm(self):
        return self.llm


# class ChatLLMEnum(Enum):
#     CHAT_GOOGLE_AI=1
#     CHAT_AI21=2


# class GenericChatLLM:
#     def __init__(self, llm_type:ChatLLMEnum) -> None:
#         self.llm_type = llm_type

#     def generic(self) -> BaseChatModel:
#         if self.llm_type == ChatLLMEnum.CHAT_GOOGLE_AI:
#             return self._chat_google_ai()
        
#         return self._chat_ai21()

#     def _chat_google_ai(self) -> ChatGoogleGenerativeAI:
#         google_llm = ChatGoogleGenerativeAI(
#             model="gemini-1.5-pro",
#             temperature=0,
#             google_api_key=os.getenv('GOOGLE_AI_API_KEY')
#         )
#         return google_llm
    
#     def _chat_ai21(self) -> ChatAI21:
#         ai21_llm = ChatAI21(
#             model="jamba-instruct",
#             api_key=os.getenv('AI21_API_KEY')
#         )
#         return ai21_llm