import math

EARTH_RADIUS_KM = 6371


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    )
    return EARTH_RADIUS_KM * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def find_nearest_station(
    user_lat: float, user_lon: float, stations: list[dict]
) -> dict | None:
    if not stations:
        return None
    return min(
        stations,
        key=lambda s: haversine(user_lat, user_lon, s["lat"], s["lon"]),
    )
