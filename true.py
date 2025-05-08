from openai import OpenAI

import requests
import os
from dotenv import load_dotenv
import datetime
from geocode_events import extract_location
from model import EventModel

load_dotenv()

class TrueRelevanceDataSource:


    def __init__(self) -> None:
        self.client_id = os.getenv("CF_ACCESS_CLIENT_ID")
        self.client_secret = os.getenv("CF_ACCESS_SECRET_KEY")
        self.events: list[EventModel] = []
        self.open_aiclient = OpenAI(
          api_key=os.getenv("OPENAI_API_KEY"),
        )

    def get_data(self):
        if len(self.events) == 0:
            self._request_data()
        return self.events



    def _request_data(self):
        body = {
            "model_id":"S8Uj0pUBL7s0EZbEKqn3",
            "keyword_text":"Landau an der Isar",
            "keyword_weight":0.4,
            "embedding_text":"Landau an der Isar",
            "embedding_weight":0.4,
            "image_caption_text":"Landau an der Isar",
            "image_caption_weight":0.2,
            "knn":25,
            "sentiment":-10,
            "sentiment_operator":">",
            "time_filter_start":"2019-12-31T23:00:00.000Z",
            "time_filter_end":"2024-12-31T23:00:00.000Z"
        }

        url = 'https://true-relevance-targeting.com/api/ml/query/instant'

        # headers
        headers = {
            'CF-Access-Client-Id': self.client_id,
            'CF-Access-Client-Secret': self.client_secret
        }

        # make request'
        response = requests.post(url, headers=headers, json=body)
        hits = response.json()

        i = 0.0001
        j = 0

        for hit in hits['hits']['hits']:
            today = datetime.datetime.now()
            start_time = today + datetime.timedelta(days=j)

            addr = self.location_for_description(hit["_source"]["article_body"])
            lat, long = extract_location(addr)

            event = EventModel(
                name=hit["_source"]["article_body"][0:20],
                description=hit["_source"]["article_body"],
                start_time=start_time,
                end_time=None,
                category="news",
                latitude=lat or 48.667102 + i,
                longitude=long or 12.695920 - i
            )

            print(f"Name {event.name}, addr {addr}, lat {lat}, long {long}")

            i += 0.0001
            j += 1

            self.events.append(event)

    def location_for_description(self, desc: str):
        completion = self.open_aiclient.chat.completions.create(
          model="gpt-4.1-nano",
          messages=[
                {"role": "user", "content": "Suche die genauen Adressen aus dem folgenden Text? schreibe alle adressen mit Straße Hausnummer Ort und PLZ mit Kommma getrennt ohne weitere Formatierung. hier ist der text: " + desc},
          ]
        )
        return completion.choices[0].message.content


trueRelevanceDataSource = TrueRelevanceDataSource()
trueRelevanceDataSource._request_data()
