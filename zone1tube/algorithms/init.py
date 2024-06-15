import copy
import sys
from logging import ERROR, log

from zone1tube.algorithms.shortest_path import TrainNetwork
from zone1tube.data.stations import ExtStation


class InitState(TrainNetwork):
    def __init__(self, stations: list[ExtStation], change_time: int = 7):
        super().__init__(stations=stations, change_time=change_time)

    def get(
        self,
        start_id: int,
        remaining_stations: list[ExtStation] | None = None,
        state: None | list[int] = None,
    ) -> list[int]:
        if state is None:
            state = [start_id]
        if remaining_stations is None:
            remaining_stations = [
                s for s in copy.deepcopy(self.stations) if s.id != start_id
            ]
            return self.get(
                start_id=start_id, remaining_stations=remaining_stations, state=state
            )
        if len(remaining_stations) == 0:
            return state

        remains = []
        for r in remaining_stations:
            try:
                remains.append((r.id, self.shortest_path([state[-1], r.id])[0]))
            except BaseException:
                continue

        if len(remains) == 0:
            log(level=ERROR, msg={"from": state[-1], "remaining": remaining_stations})
            sys.exit(0)

        id, _ = min(remains, key=lambda x: x[1])
        return self.get(
            start_id=start_id,
            remaining_stations=[r for r in remaining_stations if r.id != id],
            state=state + [id],
        )
