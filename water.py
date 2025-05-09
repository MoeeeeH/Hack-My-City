import requests
from dotenv import load_dotenv
import datetime
from model import EventModel
import glob
import csv

load_dotenv()

class WaterDataSource:


    def __init__(self) -> None:
        self.events = []

    def get_data(self):
        if len(self.events) == 0:
            self._request_data()
        return self.events



    def _request_data(self):
        files = glob.glob("./zst12/*data.csv")
        for file in files:
            events = self._parse_file(file)
            self.events.extend(events)

    def _parse_file(self, file) -> list[EventModel]:
        events = []
        lat, long = self._location_for_file(file)
        with open(file, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                date = row[0].split(";")[0].replace('\ufeff', '')

                date = datetime.datetime.strptime(date, "%Y-%m-%d")

                avg = row[1].split(";")[0]
                max = row[2].split(";")[0]
                min = row[3].split(";")[0]

                print(f"measure from {date} and location {lat},{long} is {avg} with max {max} and min {min}")
                event = EventModel(
                    name="Water Temperature",
                    description=f"Min: {min}, Max: {max}, Avg: {avg}, Date: {date}, Location: {lat},{long}",
                    start_time=date,
                    end_time=None,
                    category="infrastructure",
                    latitude=lat,
                    longitude=long,
                )
                events.append(event)
        return events

    def _location_for_file(self, file: str):
        if "landau" in file:
            return 48.675277, 12.692606
        elif "aham" in file:
            return 48.527419, 12.472331
        return 48.135124, 11.581981


waterDataSource = WaterDataSource()
waterDataSource.get_data()
