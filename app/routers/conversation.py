from fastapi import APIRouter, Body, Request
from fastapi.responses import StreamingResponse
from typing import Any, Optional, Annotated
import os
from dotenv import load_dotenv, find_dotenv

from langchain_core.messages import AIMessage, HumanMessage
from ai.utils import get_rag_agent_executor
from ai.helpers import send_stream_ai_message, get_fake_message


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
    
    agent_response = agent_exec.invoke({"input": query, "chat_history": chat_hist})
    print(f"AI: {agent_response['output']}")

    chat_hist.append(HumanMessage(content=query))
    chat_hist.append(AIMessage(content=agent_response["output"]))


    stream_headers = {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive"
        
    }
    response = StreamingResponse(send_stream_ai_message(response_chunks=agent_response["output"]),
                                 headers=stream_headers,
                                 media_type="text/event-stream")
    return response
    # return {"html": agent_response["output"]}