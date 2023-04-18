import os
import datetime
from typing import Optional
from pydantic import BaseModel
from tools.utils import load_config
from tools.utils import randomword
from ml.predict import predict_response
from fastapi.security import HTTPBearer
from fastapi import FastAPI, Depends, Response, status


class ChatMesg(BaseModel):
    chatID: str
    message: str

app = FastAPI()

token_auth_scheme = HTTPBearer()
load_config()


@app.get("/")
def read_root():
    return {"Hello":"Bot World"}


@app.post("/chat/")
async def chat_back(item: ChatMesg):
    response = predict_response(item.chatID, item.message)
    return { "chatID":item.chatID, "message":response }
