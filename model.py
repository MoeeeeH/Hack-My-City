from pydantic import BaseModel
import datetime

class EventModel(BaseModel):
    name: str
    description: str | None
    start_time: datetime.datetime
    end_time: datetime.datetime | None
    category: str
    latitude: float
    longitude: float

