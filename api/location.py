from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os

app = FastAPI()

GOOGLE_GEOLOCATION_URL = "https://www.googleapis.com/geolocation/v1/geolocate"


class WiFiAccessPoint(BaseModel):
    macAddress: str
    signalStrength: int


class LocationRequest(BaseModel):
    wifiAccessPoints: list[WiFiAccessPoint]


@app.post("/api/location")
async def get_location(body: LocationRequest):
    api_key = os.environ.get("GOOGLE_GEOLOCATION_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GOOGLE_GEOLOCATION_API_KEY not configured")

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                GOOGLE_GEOLOCATION_URL,
                params={"key": api_key},
                json=body.model_dump(),
                timeout=10.0,
            )
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=500, detail=f"Google Geolocation API error: {e.response.status_code}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to geolocate: {e}")

    location = data.get("location", {})
    lat = location.get("lat")
    lon = location.get("lng")

    if lat is None or lon is None:
        raise HTTPException(status_code=500, detail="Google Geolocation API returned no location")

    return {"lat": lat, "lon": lon}
