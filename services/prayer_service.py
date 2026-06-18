import requests
from datetime import datetime, timedelta
from config import PRAYER_METHOD

from services.i18n import get_prayer_labels, format_remaining

TIMEOUT = 8
HEADERS = {"User-Agent": "DiyanetWebPortal/1.0"}

KEYS = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]


def _fetch(city, endpoint_suffix=""):
    try:
        url = f"https://api.aladhan.com/v1/timingsByCity{endpoint_suffix}"
        params = {"city": city, "country": "Turkey", "method": PRAYER_METHOD}
        r = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def get_today_timings(city="Ankara", lang="tr"):
    labels = get_prayer_labels(lang)
    data = _fetch(city)
    if not data or "data" not in data:
        return _fallback_timings(lang)

    timings = data["data"]["timings"]
    date = data["data"]["date"]
    result = []
    for key in KEYS:
        time_val = timings.get(key, "00:00").split(" ")[0]
        result.append({"key": key, "label": labels[key], "time": time_val})

    hijri = date.get("hijri", {})
    gregorian = date.get("gregorian", {})

    return {
        "city": city,
        "timings": result,
        "hijri": f"{hijri.get('day')} {hijri.get('month', {}).get('en', '')} {hijri.get('year')}",
        "gregorian": f"{gregorian.get('day')} {gregorian.get('month', {}).get('en', '')} {gregorian.get('year')}",
        "active": _active_vakit(result),
        "next": _next_vakit(result, lang),
    }


def get_monthly_timings(city="Ankara"):
    now = datetime.now()
    try:
        url = "https://api.aladhan.com/v1/calendarByCity"
        params = {
            "city": city,
            "country": "Turkey",
            "method": PRAYER_METHOD,
            "month": now.month,
            "year": now.year,
        }
        r = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        days = []
        for day in data.get("data", []):
            t = day["timings"]
            g = day["date"]["gregorian"]
            days.append({
                "day": g["day"],
                "weekday": g["weekday"]["en"],
                "imsak": t["Fajr"].split(" ")[0],
                "gunes": t["Sunrise"].split(" ")[0],
                "ogle": t["Dhuhr"].split(" ")[0],
                "ikindi": t["Asr"].split(" ")[0],
                "aksam": t["Maghrib"].split(" ")[0],
                "yatsi": t["Isha"].split(" ")[0],
            })
        return {"city": city, "month": now.month, "year": now.year, "days": days}
    except Exception:
        return {"city": city, "month": now.month, "year": now.year, "days": []}


def _parse_time(t):
    h, m = map(int, t.split(":"))
    now = datetime.now()
    return now.replace(hour=h, minute=m, second=0, microsecond=0)


def _active_vakit(timings):
    now = datetime.now()
    active = "Fajr"
    for item in timings:
        if _parse_time(item["time"]) <= now:
            active = item["key"]
    return active


def _next_vakit(timings, lang="tr"):
    now = datetime.now()
    for item in timings:
        t = _parse_time(item["time"])
        if t > now:
            diff = t - now
            secs = int(diff.total_seconds())
            hours, rem = divmod(secs, 3600)
            minutes, seconds = divmod(rem, 60)
            return {
                "key": item["key"],
                "label": item["label"],
                "time": item["time"],
                "remaining": format_remaining(hours, minutes, lang),
                "seconds_until": secs,
                "hours": hours,
                "minutes": minutes,
                "seconds": seconds,
            }
    tomorrow = _parse_time(timings[0]["time"]) + timedelta(days=1)
    diff = tomorrow - now
    secs = int(diff.total_seconds())
    hours, rem = divmod(secs, 3600)
    minutes, seconds = divmod(rem, 60)
    return {
        "key": timings[0]["key"],
        "label": timings[0]["label"],
        "time": timings[0]["time"],
        "remaining": format_remaining(hours, minutes, lang),
        "seconds_until": secs,
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds,
    }


def _fallback_timings(lang="tr"):
    labels = get_prayer_labels(lang)
    fallback = [
        {"key": key, "label": labels[key], "time": time}
        for key, time in [
            ("Fajr", "04:45"), ("Sunrise", "06:15"), ("Dhuhr", "13:00"),
            ("Asr", "16:30"), ("Maghrib", "19:45"), ("Isha", "21:15"),
        ]
    ]
    return {
        "city": "Ankara",
        "timings": fallback,
        "hijri": "",
        "gregorian": datetime.now().strftime("%d %B %Y"),
        "active": _active_vakit(fallback),
        "next": _next_vakit(fallback, lang),
    }
