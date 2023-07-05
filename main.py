import datetime
import os.path

from google.auth.transport import requests
from google.oauth2 import credentials as oauth_credentials
from google_auth_oauthlib import flow
from googleapiclient import discovery
from googleapiclient.errors import HttpError

scopes = ["https://www.googleapis.com/auth/calendar"]
calendar_id = "dc19c79d0c85db398ce294cb1a66256de1828e905e7bea388279aa1c8289f2cc@group.calendar.google.com"


def scrape_events(url):
    events = []
    return events


def add_events(events):
    pass


def authenticate():
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


def test(credentials):
    try:
        service = discovery.build("calendar", "v3", credentials=credentials)

        event = {
            "summary": "test sum",
            "location": "test loc",
            "description": "test desc",
            "start": {
                "dateTime": "2023-07-05T09:00:00",
                "timeZone": "America/Chicago",
            },
            "end": {
                "dateTime": "2023-07-05T10:00:00",
                "timeZone": "America/Chicago",
            },
        }

        event = service.events().insert(calendarId=calendar_id, body=event).execute()

        print("Getting the upcoming 10 events ...")
        events = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=datetime.datetime.utcnow().isoformat() + "Z",
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        for event in events.get("items", []):
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])
        else:
            print("No upcoming events found.")
            return

    except HttpError as error:
        print("An error occurred: %s" % error)


def main():
    credentials = authenticate()
    test(credentials)


if __name__ == "__main__":
    main()
