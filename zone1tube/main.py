from logging import INFO, basicConfig, log
from typing import Annotated

import typer

from zone1tube.algorithms.graph import generate_graph
from zone1tube.data.stations import ExtStations
from zone1tube.logger import TyperLoggerHandler

typer_handler = TyperLoggerHandler()
basicConfig(level=INFO, handlers=(typer_handler,))


with open("./zone1.json", "r") as f:
    stations = ExtStations.validate_json(f.read())


def starting_stations_autocomplete(incomplete: str):
    return [s.name for s in stations if s.name.lower().startswith(incomplete.lower())]


app = typer.Typer()


@app.command()
def main(
    start: Annotated[
        str,
        typer.Option(
            help="Starting station, must be in Zone 1.",
            autocompletion=starting_stations_autocomplete,
        ),
    ],
    change_time: Annotated[
        int, typer.Option(help="Time to change between lines (mins)")
    ] = 7,
):
    log(level=INFO, msg=f"Loaded {len(stations)} stations.")
    log(level=INFO, msg=f"Starting station set as '{start}'.")
    generate_graph(stations, change_time)


if __name__ == "__main__":
    app()
