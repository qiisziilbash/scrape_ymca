import utils

# Fixed Params
SWIM = "Swim"
YOGA = "Yoga"
CLUB = "club"
CARONDELETPARK = "carondeletparkreccomplex"
SOUTHCITY = "southcity"

CODES = {
    SOUTHCITY: {
        CLUB: 37685,
        SWIM: 9,
        YOGA: 2,
    },
    CARONDELETPARK: {
        CLUB: 37670,
        SWIM: 8,
        YOGA: 2,
    }
}

CALENDAR_IDS = {
    SWIM
    + CARONDELETPARK: "dc19c79d0c85db398ce294cb1a66256de1828e905e7bea388279aa1c8289f2cc@group.calendar.google.com",
    YOGA
    + CARONDELETPARK: "a1f976b36492615a4041fb7adb8a02a36354abd81dafac9436ab31f8eae8e87d@group.calendar.google.com",
    SWIM
    + SOUTHCITY: "315ae8dee1fb053d8bf36c90a2e27d59af6a079f1396948c3e4b9d4dff82cc33@group.calendar.google.com",
    YOGA
    + SOUTHCITY: "c414bcceaacfc935de41125f0d45f48c16822442394a4e4a8749259cbd5b72f3@group.calendar.google.com",
}


# Given Params
date = "2023-07-08"
sport_type = YOGA
location = SOUTHCITY


sport_code = CODES[location][sport_type]
club_code  = CODES[location][CLUB]
calendar_id = CALENDAR_IDS[sport_type + location]
schedules_url = f"https://{location}.virtuagym.com//classes/week/{date}?event_type={sport_code}&embedded=1&pref_club={club_code}"


def main():
    events = utils.scrape_events(schedules_url, date, sport_type)
    events = utils.format_events(events)
    utils.add_events(events, date, calendar_id, location)


if __name__ == "__main__":
    main()
