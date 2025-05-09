import json
from geopy.distance import geodesic

def load_events():
    with open("events.json", "r", encoding="utf-8") as f:
        return json.load(f)

def calculate_distance(user_coords, event_coords):
    print(geodesic(user_coords, event_coords))
    return geodesic(user_coords, event_coords).km

def find_nearby_events(user_lat, user_lon, max_distance_km=None):
    user_location = (user_lat, user_lon)
    events = load_events()
    nearby_events = []

    for event in events:
        if "latitude" in event and "longitude" in event:
            event_location = (event["latitude"], event["longitude"])
            distance_km = calculate_distance(user_location, event_location)

            return distance_km

            print(distance_km)
            event["distance_km"] = round(distance_km, 2)

            if max_distance_km is None or distance_km <= max_distance_km:
                nearby_events.append(event)

    nearby_events.sort(key=lambda x: x["distance_km"])
    return nearby_events

# Example use
if __name__ == "__main__":
    user_lat = 48.671
    user_lon = 12.696

    nearby = find_nearby_events(user_lat, user_lon, max_distance_km=10)

    print("\nNearby events within 10 km:")
    for event in nearby:
        print(f"- {event['name']} ({event['distance_km']} km)")