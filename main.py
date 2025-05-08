from fastapi import FastAPI
import json

app = FastAPI()

with open("events.json", "r", encoding="utf-8") as f:
    events = json.load(f)

@app.get("/api/events")
def get_events():
    return events
