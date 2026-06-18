import math

KAABA_LAT = 21.4225
KAABA_LON = 39.8262


def _to_rad(deg):
    return deg * math.pi / 180


def _to_deg(rad):
    return rad * 180 / math.pi


def calculate_qibla(lat, lon):
    lat1, lon1 = _to_rad(lat), _to_rad(lon)
    lat2, lon2 = _to_rad(KAABA_LAT), _to_rad(KAABA_LON)
    d_lon = lon2 - lon1

    y = math.sin(d_lon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(d_lon)
    bearing = (_to_deg(math.atan2(y, x)) + 360) % 360

    a = (
        math.sin((lat2 - lat1) / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    )
    distance_km = 6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return {
        "bearing": round(bearing, 1),
        "distance_km": round(distance_km, 0),
        "kaaba": {"lat": KAABA_LAT, "lon": KAABA_LON},
    }
