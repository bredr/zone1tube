from logging import INFO, basicConfig, log
from typing import Annotated

import typer

from zone1tube.algorithms.init import InitState
from zone1tube.algorithms.optimizer import SimulatedAnnealing
from zone1tube.data.stations import ExtStations
from zone1tube.logger import TyperLoggerHandler

typer_handler = TyperLoggerHandler()
basicConfig(level=INFO, handlers=(typer_handler,))


with open("./zone1.json", "r") as f:
    stations = ExtStations.validate_json(f.read())


def starting_stations_autocomplete(incomplete: str):
    return [s.name for s in stations if s.name.lower().startswith(incomplete.lower())]


app = typer.Typer(pretty_exceptions_enable=False)


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
    optimizer = SimulatedAnnealing(stations, change_time)
    start_id = next(s.id for s in stations if s.name == start)
    name_lookup = {s.id: s.name for s in stations}

    init_generator = InitState(stations, change_time)

    init_state = init_generator.get(start_id)
    log(
        level=INFO,
        msg="Starting state:" + " -> ".join(name_lookup[s] for s in init_state),
    )

    solution, time, route = optimizer.optimize(init_state)
    log(level=INFO, msg=f"Solution found of {time} mins")

    log(level=INFO, msg=" -> ".join(name_lookup[s] for s in solution))


if __name__ == "__main__":
    app()
