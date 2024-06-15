import copy
import math
import random
from logging import ERROR, INFO, log

from zone1tube.algorithms.shortest_path import TrainNetwork
from zone1tube.data.stations import ExtStation


class SimulatedAnnealing(TrainNetwork):
    def __init__(self, stations: list[ExtStation], change_time: int = 7):
        super().__init__(stations=stations, change_time=change_time)

    def optimize(
        self,
        initial_state: list[int],
        initial_temp=1000,
        alpha=0.999,
        same_solution_limit=1500,
        same_cost_diff_limit=150000,
    ):
        """Peforms simulated annealing to find a solution"""

        current_temp = initial_temp

        # Start by initializing the current state with the initial state
        solution = initial_state
        solution_time, solution_route = self.shortest_path(solution)
        same_solution = 0
        same_cost_diff = 0

        while (
            same_solution < same_solution_limit
            and same_cost_diff < same_cost_diff_limit
        ):
            neighbor = get_neighbors(solution)

            # Check if neighbor is best so far
            try:
                neighbor_time, neighbor_route = self.shortest_path(neighbor)
                cost_diff = 1 / neighbor_time - 1 / solution_time
                # if the new solution is better, accept it
                if cost_diff > 0:
                    solution = neighbor
                    same_solution = 0
                    same_cost_diff = 0
                    solution_time = neighbor_time
                    solution_route = neighbor_route

                elif cost_diff == 0:
                    solution = neighbor
                    same_solution = 0
                    same_cost_diff += 1
                    solution_time = neighbor_time
                    solution_route = neighbor_route

                # if the new solution is not better, accept it with a probability of e^(-cost/temp)
                else:
                    if random.uniform(0, 1) <= math.exp(
                        float(cost_diff) / float(current_temp)
                    ):
                        solution = neighbor
                        solution_time = neighbor_time
                        solution_route = neighbor_route

                        same_solution = 0
                        same_cost_diff = 0
                    else:
                        same_solution += 1
                        same_cost_diff += 1
            except BaseException as e:
                log(level=ERROR, msg=e)
            # decrement the temperature
            current_temp = current_temp * alpha
            if same_solution == 0:
                log(level=INFO, msg=f"{solution_time}")

        return solution, solution_time, solution_route


def get_neighbors(state: list[int]):
    """Returns neighbor of  your solution."""

    neighbor = copy.deepcopy(state)

    func = random.choice([0, 1, 2, 3])
    if func == 0:
        inverse(neighbor)

    elif func == 1:
        insert(neighbor)

    elif func == 2:
        swap(neighbor)

    else:
        swap_routes(neighbor)

    return neighbor


def inverse(state: list[int]):
    "Inverses the order of cities in a route between node one and node two"

    node_one = random.choice(state[1:])
    new_list = list(
        filter(lambda city: city != node_one, state[1:])
    )  # route without the selected node one
    node_two = random.choice(new_list)
    state[min(node_one, node_two) : max(node_one, node_two)] = state[
        min(node_one, node_two) : max(node_one, node_two)
    ][::-1]

    return state


def insert(state: list[int]):
    "Insert city at node j before node i"
    node_j = random.choice(state[1:])
    state.remove(node_j)
    node_i = random.choice(state[1:])
    index = state.index(node_i)
    state.insert(index, node_j)

    return state


def swap(state: list[int]):
    "Swap cities at positions i and j with each other"

    pos_one = random.choice(range(1, len(state)))
    pos_two = random.choice(range(1, len(state)))
    state[pos_one], state[pos_two] = state[pos_two], state[pos_one]

    return state


def swap_routes(state: list[int]):
    "Select a subroute from a to b and insert it at another position in the route"
    subroute_a = random.choice(range(1, len(state)))
    subroute_b = random.choice(range(1, len(state)))
    subroute = state[min(subroute_a, subroute_b) : max(subroute_a, subroute_b)]
    del state[min(subroute_a, subroute_b) : max(subroute_a, subroute_b)]
    insert_pos = random.choice(range(1, len(state)))
    for i in subroute:
        state.insert(insert_pos, i)
    return state
