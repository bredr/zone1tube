from collections import defaultdict

import numpy as np
from scipy.sparse.csgraph import csgraph_from_dense, shortest_path

from zone1tube.algorithms.graph import Graph, Node, generate_graph
from zone1tube.data.stations import ExtStation


class TrainNetwork:
    def __init__(self, stations: list[ExtStation], change_time: int = 7):
        self.stations = stations
        self.graph = generate_graph(stations, change_time)

    def shortest_path(self, station_ids: list[int]) -> tuple[int, list[Node]]:
        stops = [(id, self.graph.platforms(id)) for id in station_ids]
        route = list(zip(stops[:-1], stops[1:], strict=True))
        shortest_steps = [
            x
            for x in (
                (i,)
                + min(
                    *(
                        (
                            j,
                            self.graph.dists_matrix[
                                self.graph.node_inverse_lookup[i],
                                self.graph.node_inverse_lookup[j],
                            ],
                        )
                        for j in to_stop[1]
                    ),
                    key=lambda y: y[1],
                )
                if len(to_stop[1]) > 1
                else (
                    i,
                    to_stop[1][0],
                    self.graph.dists_matrix[
                        self.graph.node_inverse_lookup[i],
                        self.graph.node_inverse_lookup[to_stop[1][0]],
                    ],
                )
                for from_stop, to_stop in route
                for i in from_stop[1]
                if len(to_stop[1]) > 0
            )
            if x[2] < np.inf
        ]
        intermediate_graph = build_intermediate_graph(shortest_steps)
        from_intermediates = [
            intermediate_graph.node_inverse_lookup[node]
            for node in stops[0][1]
            if node in intermediate_graph.node_inverse_lookup
        ]
        to_intermediates = [
            intermediate_graph.node_inverse_lookup[node]
            for node in stops[-1][1]
            if node in intermediate_graph.node_inverse_lookup
        ]
        i, j, time = min(
            (
                (i, j, intermediate_graph.dists_matrix[i, j])
                for i in from_intermediates
                for j in to_intermediates
            ),
            key=lambda x: x[2],
        )

        if time == np.inf:
            print("impossible!!!", stops[0][0], stops[-1][0])

        shortest_intermediate_stops = intermediate_graph.reconstruct_path(i, j)
        if shortest_intermediate_stops is None:
            return int(time), []
        return int(time), [
            n
            for a, b in zip(
                shortest_intermediate_stops[:-1],
                shortest_intermediate_stops[1:],
                strict=True,
            )
            if (path := self.graph.reconstruct_path(a, b)) and path is not None
            for n in path
        ]


def build_intermediate_graph(input: list[tuple[Node, Node, float]], change_time=7):
    node_lookup: dict[int, Node] = dict(
        enumerate({a for a, _, _ in input} | {b for _, b, _ in input})
    )
    node_inverse_lookup: dict[Node, int] = {v: k for k, v in node_lookup.items()}
    node_count = len(node_lookup)
    adj_matrix = np.array(np.ones((node_count, node_count), dtype=np.int8) * np.inf)
    for a, b, w in input:
        i = node_inverse_lookup[a]
        j = node_inverse_lookup[b]
        adj_matrix[i, j] = w

    platform_lookup: dict[int, set[Node]] = defaultdict(set)
    for node in node_lookup.values():
        platform_lookup[node.station_id].add(node)

    for i in range(node_count):
        adj_matrix[i, i] = 0

    for lines in platform_lookup.values():
        for a in lines:
            for b in lines:
                if a != b:
                    i = node_inverse_lookup[a]
                    j = node_inverse_lookup[b]
                    adj_matrix[i, j] = change_time
    csr_m = csgraph_from_dense(adj_matrix, null_value=np.inf)

    dists_matrix, predecessors = shortest_path(
        csr_m, directed=True, return_predecessors=True
    )
    return Graph(
        platform_lookup=platform_lookup,
        csr_m=csr_m,
        node_lookup=node_lookup,
        node_inverse_lookup=node_inverse_lookup,
        dists_matrix=dists_matrix,
        predecessors=predecessors,
    )
