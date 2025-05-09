from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import json
from dotenv import load_dotenv
from water import WaterDataSource
from true import TrueRelevanceDataSource
from typing import Optional
from calculate_distance import load_events, calculate_distance, find_nearby_events

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

waterDataSource = WaterDataSource()
trueRelevanceDataSource = TrueRelevanceDataSource()


global event_cache
event_cache = None

with open("events.json", "r", encoding="utf-8") as f:
    events = json.load(f)

@app.get("/health")
def health():
    return "ok"

@app.get("/api/events")
def get_events(lat: Optional[float] = Query(None), lon: Optional[float] = Query(None)):

    if event_cache is not None and len(event_cache) > 0:
        return event_cache

    all_events = trueRelevanceDataSource.get_data()
    events = load_events()


    water_events = waterDataSource.get_data()
    for e in water_events:
        all_events.append(e)

    for e in events:
        all_events.append(e)


    if lat is not None and lon is not None:
        user_coords = (lat, lon)
        for event in all_events:
            if "latitude" in event and "longitude" in event:
                event_coords = (event["latitude"], event["longitude"])
                event["user_distance"] = round(calculate_distance(user_coords, event_coords), 2)


    event_cache = all_events
    return all_events








