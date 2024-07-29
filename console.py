import os
from dotenv import load_dotenv, find_dotenv


from langchain_core.messages import AIMessage, HumanMessage
from ai.utils import get_rag_agent_executor

load_dotenv(find_dotenv())

os.environ['LLM_APP_ROOT_PATH'] = os.path.dirname(os.path.abspath(__file__))


agent_exec = get_rag_agent_executor()
chat_hist = []
while True:
    try:
        query = input("You: ")
        if query.lower() in ["exit", "quit"]:
            print("AI: See you!")
            break
        response = agent_exec.invoke({"input": query, "chat_history": chat_hist})
        
        print(f"AI: {response['output']}")

        # Update history
        chat_hist.append(HumanMessage(content=query))
        chat_hist.append(AIMessage(content=response["output"]))
    
    except Exception as err:
        import traceback
        print(traceback.print_exc())
        break


