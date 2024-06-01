from collections import defaultdict, namedtuple
from dataclasses import dataclass

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import csgraph_from_dense

from zone1tube.data.stations import ExtStation

Node = namedtuple("Node", ("station_id", "line_ref"))


@dataclass
class Graph:
    platform_lookup: dict[int, set[Node]]
    csr_m: csr_matrix
    node_lookup: dict[int, Node]
    node_inverse_lookup: dict[Node, int]


def generate_graph(stations: list[ExtStation], change_time: int) -> Graph:
    lines_in: dict[int, set[int]] = defaultdict(set)
    platform_lookup: dict[int, set[Node]] = defaultdict(set)
    nodes: set[Node] = set()
    for station in stations:
        for dest in station.destinations:
            lines_in[dest.station_id].add(dest.line_ref)
            lines_in[station.id].add(dest.line_ref)
            nodes.add(Node(station.id, dest.line_ref))
            nodes.add(Node(dest.station_id, dest.line_ref))
            platform_lookup[station.id].add(Node(station.id, dest.line_ref))

    node_lookup = dict(enumerate(nodes))
    node_inverse_lookup = {v: k for k, v in node_lookup.items()}

    node_count = len(node_lookup)
    adj_matrix = np.matrix(np.ones((node_count, node_count), dtype=np.int8) * np.inf)

    for station in stations:
        for line_ref in lines_in[station.id]:
            source_ref = Node(station.id, line_ref)
            i = node_inverse_lookup[source_ref]
            for dest in station.destinations:
                dest_ref = Node(dest.station_id, dest.line_ref)
                j = node_inverse_lookup[dest_ref]
                if line_ref == dest.line_ref:
                    adj_matrix[i, j] = dest.time
                elif dest.time == 0:
                    adj_matrix[i, j] = 0
                else:
                    adj_matrix[i, j] = dest.time + change_time
    csr_m = csgraph_from_dense(adj_matrix, null_value=np.inf)

    return Graph(
        platform_lookup=platform_lookup,
        csr_m=csr_m,
        node_lookup=node_lookup,
        node_inverse_lookup=node_inverse_lookup,
    )
