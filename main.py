from fastapi import FastAPI
import json
from dotenv import load_dotenv
from true import TrueRelevanceDataSource

load_dotenv()

app = FastAPI()

trueRelevanceDataSource = TrueRelevanceDataSource()

with open("events.json", "r", encoding="utf-8") as f:
    events = json.load(f)

@app.get("/health")
def health():
    return "ok"

@app.get("/api/events")
def get_events():
    all_events = trueRelevanceDataSource.get_data()
    return all_events
