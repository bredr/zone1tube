from logging import INFO, basicConfig, log

import typer

from zone1tube.data.stations import Stations
from zone1tube.logger import TyperLoggerHandler

typer_handler = TyperLoggerHandler()
basicConfig(level=INFO, handlers=(typer_handler,))


def main():
    with open("./data.json", "r") as f:
        stations = Stations.validate_json(f.read())
    log(level=INFO, msg=f"Loaded {len(stations)} stations.")


if __name__ == "__main__":
    typer.run(main)
