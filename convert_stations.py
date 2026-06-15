import csv
import json

stations = []

with open("stations.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        stations.append({
            "id": row["Station ID"],
            "name": row["Stop Name"],
            "lat": float(row["GTFS Latitude"]),
            "lon": float(row["GTFS Longitude"]),
            "lines": row["Daytime Routes"].split(),
            "north_label": row["North Direction Label"],
            "south_label": row["South Direction Label"],
        })

with open("utils/stations.json", "w") as f:
    json.dump(stations, f, indent=2)

print(f"Done — {len(stations)} stations written to utils/stations.json")