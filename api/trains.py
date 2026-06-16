from fastapi import FastAPI, Request
from utils.haversine import find_nearest_station
from utils.gtfs import fetch_departures
import json
import os
import httpx

app = FastAPI()

_stations_path = os.path.join(os.path.dirname(__file__), "../utils/stations.json")
with open(_stations_path) as f:
    STATIONS = json.load(f)

NYC_COORDS = (40.7128, -74.0060)


async def geolocate_ip(ip: str) -> tuple[float, float]:
    if ip in ("127.0.0.1", "::1", "localhost"):
        return NYC_COORDS
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"http://ip-api.com/json/{ip}", timeout=5.0)
            data = resp.json()
            if data.get("status") == "success":
                return data["lat"], data["lon"]
    except Exception:
        pass
    return NYC_COORDS


@app.get("/api/trains")
async def get_trains(request: Request):
    ip = request.client.host if request.client else "127.0.0.1"
    lat, lon = await geolocate_ip(ip)

    station = find_nearest_station(lat, lon, STATIONS)
    if station is None:
        return {"station": None, "uptown": None, "downtown": None}

    departures = await fetch_departures(station["id"], station["lines"])

    return {
        "station": station["name"],
        "uptown": departures["uptown"],
        "downtown": departures["downtown"],
        "north_label": station["north_label"],
        "south_label": station["south_label"],
    }
