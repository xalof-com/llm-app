import os
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from langchain_core.messages import AIMessage, HumanMessage
from ai.utils import get_rag_agent_executor, record_chat_message

load_dotenv(find_dotenv())
os.environ['LLM_APP_ROOT_PATH'] = os.path.dirname(os.path.abspath(__file__))

app = App(token=os.getenv('SLACK_BOT_TOKEN'),
          signing_secret=os.getenv('SLACK_SIGNING_SECRET'))

agent_exec = get_rag_agent_executor(llm_name=os.getenv('CHAT_LLM_NAME'))
chat_hist = []
channel_name = 'Slack'
is_record_message = eval(os.getenv('RECORD_MESSAGES', 'True'))

@app.message("")
def conversation(message, say):
    query = message['text']
    
    response = agent_exec.invoke({"input": query, "chat_history": chat_hist})
    print(f"AI: {response['output']}")
    
    if is_record_message:
        record_chat_message(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    channel_name=channel_name,
                                    human_message=query,
                                    bot_message=response["output"])

    chat_hist.append(HumanMessage(content=query))
    chat_hist.append(AIMessage(content=response["output"]))

    say(response["output"])


if __name__ == "__main__":
    try:
        SocketModeHandler(app, os.getenv('SLACK_APP_TOKEN')).start()
    except KeyboardInterrupt:
        print("\n.::.Slack Bolt terminated!")
        exit(0)