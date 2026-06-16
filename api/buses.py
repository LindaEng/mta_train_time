from fastapi import FastAPI, Request
from utils.haversine import find_nearest_station
from utils.bus import fetch_bus_departures
import json
import os
import httpx

app = FastAPI()

_bus_stops_path = os.path.join(os.path.dirname(__file__), "../utils/bus_stops.json")
BUS_STOPS = []
if os.path.exists(_bus_stops_path):
    with open(_bus_stops_path) as f:
        BUS_STOPS = json.load(f)

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


@app.get("/api/buses")
async def get_buses(request: Request):
    if not BUS_STOPS:
        return {"stop": None, "inbound": None, "outbound": None}

    ip = request.client.host if request.client else "127.0.0.1"
    lat, lon = await geolocate_ip(ip)

    stop = find_nearest_station(lat, lon, BUS_STOPS)
    if stop is None:
        return {"stop": None, "inbound": None, "outbound": None}

    departures = await fetch_bus_departures(stop["id"])

    return {
        "stop": stop["name"],
        "inbound": departures["inbound"],
        "outbound": departures["outbound"],
    }
