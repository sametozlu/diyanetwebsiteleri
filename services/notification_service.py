from services.content_service import (
    get_daily_reminder,
    get_hourly_reminder,
    get_verse_of_day,
    get_hadith_of_day,
    get_esma_of_day,
    get_hijri_date,
)
from services.prayer_service import get_today_timings


def get_spiritual_bundle(city="Ankara", lang="tr"):
    daily = get_daily_reminder(lang)
    hourly = get_hourly_reminder(lang)
    verse = get_verse_of_day(lang)
    hadith = get_hadith_of_day(lang)
    esma = get_esma_of_day(lang)
    prayer = get_today_timings(city, lang)

    return {
        "lang": lang,
        "daily": daily,
        "hourly": hourly,
        "verse": verse,
        "hadith": hadith,
        "esma": esma,
        "hijri": get_hijri_date(lang) or daily.get("hijri", ""),
        "prayer": {
            "city": prayer.get("city"),
            "active": prayer.get("active"),
            "next": prayer.get("next"),
            "timings": prayer.get("timings"),
        },
    }
