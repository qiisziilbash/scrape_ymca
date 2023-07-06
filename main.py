import utils

SWIM = "Swim"
YOGA = "Yoga"
CARONDELETPARK = "carondeletpark"
SOUTH_CITY = ""

SPORT_CODES = {
    SWIM: 8,
    YOGA: 2,
}

CALENDAR_IDS = {
    SWIM
    + CARONDELETPARK: "dc19c79d0c85db398ce294cb1a66256de1828e905e7bea388279aa1c8289f2cc@group.calendar.google.com",
    YOGA
    + CARONDELETPARK: "a1f976b36492615a4041fb7adb8a02a36354abd81dafac9436ab31f8eae8e87d@group.calendar.google.com",
}


date = "2023-07-06"
location = CARONDELETPARK
sport_type = YOGA
sport_code = SPORT_CODES[sport_type]


calendar_id = CALENDAR_IDS[sport_type + location]
schedules_url = f"https://{location}reccomplex.virtuagym.com//classes/week/{date}?event_type={sport_code}&embedded=1&pref_club=37670"


def main():
    events = utils.scrape_events(schedules_url, date, sport_type)
    events = utils.format_events(events)
    utils.add_events(events, date, calendar_id, location)


if __name__ == "__main__":
    main()
