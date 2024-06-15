from collections import defaultdict, namedtuple
from dataclasses import dataclass

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import csgraph_from_dense, shortest_path

from zone1tube.data.stations import ExtStation

Node = namedtuple("Node", ("station_id", "line_ref"))


@dataclass
class Graph:
    platform_lookup: dict[int, set[Node]]
    csr_m: csr_matrix
    node_lookup: dict[int, Node]
    node_inverse_lookup: dict[Node, int]
    dists_matrix: np.ndarray
    predecessors: np.ndarray

    def platforms(self, id: int) -> list[Node]:
        return list(self.platform_lookup[id])

    def reconstruct_path(
        self, i: int | Node, j: int | Node, path=None
    ) -> list[Node] | None:
        if isinstance(i, Node):
            i = self.node_inverse_lookup[i]
        if isinstance(j, Node):
            j = self.node_inverse_lookup[j]
        if path is None:
            path = []
        previous = self.predecessors[i, j]
        if previous == i:
            return [self.node_lookup[n] for n in (path + [j, i])[::-1]]
        if previous == -9999:
            return None
        return self.reconstruct_path(i, previous, path=path + [j])


def generate_graph(stations: list[ExtStation], change_time: int) -> Graph:
    platform_lookup: dict[int, set[Node]] = defaultdict(set)
    nodes: set[Node] = set()
    destination_lookup: dict[int, set[int]] = defaultdict(set)
    time_lookup: dict[tuple[Node, Node], int] = {}

    for station in stations:
        for dest in station.destinations:
            nodes.add(Node(station.id, dest.line_ref))
            nodes.add(Node(dest.station_id, dest.line_ref))
            platform_lookup[station.id].add(Node(station.id, dest.line_ref))
            platform_lookup[dest.station_id].add(Node(dest.station_id, dest.line_ref))
            destination_lookup[station.id].add(dest.station_id)
            time_lookup[
                (Node(station.id, dest.line_ref), Node(dest.station_id, dest.line_ref))
            ] = dest.time
    for station in stations:
        for platform_a in platform_lookup[station.id]:
            for platform_b in platform_lookup[station.id]:
                if platform_a == platform_b:
                    time_lookup[(platform_a, platform_b)] = 0
                else:
                    time_lookup[(platform_a, platform_b)] = change_time

    node_lookup = dict(enumerate(nodes))
    node_inverse_lookup = {v: k for k, v in node_lookup.items()}

    node_count = len(node_lookup)
    adj_matrix = np.array(np.ones((node_count, node_count), dtype=np.int8) * np.inf)

    for from_node in nodes:
        i = node_inverse_lookup[from_node]
        for to_node in nodes:
            j = node_inverse_lookup[to_node]
            if (
                time := time_lookup.get((from_node, to_node)),
                None,
            ) and time is not None:
                adj_matrix[i, j] = time

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
