import json
import time
from geopy.geocoders import Nominatim


geolocator = Nominatim(user_agent="landau-event-mapper")


with open("events.json", "r", encoding="utf-8") as f:
    events = json.load(f)

for event in events:
    if "latitude" not in event or "longitude" not in event:
        try:
            address = f"{event['location']}, Landau an der Isar, Germany"
            location = geolocator.geocode(address)
            if location:
                event["latitude"] = location.latitude
                event["longitude"] = location.longitude
                print(f"Updated: {event['name']} → ({location.latitude}, {location.longitude})")
            else:
                print(f"Could not geocode: {address}")
            time.sleep(1)  # Respectful delay
        except Exception as e:
            print(f"Error geocoding {event['name']}: {e}")

with open("events.json", "w", encoding="utf-8") as f:
    json.dump(events, f, indent=2, ensure_ascii=False)

print("Geocoding complete. File updated.")