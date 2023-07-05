import os.path
import logging
import urllib.request
from datetime import datetime

import bs4
from google.auth.transport import requests
from google.oauth2 import credentials as oauth_credentials
from google_auth_oauthlib import flow
from googleapiclient import discovery

date = "2023-07-14"
location = "carondeletpark"
KEYWORD = "Swim"
scopes = ["https://www.googleapis.com/auth/calendar"]
calendar_id = "dc19c79d0c85db398ce294cb1a66256de1828e905e7bea388279aa1c8289f2cc@group.calendar.google.com"
swimming_schedules_url = f"https://{location}reccomplex.virtuagym.com//classes/week/{date}?event_type=8&embedded=1&pref_club=37670"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def scrape_events(url, date):
    logger.info("Scraping the events from the given url ...")
    url_reader = urllib.request.urlopen(url)
    swimming_schedules_html = url_reader.read().decode("utf8")
    url_reader.close()

    soup = bs4.BeautifulSoup(swimming_schedules_html, features="html.parser")
    reversed_date = "-".join(date.split("-")[::-1])
    elements = soup.find_all(
        "div", attrs={"class": f"internal-event-day-{reversed_date}"}
    )

    events = []

    for element in elements:
        if KEYWORD in element.text:
            events.append(element.text.replace("\n", "").strip())

    logger.info(f"Scraped {len(events)} events at {date}!")

    return events


def format_events(events):
    formatted_events = []

    for event in events:
        event_parts = event.replace("     ", "$").split("$")
        start_time = datetime.strptime(
            event_parts[-1].split("-")[0].strip(), "%I:%M %p"
        )
        end_time = datetime.strptime(event_parts[-1].split("-")[1].strip(), "%I:%M %p")

        formatted_events.append(
            {
                "description": event_parts[0],
                "start_time": datetime.strftime(start_time, "%H:%M"),
                "end_time": datetime.strftime(end_time, "%H:%M"),
            }
        )

    logger.info("Formatted the events!")
    return formatted_events


def add_events(events):
    credentials = authenticate()
    logger.info("Adding the events ...")
    service = discovery.build("calendar", "v3", credentials=credentials)
    for event in events:
        add_event(event, service)


def add_event(event, service):
    body = {
        "summary": event["description"],
        "location": location,
        "start": {
            "dateTime": f"{date}T{event['start_time']}:00",
            "timeZone": "America/Chicago",
        },
        "end": {
            "dateTime": f"{date}T{event['end_time']}:00",
            "timeZone": "America/Chicago",
        },
    }

    event = service.events().insert(calendarId=calendar_id, body=body).execute()


def authenticate():
    logger.info("Authenticating ...")
    credentials = None
    if os.path.exists("token.json"):
        credentials = oauth_credentials.Credentials.from_authorized_user_file(
            "token.json", scopes
        )

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(requests.Request())
        else:
            credentials = flow.InstalledAppFlow.from_client_secrets_file(
                "credentials.json", scopes
            ).run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(credentials.to_json())

    return credentials


def main():
    events = scrape_events(swimming_schedules_url, date)
    events = format_events(events)
    add_events(events)
    logger.info("Events are succesefully added!")


if __name__ == "__main__":
    main()
