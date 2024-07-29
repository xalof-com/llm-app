from fastapi import APIRouter, Body, Request
from typing import Any, Optional, Annotated
import os
from dotenv import load_dotenv, find_dotenv

from langchain_core.messages import AIMessage, HumanMessage
from ai.utils import get_rag_agent_executor


load_dotenv(find_dotenv())

router = APIRouter(
    prefix="/ai"
)

agent_exec = get_rag_agent_executor()
chat_hist = []

@router.post("/conversation")
async def conversation(payload:Annotated[Any, Body()], request:Request) -> Any:
    # print(await request.json())
    # print(payload['messages'][0]['text'])
    query = payload['messages'][0]['text']
    
    response = agent_exec.invoke({"input": query, "chat_history": chat_hist})
    print(f"AI: {response['output']}")

    chat_hist.append(HumanMessage(content=query))
    chat_hist.append(AIMessage(content=response["output"]))

    return {"html": response['output']}