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

with open("events.json", "r", encoding="utf-8") as f:
    events = json.load(f)

@app.get("/health")
def health():
    return "ok"

@app.get("/api/events")
def get_events(lat: Optional[float] = Query(None), lon: Optional[float] = Query(None)):
    all_events = trueRelevanceDataSource.get_data()
    events = load_events()


    water_events = waterDataSource.get_data()
    for e in water_events:
        all_events.append(e)

    for e in events:
        all_events.append(e)


    if lat is not None and lon is not None:
        print(f"User coordinates: {lat}, {lon}")
        user_coords = (lat, lon)
        for event in events:
            if "latitude" in event and "longitude" in event:
                event_coords = (event["latitude"], event["longitude"])
                event["user_distance"] = round(calculate_distance(user_coords, event_coords), 2)
                print(f"Distance to {event['name']}: {event['user_distance']} km")

    return all_events








