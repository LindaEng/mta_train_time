import os
import httpx
from google.transit import gtfs_realtime_pb2
from datetime import datetime

FEED_URLS = {
    "A": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace",
    "C": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace",
    "E": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace",
    "B": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm",
    "D": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm",
    "F": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm",
    "M": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm",
    "G": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g",
    "J": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-jz",
    "Z": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-jz",
    "N": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw",
    "Q": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw",
    "R": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw",
    "W": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw",
    "L": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l",
    "1": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
    "2": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
    "3": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
    "4": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
    "5": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
    "6": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
    "7": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
    "S": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
}


def get_feed_url_for_line(line: str) -> str | None:
    return FEED_URLS.get(line.upper())


async def fetch_departures(station_id: str, lines: list[str]) -> dict:
    """
    Given a station ID and list of lines serving it,
    fetch real-time departures and return next uptown/downtown times.
    """
    now = datetime.now().timestamp()

    # Deduplicate feed URLs so we don't hit the same feed twice
    feed_urls = list(set(
        url for line in lines
        if (url := get_feed_url_for_line(line))
    ))

    northbound = []
    southbound = []

    mta_key = os.environ.get("MTA_BUS_API_KEY", "")
    headers = {"x-api-key": mta_key} if mta_key else {}

    async with httpx.AsyncClient() as client:
        for url in feed_urls:
            try:
                response = await client.get(url, headers=headers, timeout=10.0)
                response.raise_for_status()

                feed = gtfs_realtime_pb2.FeedMessage()
                feed.ParseFromString(response.content)

                for entity in feed.entity:
                    if not entity.HasField("trip_update"):
                        continue

                    trip = entity.trip_update
                    route_id = trip.trip.route_id

                    for stop_time in trip.stop_time_update:
                        stop_id = stop_time.stop_id

                        # Match station — GTFS stop IDs have N/S suffix e.g. "127N", "127S"
                        if not stop_id.startswith(station_id):
                            continue

                        # Prefer arrival time, fall back to departure time
                        arrival = stop_time.arrival.time or stop_time.departure.time

                        # Skip if no valid time or train has already passed
                        if not arrival or arrival < now:
                            continue

                        minutes = round((arrival - now) / 60)
                        entry = {"line": route_id, "minutes": minutes}

                        if stop_id.endswith("N"):
                            northbound.append(entry)
                        elif stop_id.endswith("S"):
                            southbound.append(entry)

            except Exception as e:
                print(f"Error fetching feed {url}: {e}")
                continue

    northbound.sort(key=lambda x: x["minutes"])
    southbound.sort(key=lambda x: x["minutes"])

    return {
        "uptown": northbound[:3] if northbound else [],
        "downtown": southbound[:3] if southbound else [],
    }