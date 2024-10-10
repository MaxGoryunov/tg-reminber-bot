from fastapi import FastAPI
import datetime
from bot import bot

app = FastAPI()

@app.post('/notify')
async def notify():
  return {"one": "two"}