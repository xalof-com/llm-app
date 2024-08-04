import os, time
from datetime import datetime
from dotenv import load_dotenv, find_dotenv


from langchain_core.messages import AIMessage, HumanMessage
from ai.utils import get_rag_agent_executor, record_chat_message
from ai.helpers import print_console_ai_message

load_dotenv(find_dotenv())

os.environ['LLM_APP_ROOT_PATH'] = os.path.dirname(os.path.abspath(__file__))

def chat_console():
    agent_exec = get_rag_agent_executor(llm_name=os.getenv('CHAT_LLM_NAME'))
    chat_hist = []
    channel_name = "Console"
    
    is_record_message = eval(os.getenv('RECORD_MESSAGES', 'True'))

    while True:
        try:
            query = input("You: ")
            if query.lower() in ["exit", "quit"]:
                ai_message = "See you!"
                print(f"AI: {ai_message}")
                record_chat_message(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                channel_name=channel_name,
                                human_message=query,
                                bot_message=ai_message)    
                break
            
            response = agent_exec.invoke({"input": query, "chat_history": chat_hist})
            
            if is_record_message:
                record_chat_message(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    channel_name=channel_name,
                                    human_message=query,
                                    bot_message=response["output"])
                
            print_console_ai_message(response_chunks=response["output"])
            
            # Update history
            chat_hist.append(HumanMessage(content=query))
            chat_hist.append(AIMessage(content=response["output"]))
        
        except Exception as err:
            import traceback
            print(traceback.print_exc())
            break



if __name__ == '__main__':
    chat_console()
