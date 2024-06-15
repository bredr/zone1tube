import numpy as np
from scipy.sparse.csgraph import csgraph_to_dense

from zone1tube.algorithms.graph import Node
from zone1tube.algorithms.shortest_path import TrainNetwork
from zone1tube.data.stations import ExtStations

data_1 = [
    {
        "name": "Pimlico",
        "total_lines": 1,
        "id": 197,
        "longitude": -0.1334,
        "latitude": 51.4893,
        "rail": 0,
        "zone": 1.0,
        "destinations": [
            {
                "name": "Vauxhall",
                "line_colour": "00a0e2",
                "line_stripe": "",
                "time": 1,
                "longitude": -0.1253,
                "latitude": 51.4861,
                "station_id": 271,
                "line_name": "Victoria Line",
                "line_id": 11,
                "line_ref": 3,
            },
        ],
    },
    {
        "name": "Vauxhall",
        "total_lines": 1,
        "id": 271,
        "longitude": -0.1253,
        "latitude": 51.4861,
        "rail": 1,
        "zone": 1.5,
        "destinations": [
            {
                "name": "Pimlico",
                "line_colour": "00a0e2",
                "line_stripe": "",
                "time": 1,
                "longitude": -0.1334,
                "latitude": 51.4893,
                "station_id": 197,
                "line_name": "Victoria Line",
                "line_id": 11,
                "line_ref": 4,
            }
        ],
    },
]

data_2 = [
    {
        "name": "Chancery Lane",
        "total_lines": 1,
        "id": 48,
        "longitude": -0.1111,
        "latitude": 51.5185,
        "rail": 0,
        "zone": 1.0,
        "destinations": [
            {
                "name": "Holborn",
                "line_colour": "dc241f",
                "line_stripe": "",
                "time": 1,
                "longitude": -0.12,
                "latitude": 51.5174,
                "station_id": 126,
                "line_name": "Central Line",
                "line_id": 2,
                "line_ref": 2,
            },
        ],
    },
    {
        "name": "Holborn",
        "total_lines": 2,
        "id": 126,
        "longitude": -0.12,
        "latitude": 51.5174,
        "rail": 0,
        "zone": 1.0,
        "destinations": [
            {
                "name": "Chancery Lane",
                "line_colour": "dc241f",
                "line_stripe": "",
                "time": 1,
                "longitude": -0.1111,
                "latitude": 51.5185,
                "station_id": 48,
                "line_name": "Central Line",
                "line_id": 2,
                "line_ref": 1,
            },
            {
                "name": "Covent Garden",
                "line_colour": "0019a8",
                "line_stripe": "",
                "time": 1,
                "longitude": -0.1243,
                "latitude": 51.5129,
                "station_id": 60,
                "line_name": "Piccadilly Line",
                "line_id": 10,
                "line_ref": 8,
            },
        ],
    },
    {
        "name": "Covent Garden",
        "total_lines": 1,
        "id": 60,
        "longitude": -0.1243,
        "latitude": 51.5129,
        "rail": 0,
        "zone": 1.0,
        "destinations": [
            {
                "name": "Holborn",
                "line_colour": "0019a8",
                "line_stripe": "",
                "time": 1,
                "longitude": -0.12,
                "latitude": 51.5174,
                "station_id": 126,
                "line_name": "Piccadilly Line",
                "line_id": 10,
                "line_ref": 7,
            },
        ],
    },
]

stations_1 = ExtStations.validate_python(data_1)
stations_2 = ExtStations.validate_python(data_2)


def test_graph_data_1():
    network = TrainNetwork(stations_1, 7)
    assert network.graph.platforms(197) == [
        Node(station_id=197, line_ref=3),
        Node(station_id=197, line_ref=4),
    ]
    assert network.graph.platforms(271) == [
        Node(station_id=271, line_ref=3),
        Node(station_id=271, line_ref=4),
    ]
    assert np.array_equal(
        csgraph_to_dense(network.graph.csr_m, null_value=np.Inf),
        np.array(
            [
                [0, 7, np.Inf, np.Inf],
                [7, 0, np.Inf, 1],
                [1, np.Inf, 0, 7],
                [np.Inf, np.Inf, 7, 0],
            ],
            dtype=np.float64,
        ),
    )


def test_graph_data_2():
    network = TrainNetwork(stations_2, 7)
    assert network.graph.platforms(60) == [
        Node(station_id=60, line_ref=7),
        Node(station_id=60, line_ref=8),
    ]
    assert network.graph.platforms(126) == [
        Node(station_id=126, line_ref=1),
        Node(station_id=126, line_ref=2),
        Node(station_id=126, line_ref=8),
        Node(station_id=126, line_ref=7),
    ]

    assert network.graph.platforms(48) == [
        Node(station_id=48, line_ref=1),
        Node(station_id=48, line_ref=2),
    ]
    assert np.array_equal(
        csgraph_to_dense(network.graph.csr_m, null_value=np.Inf),
        np.array(
            [
                [0, np.Inf, np.Inf, np.Inf, np.Inf, 7, np.Inf, np.Inf],
                [np.Inf, 0, 7, np.Inf, 7, np.Inf, 7, np.Inf],
                [1, 7, 0, np.Inf, 7, np.Inf, 7, np.Inf],
                [np.Inf, np.Inf, np.Inf, 0, np.Inf, np.Inf, np.Inf, 7],
                [np.Inf, 7, 7, 1, 0, np.Inf, 7, np.Inf],
                [7, np.Inf, np.Inf, np.Inf, np.Inf, 0, 1, np.Inf],
                [np.Inf, 7, 7, np.Inf, 7, np.Inf, 0, np.Inf],
                [np.Inf, 1, np.Inf, 7, np.Inf, np.Inf, np.Inf, 0],
            ],
            dtype=np.float64,
        ),
    )


def test_shortest_path_1():
    network = TrainNetwork(stations_1, 7)
    time, path = network.shortest_path([197, 271])
    assert time == 1
    assert path == [Node(197, 3), Node(271, 3)]


def test_shortest_path_2():
    network = TrainNetwork(stations_2, 7)
    time, path = network.shortest_path([48, 60])
    assert time == 9
    assert path == [Node(48, 2), Node(126, 2), Node(126, 8), Node(60, 8)]
