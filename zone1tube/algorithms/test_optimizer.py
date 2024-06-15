import random

from zone1tube.algorithms.optimizer import insert, inverse, swap, swap_routes

random.seed(10)


def test_mutations_preserve_first_element():
    init_state = [1, 2, 3, 4, 5, 6, 7]
    for func in [inverse, insert, swap, swap_routes]:
        for _ in range(10000):
            result = func(init_state)
            assert result[0] == 1
            assert len(result) == 7
