from logging import INFO, basicConfig, log
from typing import Annotated

import typer

from zone1tube.data.stations import Stations
from zone1tube.logger import TyperLoggerHandler

typer_handler = TyperLoggerHandler()
basicConfig(level=INFO, handlers=(typer_handler,))


def main(starting_station: Annotated[str, typer.Option(help="Starting station, must be in Zone 1.", prompt=True)]):
    with open("./data.json", "r") as f:
        stations = Stations.validate_json(f.read())
    log(level=INFO, msg=f"Loaded {len(stations)} stations.")

    # stations in zone 1
    zone1_stations = [s for s in stations if s.zone == 1.0]
    log(level=INFO, msg=f"Found {len(zone1_stations)} zone 1 stations.")
    if not any(s.name == starting_station for s in zone1_stations):
        raise ValueError("starting_station not in zone 1")
    log(level=INFO, msg=f"Starting station set as '{starting_station}'.")


if __name__ == "__main__":
    typer.run(main)
