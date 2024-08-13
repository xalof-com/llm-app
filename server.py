from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import conversation, token
import uvicorn
import os
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
# os.environ['LLM_APP_ROOT_PATH'] = os.path.dirname(os.path.abspath(__file__))

app = FastAPI()
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(token.router)
app.include_router(conversation.router)


def main():
    try:
        uvicorn.run(
            app=app, # app="server:app"
            reload=eval(os.getenv('UVICORN_RELOAD')),
            host=os.getenv('UVICORN_HOST'),
            port=int(os.getenv('UVICORN_PORT'))
        )
    except KeyboardInterrupt:
        print("\n.::.Service terminated!")
        exit(0)

if __name__ == "__main__":
    main()