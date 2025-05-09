from openai import AzureOpenAI
import concurrent.futures

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
        self.open_aiclient = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
            api_version="2024-07-01-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
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
            "knn":500,
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

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_index = {
                executor.submit(
                    self.process_single_hit,
                    hit,
                    index,
                    i,
                    j,
                    self.location_for_description, # Pass the bound method
                    extract_location # Pass the function
                ): index
                for index, hit in enumerate(hits['hits']['hits'])
            }

        for future in concurrent.futures.as_completed(future_to_index):
            index = future_to_index[future]
            try:
                event = future.result() # Get the result (the EventModel object)
                if event is not None: # Only append if processing was successful
                    self.events.append(event)
            except Exception as exc:
                # This catches exceptions raised *within* the process_single_hit function
                print(f'Hit at index {index} generated an exception: {exc}')
                # You might want to log this or handle it differently

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

    def process_single_hit(self, hit_data, index, initial_i, initial_j, location_finder_method, location_extractor_func):
        current_i = initial_i + index * 0.0001
        current_j = initial_j + index * 1

        today = datetime.datetime.now()
        start_time = today + datetime.timedelta(days=current_j) # Use current_j

        try:
            # Perform the potentially slow operations
            addr = location_finder_method(hit_data["_source"]["article_body"])
            lat, long = location_extractor_func(addr)

            # Create the event model
            event = EventModel(
                name=hit_data["_source"]["article_body"][0:20],
                description=hit_data["_source"]["article_body"],
                start_time=start_time,
                end_time=None,
                category="news",
                # Use current_i for latitude/longitude offset
                latitude=lat or 48.667102 + current_i,
                longitude=long or 12.695920 - current_i
            )

            # Print is often tricky in parallel execution as output can be interleaved.
            # You might want to print after collecting results or use a thread-safe print.
            # For now, keeping the print as is for demonstration, but be aware.
            print(f"Processed index {index}: Name {event.name}, addr {addr}, lat {lat}, long {long}")

            return event # Return the created event
        except Exception as e:
            # Handle any exceptions that occur during processing a single hit
            print(f"Error processing hit at index {index}: {e}")
            return None # Return None or raise the exception, depending on desired behavior



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
