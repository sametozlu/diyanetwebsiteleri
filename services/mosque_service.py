import json
import math
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def _load_mosques():
    path = os.path.join(DATA_DIR, "mosques.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _distance_km(lat1, lon1, lat2, lon2):
    r = 6371
    p = math.pi / 180
    a = (
        0.5
        - math.cos((lat2 - lat1) * p) / 2
        + math.cos(lat1 * p) * math.cos(lat2 * p) * (1 - math.cos((lon2 - lon1) * p)) / 2
    )
    return 2 * r * math.asin(math.sqrt(a))


def get_mosques(city=None, lat=None, lon=None, limit=20):
    mosques = _load_mosques()
    if city:
        city_lower = city.lower()
        mosques = [m for m in mosques if m.get("city", "").lower() == city_lower or city_lower in m.get("city", "").lower()]

    if lat is not None and lon is not None:
        for m in mosques:
            m["distance_km"] = round(_distance_km(float(lat), float(lon), m["lat"], m["lon"]), 1)
        mosques.sort(key=lambda x: x.get("distance_km", 9999))

    return mosques[:limit]


def get_diyanet_centers():
    return [m for m in _load_mosques() if m.get("type") == "diyanet_center"]
