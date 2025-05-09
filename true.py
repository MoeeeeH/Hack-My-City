from openai import AzureOpenAI
import time

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
        self.fetched = False
        self.open_aiclient = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
            api_version="2024-07-01-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )

    def get_data(self):
        if self.fetched:
            return self.events

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
            "knn":int(os.getenv("KNN")),
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

            try:
                addr = self.location_for_description(hit["_source"]["article_body"])
            except Exception as e:
                print(f"Error: {e}")
                continue

            global lat, long
            try:
                lat, long = extract_location(addr)
            except Exception as e:
                lat, long = None, None

            print(hit)
            event = EventModel(
                name=hit["_source"]["article_body"][0:20],
                description=f'url: {hit["_source"]["url"]} description: {hit["_source"]["article_body"]}',
                start_time=start_time,
                end_time=None,
                category="news",
                latitude=lat or 48.667102 + i,
                longitude=long or 12.695920 - i,
                user_distance=None
            )

            print(f"Name {event.name}, addr {addr}, lat {lat}, long {long}")

            i += 0.0001
            j += 1

            self.events.append(event)
            time.sleep(1)
        self.fetched = True

    def location_for_description(self, desc: str):
        completion = self.open_aiclient.chat.completions.create(
          model="gpt-4.1-mini",
          messages=[
                {"role": "user", "content": "search the streetname and the house number if possible, if there are more than one pick the one that's mentioned the most. Just give me name no formatting: " + desc},
          ]
        )
        return completion.choices[0].message.content


trueRelevanceDataSource = TrueRelevanceDataSource()
trueRelevanceDataSource._request_data()
