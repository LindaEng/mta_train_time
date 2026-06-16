import os
import httpx
from datetime import datetime, timezone

BUS_API_URL = "https://bustime.mta.info/api/siri/stop-monitoring.json"


async def fetch_bus_departures(stop_id: str) -> dict:
    api_key = os.environ.get("MTA_BUS_API_KEY", "")
    if not api_key:
        return {"inbound": None, "outbound": None}

    now = datetime.now(timezone.utc).timestamp()

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                BUS_API_URL,
                params={
                    "key": api_key,
                    "MonitoringRef": stop_id,
                },
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"Error fetching bus departures: {e}")
            return {"inbound": None, "outbound": None}

    visits = (
        data.get("Siri", {})
        .get("ServiceDelivery", {})
        .get("StopMonitoringDelivery", [{}])[0]
        .get("MonitoredStopVisit", [])
    )

    inbound = []
    outbound = []

    for visit in visits:
        journey = visit.get("MonitoredVehicleJourney", {})
        route = journey.get("PublishedLineName", "")
        direction_ref = journey.get("DirectionRef", "")

        arrival = (
            journey.get("MonitoredCall", {})
            .get("ExpectedArrivalTime", "")
        )
        if not arrival:
            continue

        try:
            arrival_dt = datetime.fromisoformat(arrival.replace("Z", "+00:00"))
            minutes = round((arrival_dt.timestamp() - now) / 60)
        except (ValueError, TypeError):
            continue

        if minutes < 0:
            continue

        entry = {"route": route, "minutes": minutes}

        if direction_ref == "0":
            inbound.append(entry)
        elif direction_ref == "1":
            outbound.append(entry)

    inbound.sort(key=lambda x: x["minutes"])
    outbound.sort(key=lambda x: x["minutes"])

    return {
        "inbound": inbound[0] if inbound else None,
        "outbound": outbound[0] if outbound else None,
    }
