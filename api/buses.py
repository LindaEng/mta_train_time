from fastapi import FastAPI, HTTPException, Query, Request
from utils.haversine import find_nearest_station, haversine
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
async def get_buses(
    request: Request,
    stop: str | None = None,
    lat: float | None = Query(None),
    lon: float | None = Query(None),
):
    if not BUS_STOPS and stop is None and lat is None:
        return {"stop": None, "inbound": None, "outbound": None}

    if stop is not None:
        matches = [s for s in BUS_STOPS if s["id"] == stop]
        if not matches:
            raise HTTPException(status_code=404, detail=f"Stop {stop} not found")
        found = matches[0]
    elif lat is not None and lon is not None:
        found = find_nearest_station(lat, lon, BUS_STOPS)
        if found is None:
            return {"stop": None, "inbound": None, "outbound": None}
    else:
        forwarded = request.headers.get("x-forwarded-for", "")
        ip = forwarded.split(",")[0].strip() or (request.client.host if request.client else "127.0.0.1")
        lat2, lon2 = await geolocate_ip(ip)
        found = find_nearest_station(lat2, lon2, BUS_STOPS)
        if found is None:
            return {"stop": None, "inbound": None, "outbound": None}

    found_routes = set(found.get("routes", []))
    paired_ids = [
        s["id"] for s in BUS_STOPS
        if set(s.get("routes", [])).intersection(found_routes)
        and haversine(found["lat"], found["lon"], s["lat"], s["lon"]) <= 0.50
    ]
    departures = await fetch_bus_departures(paired_ids)

    return {
        "stop": found["name"],
        "inbound": departures["inbound"],
        "outbound": departures["outbound"],
    }
