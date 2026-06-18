from datetime import datetime, timedelta

from services.content_service import get_hijri_date
from services.prayer_service import get_today_timings, _parse_time
from services.i18n import normalize_lang, format_remaining


def get_ramadan_status(city="Ankara", lang="tr"):
    lang = normalize_lang(lang)
    hijri = get_hijri_date(lang).lower()
    is_ramadan = "ramazan" in hijri or "ramadan" in hijri or "رمضان" in hijri

    prayer = get_today_timings(city, lang)
    timings = {item["key"]: item for item in prayer.get("timings", [])}
    now = datetime.now()

    def countdown_to(key):
        item = timings.get(key)
        if not item:
            return None
        target = _parse_time(item["time"])
        if target <= now:
            target = target + timedelta(days=1)
        diff = target - now
        secs = int(diff.total_seconds())
        hours, rem = divmod(secs, 3600)
        minutes, seconds = divmod(rem, 60)
        return {
            "label": item.get("label", key),
            "time": item.get("time"),
            "remaining": format_remaining(hours, minutes, lang),
            "seconds_until": secs,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
        }

    suhoor_cd = countdown_to("Fajr")
    iftar_cd = countdown_to("Maghrib")

    fasting_day = None
    if is_ramadan:
        try:
            fasting_day = int(hijri.split()[0])
        except (ValueError, IndexError):
            fasting_day = None

    return {
        "is_ramadan": is_ramadan,
        "hijri": get_hijri_date(lang),
        "city": city,
        "suhoor": suhoor_cd,
        "iftar": iftar_cd,
        "fasting_day": fasting_day,
        "next_event": "iftar" if iftar_cd and suhoor_cd and iftar_cd["seconds_until"] < suhoor_cd["seconds_until"] else "suhoor",
    }
