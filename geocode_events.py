import json
import time
from geopy.geocoders import Nominatim


geolocator = Nominatim(user_agent="landau-event-mapper")


with open("events.json", "r", encoding="utf-8") as f:
    events = json.load(f)


def extract_location(address) -> tuple:
    if "Landau" not in address:
        address = f"{address}, Landau an der Isar, Germany"
    location = geolocator.geocode(address)
    if location:
        print(f"Updated: {address} → ({location.latitude}, {location.longitude})")
        return (location.latitude, location.longitude)
    else:
        print(f"Could not geocode: {address}")
        return (None, None)

for event in events:
    if "latitude" not in event or "longitude" not in event:
        try:
            address = f"{event['location']}, Landau an der Isar, Germany"
            lat, long = extract_location(address)
            event["latitude"] = lat
            event["longitude"] = long
            
            time.sleep(1)  # Respectful delay
        except Exception as e:
            print(f"Error geocoding {event['name']}: {e}")

with open("events.json", "w", encoding="utf-8") as f:
    json.dump(events, f, indent=2, ensure_ascii=False)

print("Geocoding complete. File updated.")
