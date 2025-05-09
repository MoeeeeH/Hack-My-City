import requests
import time
import json
from datetime import datetime
from bs4 import BeautifulSoup
from model import EventModel
from geocode_events import extract_location
import re

def load_all_events():
    url = 'https://www.landau-isar.de/freizeit-tourismus/veranstaltungen/veranstaltungskalender/veranstaltungsliste'
    links = load_page(url)

    for i in range(2, 16):
        url = f'https://www.landau-isar.de/freizeit-tourismus/veranstaltungen/veranstaltungskalender/veranstaltungsliste/{i}'
        more_links = load_page(url)
        for link in more_links:
            links.append(link)

    events = []
    for link in links:
        try:
            url = f'https://www.landau-isar.de{link}'
            event = parse_article(url)
            if event is not None:
                events.append(event)
        except Exception as e:
            print(f"Error parsing {link}: {e}")


    copy = []
    for event in events:
        copy.append({
            "name": event.name,
            "description": event.description,
            "start_time": event.start_time.isoformat(),
            "end_time": event.end_time.isoformat() if event.end_time else None,
            "category": event.category,
            "latitude": event.latitude,
            "longitude": event.longitude
        })

    print(f"len of copy: {len(copy)}")

    with open("./events.json", 'w', encoding='utf-8') as f:
        json.dump(copy, f, ensure_ascii=False, indent=4)



def parse_article(link: str):
    # make get request
    response = requests.get(link)

    # parse
    soup = BeautifulSoup(response.content)

    # get the title
    title = soup.find("h1").text.strip()
    description = soup.find("div", class_="event_body").text.strip()
    try:
        location = soup.find("span", class_="detail-meta-date--location").text.strip()
        location = location.replace("\\", "").replace("\n", " ")
    except Exception:
        location = "Unknown"

    d = None
    try:
        date = soup.find("time", class_="detail-meta-date mr-2").text.strip()
        date = re.sub('[\s+]', '', date)
        date = re.sub('Uhr', '', date)
        date_time_part = date.split('–')[0]
        d = datetime.strptime(date_time_part, '%d.%m.%Y%H:%M')
    except Exception:
        pass


    # description = soup.find("div", class_="description").text.strip()
    if d is None:
        return None

    lat = 0.0
    lon = 0.0
    try:
        lat, lon = extract_location(location)
    except Exception as e:
        print(f"Error extracting location: {e} for {location}")
        lat, lon = None, None

    if lat is None or lon is None:
        return None

    if lat == 0.0 and lon == 0.0:
        return None

    # get the image
    print(f"link: {link}")
    print(f"lat: {lat}")
    print(f"lon: {lon}")

    event = EventModel(
        name=title,
        description=description,
        start_time=d,
        end_time=None,
        category="event",
        latitude=lat,
        longitude=lon
    )

    time.sleep(1)

    return event


def load_page(url: str) -> list:
    # make get request
    response = requests.get(url)

    # parse
    soup = BeautifulSoup(response.content)

    # get the list
    l = soup.find("section", class_="calendar calendar-list")

    if l is None:
        return


    # get all links in the list
    links = l.find_all("a")


    links = links[:-4]
    hrefs = []

    for link in links:
        href = link.get("href")
        if href is None:
            continue
        hrefs.append(href)

    return hrefs



load_all_events()
