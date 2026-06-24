from fastapi import FastAPI, HTTPException, Query, Request, Header
from utils.haversine import find_nearest_station
from utils.gtfs import fetch_departures
import json
import os
import httpx

SECRET = os.enviorn.get("API_SECRET")

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
async def get_trains(
    request: Request,
    station: str | None = None,
    lat: float | None = Query(None),
    lon: float | None = Query(None),
    x_api_secret: str | None = Header(None)
):
    if SECRET and x_api_secret != SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if station is not None:
        matches = [s for s in STATIONS if s["id"] == station]
        if not matches:
            raise HTTPException(status_code=404, detail=f"Station {station} not found")
        found = matches[0]
    elif lat is not None and lon is not None:
        found = find_nearest_station(lat, lon, STATIONS)
        if found is None:
            return {"station": None, "uptown": None, "downtown": None}
    else:
        forwarded = request.headers.get("x-forwarded-for", "")
        ip = forwarded.split(",")[0].strip() or (request.client.host if request.client else "127.0.0.1")
        lat2, lon2 = await geolocate_ip(ip)
        found = find_nearest_station(lat2, lon2, STATIONS)
        if found is None:
            return {"station": None, "uptown": None, "downtown": None}

    departures = await fetch_departures(found["id"], found["lines"])

    return {
        "station": found["name"],
        "uptown": departures["uptown"],
        "downtown": departures["downtown"],
        "north_label": found["north_label"],
        "south_label": found["south_label"],
    }
