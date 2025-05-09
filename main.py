from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
from dotenv import load_dotenv
from true import TrueRelevanceDataSource
from water import WaterDataSource

load_dotenv()

app = FastAPI()

origins = [
    "http://localhost:3001",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

trueRelevanceDataSource = TrueRelevanceDataSource()
waterDataSource = WaterDataSource()

with open("events.json", "r", encoding="utf-8") as f:
    events = json.load(f)

@app.get("/health")
def health():
    return "ok"

@app.get("/api/events")
def get_events():
    all_events = trueRelevanceDataSource.get_data()

    water_events = waterDataSource.get_data()
    for e in water_events:
        all_events.append(e)

    for e in events:
        all_events.append(e)

    return all_events
