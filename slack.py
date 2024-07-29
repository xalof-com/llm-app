import os
from dotenv import load_dotenv, find_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from langchain_core.messages import AIMessage, HumanMessage
from ai.utils import get_rag_agent_executor

load_dotenv(find_dotenv())
os.environ['LLM_APP_ROOT_PATH'] = os.path.dirname(os.path.abspath(__file__))

app = App(token=os.getenv('SLACK_BOT_TOKEN'),
          signing_secret=os.getenv('SLACK_SIGNING_SECRET'))

agent_exec = get_rag_agent_executor()
chat_hist = []

@app.message("")
def conversation(message, say):
    query = message['text']
    
    response = agent_exec.invoke({"input": query, "chat_history": chat_hist})
    print(f"AI: {response['output']}")

    chat_hist.append(HumanMessage(content=query))
    chat_hist.append(AIMessage(content=response["output"]))

    say(response["output"])

if __name__ == "__main__":
    try:
        SocketModeHandler(app, os.getenv('SLACK_APP_TOKEN')).start()
    except KeyboardInterrupt:
        print("\n.::.Slack Bolt terminated!")
        exit(0)