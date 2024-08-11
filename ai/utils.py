from langchain_core.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent
from ai.tools import get_current_time_tool, get_sjc_gold_price_tool, CurrentStockPriceTool, RAGQuestionAnswerTool, SQLQueryTool
from ai.llm import SingletonChatLLM
from ai.prompt_templates import react_tools_chat_prompt
import os, json, requests
import config


def get_rag_agent_executor(llm_name:str):
    chatllm = SingletonChatLLM(llm_name=llm_name)
    google_llm = chatllm.get_llm()

    tools = [
        Tool(
            name="current_time",
            func=get_current_time_tool,
            description="Useful for when you want to know the current time.",
        ),
        Tool(
            name="sjc_gold_price",
            func=get_sjc_gold_price_tool,
            description="Useful for when you want to know the current price of sjc gold."
            
        ),
        CurrentStockPriceTool(),
        RAGQuestionAnswerTool(
            name="rag_question_answer:ff8",
            db_name="chromadb_ff8",
            description="Hữu ích khi bạn muốn trả lời các câu hỏi liên quan đến game 'Final Fantasy 8'"
        ),    
        RAGQuestionAnswerTool(
            name="rag_question_answer:pntt",
            db_name="chromadb_pntt",
            description="Hữu ích khi bạn muốn trả lời các câu hỏi liên quan đến truyện 'PNTT'"
        ),
        RAGQuestionAnswerTool(
            name="rag_question_answer:bds-2023",
            db_name="chromadb_bds2023",
            description="Hữu ích khi bạn muốn trả lời các câu hỏi liên quan đến luật kinh doand bất động sản(BDS)"
        ),
        RAGQuestionAnswerTool(
            name="rag_question_answer:vinalink",
            db_name="vinalink",
            from_url=True,
            description="Hữu ích khi bạn muốn trả lời các câu hỏi liên quan đến các khóa học của vinalink: google ads, tiktok marketing, AI. trainer..."
        ),
        SQLQueryTool()
    ]

    tools.extend(_get_url_web_tool())

    react_prompt = react_tools_chat_prompt()

    agent = create_react_agent(llm=google_llm, tools=tools, prompt=react_prompt)

    agent_exec = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

    return agent_exec

def _get_url_web_tool():
    urls_file = f"{config.APP_ROOT_PATH}/data_src/WEB/urls.json"
    
    sources = None
    
    with open(urls_file, mode="r", encoding="utf-8") as f:
        sources = json.load(f)
        f.close()

    tools = []
    for src_name, value in sources.items():
        description = value['description']
        tool = RAGQuestionAnswerTool(
            name=f"rag_question_answer:{src_name}",
            db_name=src_name,
            from_url=True,
            description=description
        )
        tools.append(tool)
    return tools


def record_chat_message(chat_time:str,
                        channel_name:str="",
                        human_message:str="",
                        bot_message:str=""):

    deployment_id = os.getenv('GOOGLE_APP_SCRIPT_DEPLOYMENT_ID')
    url = f"https://script.google.com/macros/s/{deployment_id}/exec"

    payload = {
        "time": chat_time,
        "channel": channel_name,
        "human_message": human_message,
        "bot_message": bot_message
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1788.0'
    }
    response = requests.post(url, data=payload, headers=headers)

