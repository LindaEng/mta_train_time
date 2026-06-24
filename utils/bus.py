import os
import httpx
from datetime import datetime, timezone

BUS_API_URL = "https://bustime.mta.info/api/siri/stop-monitoring.json"


async def _fetch_single_stop(client: httpx.AsyncClient, stop_id: str, api_key: str, now: float) -> list[dict]:
    try:
        response = await client.get(
            BUS_API_URL,
            params={"key": api_key, "MonitoringRef": stop_id},
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching bus departures for {stop_id}: {e}")
        return []

    visits = (
        data.get("Siri", {})
        .get("ServiceDelivery", {})
        .get("StopMonitoringDelivery", [{}])[0]
        .get("MonitoredStopVisit", [])
    )

    entries = []
    for visit in visits:
        journey = visit.get("MonitoredVehicleJourney", {})
        route = journey.get("PublishedLineName", "")
        direction_ref = journey.get("DirectionRef", "")

        monitored_call = journey.get("MonitoredCall", {})
        arrival = (
            monitored_call.get("ExpectedArrivalTime")
            or monitored_call.get("AimedArrivalTime")
            or ""
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

        entries.append({"route": route, "minutes": minutes, "direction_ref": direction_ref})

    return entries


async def fetch_bus_departures(stop_ids: list[str]) -> dict:
    api_key = os.environ.get("MTA_BUS_API_KEY", "")
    if not api_key:
        return {"inbound": None, "outbound": None}

    now = datetime.now(timezone.utc).timestamp()

    all_entries = []
    async with httpx.AsyncClient() as client:
        for sid in stop_ids:
            all_entries.extend(await _fetch_single_stop(client, sid, api_key, now))

    inbound = []
    outbound = []

    for entry in all_entries:
        if entry["direction_ref"] == "0":
            inbound.append({"route": entry["route"], "minutes": entry["minutes"]})
        elif entry["direction_ref"] == "1":
            outbound.append({"route": entry["route"], "minutes": entry["minutes"]})

    inbound.sort(key=lambda x: x["minutes"])
    outbound.sort(key=lambda x: x["minutes"])

    return {
        "inbound": inbound[:3] if inbound else [],
        "outbound": outbound[:3] if outbound else [],
    }
