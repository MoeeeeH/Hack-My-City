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
            reader = csv.reader(f, delimiter=";")
            for row in reader:
                date = row[0].replace('\ufeff', '')

                date = datetime.datetime.strptime(date, "%Y-%m-%d")
                if date.year < 2000:
                    continue


                if "height" in file:
                    avg = row[1]
                    max = row[2]
                    min = row[3]
                    event = EventModel(
                        name="Water Height",
                        description=f"Min: {min}, Max: {max}, Avg: {avg}, Date: {date}, Location: {lat},{long}",
                        start_time=date,
                        end_time=None,
                        category="infrastructure",
                        latitude=lat,
                        longitude=long,
                        user_distance=None
                    )
                    events.append(event)

                else:
                    avg = row[1]
                    max = row[2]
                    min = row[3]
                    print(f"measure from {date} and location {lat},{long} is {avg} with max {max} and min {min}")
                    event = EventModel(
                        name="Water Temperature",
                        description=f"Min: {min}, Max: {max}, Avg: {avg}, Date: {date}, Location: {lat},{long}, File: {file}",
                        start_time=date,
                        end_time=None,
                        category="infrastructure",
                        latitude=lat,
                        longitude=long,
                        user_distance=None
                    )
                    events.append(event)
        return events

    def _location_for_file(self, file: str):
        if "landau" in file:
            if "height" in file:
                return 48.675377, 12.692706
            return 48.675277, 12.692606
        elif "aham" in file:
            if "height" in file:
                return 48.527519, 12.472431
            return 48.527419, 12.472331
        elif "rottersdorf" in file:
            if "height" in file:
                return 48.606423, 12.694047
            return 48.606323, 12.693947
        return 48.135124, 11.581981


waterDataSource = WaterDataSource()
waterDataSource.get_data()
