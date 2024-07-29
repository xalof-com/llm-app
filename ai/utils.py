from langchain_core.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent
from ai.tools import get_current_time_tool, get_sjc_gold_price_tool, CurrentStockPriceTool, RAGQuestionAnswerTool
from ai.llm import SingletonChatLLM
from ai.prompt_templates import react_tools_chat_prompt

def get_rag_agent_executor():
    chatllm = SingletonChatLLM()
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
            name="question_answering:ff8",
            db_name="chromadb_ff8",
            description="Hữu ích khi bạn muốn trả lời các câu hỏi liên quan đến game 'Final Fantasy 8'"
        ),    
        RAGQuestionAnswerTool(
            name="question_answering:pntt",
            db_name="chromadb_pntt",
            description="Hữu ích khi bạn muốn trả lời các câu hỏi liên quan đến truyện 'PNTT'"
        ),
        RAGQuestionAnswerTool(
            name="question_answering:bds-2023",
            db_name="chromadb_bds2023",
            description="Hữu ích khi bạn muốn trả lời các câu hỏi liên quan đến luật kinh doand bất động sản(BDS)"
        )  
    ]

    react_prompt = react_tools_chat_prompt()

    agent = create_react_agent(llm=google_llm, tools=tools, prompt=react_prompt)

    agent_exec = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

    return agent_exec