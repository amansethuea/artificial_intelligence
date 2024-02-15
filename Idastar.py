from time import perf_counter as pc
import math
import numpy as np
import warnings
import random
import csv
import os


GOAL_STATE = [[]]
GLOBAL_STATE_DICT = {}
N = 0
nodes_explored = []

no_of_tiles = 8
initial_state = list(reversed(range(no_of_tiles + 1)))
goal_state = [1, 1, [[1, 2, 3], [8, 0, 4], [7, 6, 5]]]
matrix = int(math.sqrt(no_of_tiles + 1))


class IDAStar:
    def __init__(self, state, manhattan, zero_pos):
        self.state = state
        self.heuristic = manhattan
        self.zero_pos = zero_pos

    def __str__(self):
        return f"state=\n{self.state}\nheuristic={int(self.heuristic)}"

    def __eq__(self, other):
        return np.array_equal(self.state, other.state)

    def __repr__(self):
        return f"state=\n{self.state}\nheuristic={int(self.heuristic)}"

    def __hash__(self):
        return hash(self.state.tobytes())


def customSort(node):
    return node.heuristic


def nextnodes(node):
    zero = node.zero_pos

    r, c = map(int, zero)
    directions = ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1))
    nodes = []
    for direction in directions:
        if 0 <= direction[0] < N and 0 <= direction[1] < N:
            tmp = np.copy(node.state)
            goal = GLOBAL_STATE_DICT[tmp[direction]]

            tmp[direction], tmp[zero] = tmp[zero], tmp[direction]

            dir_goal_distance = manhattan_distance(direction, goal)
            goal_zero_distance = manhattan_distance(goal, (r, c))

            nodes.append(IDAStar(tmp, node.heuristic - dir_goal_distance + goal_zero_distance, direction))
    return sorted(nodes, key=customSort)


def manhattan_distance(a, b):
    return abs(b[0] - a[0]) + abs(b[1] - a[1])


def manhattan_heuristic(state):
    distance = 0
    for i in range(N):
        for j in range(N):
            num = state[i][j]
            if num != GOAL_STATE[i][j] and num != 0:
                goal = GLOBAL_STATE_DICT[num]
                distance += manhattan_distance((i, j), goal)
    return distance


def search(path, g, threshold):
    node = list(path.keys())[-1]

    f = g + node.heuristic

    if g > 30:
        return False

    if f > threshold:
        return f
    if np.array_equal(node.state, GOAL_STATE):
        return True

    minimum = float('inf')
    for n in nextnodes(node):
        nodes_explored.append(n)
        if n not in path:
            path[n] = None
            tmp = search(path, g + 1, threshold)
            if tmp == True:
                return True
            if tmp < minimum:
                minimum = tmp
            path.popitem()

    return minimum


def solve(initial_state):
    zero = np.where(initial_state == 0)
    initial_node = IDAStar(initial_state, manhattan_heuristic(initial_state), zero)
    threshold = initial_node.heuristic
    # The dictionary keeps insertion order since Python 3.7 so it can be used as a queue
    path = {initial_node: None}
    while 1:
        tmp = search(path, 0, threshold)
        if tmp == True:
            print("GOOD!")
            print(path.keys())
            return path.keys()
        elif tmp == float('inf'):
            print("WRONG!")
            return False
        elif tmp == False:
            print("WRONG")
            return False
        threshold = tmp


def random_states_generator(n):
    random.seed(755)
    for _ in range(1, 11):
        final_list = []
        random.shuffle(initial_state)
        for j in range(0, len(initial_state), n):
            final_list.append(initial_state[j:j + n])
            if len(final_list) == matrix:
                yield final_list
            else:
                pass


def get_random_states():
    x = random_states_generator(matrix)
    state_counter = 1
    state_dict = {}
    for i in x:
        start_states_array = i
        state_dict[state_counter] = start_states_array
        state_counter += 1
    return state_dict


def define_goal_state():
    global GOAL_STATE
    global N
    global GLOBAL_STATE_DICT
    global goal_state

    GOAL_STATE = np.array(goal_state[2])
    goal_state_list = goal_state[2]
    print("GOAL STATE")
    print(GOAL_STATE)
    N = len(GOAL_STATE)
    GLOBAL_STATE_DICT = {goal_state_list[r][c]: (r, c) for r in range(N) for c in range(N)}


def solve_puzzle(start_state=dict, goal_state=None, filename="IDASTAR_output.csv"):
    start_states = get_random_states()
    for k, v in start_states.items():
        puzzle = np.array(v)
        nodes_explored = []
        warnings.filterwarnings('ignore')
        define_goal_state()
        print('Puzzle:\n', puzzle)
        t0 = pc()
        try:
            path = solve(puzzle)
            t1 = pc()
            print(f'State Number {k} depth:{len(path)} runtime:{round(t1 - t0, 3)} s')
            print(f"Nodes Explored: {len(nodes_explored)}")
            print()
            with open(filename, "a", newline='') as csvfile:
                fieldnames = ['Case Number', 'Case Start State', 'Solution Found', 'No. of moves',
                              'No. of Nodes opened',
                              'Computing Time']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                is_file_empty = os.stat("").st_size
                if is_file_empty:
                    writer.writeheader()
                writer.writerow({'Case Number': "tbd", 'Case Start State': "tbd",
                                 'Solution Found': "tbd", 'No. of moves': "tbd",
                                 'No. of Nodes opened': "tbd", 'Computing Time': "tbd"})
                csvfile.close()
        except TypeError:
            print(f"Unable to solve the puzzle for State Number {k} within 30 moves")
            t1 = pc()
            print(f'Depth: Exceeded 30 moves runtime:{round(t1 - t0, 3)} s')
            print(f"Nodes Explored: {len(nodes_explored)}")
            print()
