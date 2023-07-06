import logging
import os.path
import urllib.request
from datetime import datetime

import bs4
from google.auth.transport import requests
from google.oauth2 import credentials as oauth_credentials
from google_auth_oauthlib import flow
from googleapiclient import discovery

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


TIME_ZONE_OFFSET = "-05:00"

CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar"]


def scrape_events(url, date, sport_type):
    logger.info("Scraping the events from the given url ...")
    url_reader = urllib.request.urlopen(url)
    schedules_html = url_reader.read().decode("utf8")
    url_reader.close()

    soup = bs4.BeautifulSoup(schedules_html, features="html.parser")
    reversed_date = "-".join(date.split("-")[::-1])
    elements = soup.find_all(
        "div", attrs={"class": f"internal-event-day-{reversed_date}"}
    )

    events = []

    for element in elements:
        if sport_type in element.text:
            events.append(element.text.replace("\n", "").strip())

    logger.info(f"Scraped {len(events)} events at {date}!")

    return events


def format_events(events):
    formatted_events = []

    for event in events:
        event_parts = event.replace("     ", "$").split("$")
        event_parts = [event_part for event_part in event_parts if event_part]
        start_time = datetime.strptime(event_parts[1].split("-")[0].strip(), "%I:%M %p")
        end_time = datetime.strptime(event_parts[1].split("-")[1].strip(), "%I:%M %p")

        dict_event = {
            "summary": event_parts[0],
            "start_time": datetime.strftime(start_time, "%H:%M"),
            "end_time": datetime.strftime(end_time, "%H:%M"),
        }

        if len(event_parts) == 3:
            dict_event["instructor"] = event_parts[2].strip()

        formatted_events.append(dict_event)

    logger.info("Formatted the events!")
    return formatted_events


def is_date_populated(date, service, calendar_id):
    events_result = (
        service.events()
        .list(
            calendarId=calendar_id,
            timeMin=date + "T00:00:01" + TIME_ZONE_OFFSET,
            timeMax=date + "T23:59:59" + TIME_ZONE_OFFSET,
        )
        .execute()
    )
    events = events_result.get("items", [])

    return len(events) > 0


def add_events(events, date, calendar_id, location):
    credentials = authenticate()
    service = discovery.build("calendar", "v3", credentials=credentials)
    if is_date_populated(date, service, calendar_id):
        logger.warning(f"{date} is already populated!")
        return
    logger.info("Adding the events ...")
    for event in events:
        add_event(event, date, service, calendar_id, location)
    logger.info("Events are succesefully added!")


def add_event(event, date, service, calendar_id, location):
    body = {
        "summary": event["summary"],
        "location": location,
        "start": {
            "dateTime": f"{date}T{event['start_time']}:00{TIME_ZONE_OFFSET}",
        },
        "end": {
            "dateTime": f"{date}T{event['end_time']}:00{TIME_ZONE_OFFSET}",
        },
    }

    if "instructor" in event:
        body["description"] = f"Instructor: {event['instructor']}"

    service.events().insert(calendarId=calendar_id, body=body).execute()


def authenticate():
    logger.info("Authenticating ...")
    credentials = None
    if os.path.exists("token.json"):
        credentials = oauth_credentials.Credentials.from_authorized_user_file(
            "token.json", CALENDAR_SCOPES
        )

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(requests.Request())
        else:
            credentials = flow.InstalledAppFlow.from_client_secrets_file(
                "credentials.json", CALENDAR_SCOPES
            ).run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(credentials.to_json())

    return credentials
