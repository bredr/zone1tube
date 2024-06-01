import json

from pydantic.json import pydantic_encoder

from zone1tube.data.stations import Station, Stations


def reduce_destinations(s: Station, zone1_stations: set[int]):
    s.destinations = [d for d in s.destinations if d.station_id in zone1_stations]
    return s


def main():
    with open("./data.json", "r") as f:
        stations = Stations.validate_json(f.read())
    zone1_stations = {s.id for s in stations if s.zone <= 1.5}
    zone1_only = [
        reduce_destinations(s, zone1_stations)
        for s in stations
        if s.id in zone1_stations
    ]
    with open("./zone1.json", "w") as f:
        json.dump(zone1_only, f, default=pydantic_encoder)


if __name__ == "__main__":
    main()
