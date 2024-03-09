import copy
from time import perf_counter as pc
import math
import numpy as np
import warnings
import random
import csv
import os


# Global variables
GOAL_STATE = [[]]
GLOBAL_STATE_DICT = {}
N = 0
nodes_explored = []
solution_found = 0
gn = 0

no_of_tiles = 8
# Reversing the initial state in a list starting from 8,7,6....0
initial_state = list(reversed(range(no_of_tiles + 1)))
g_state = [1, 1, [[1, 2, 3], [8, 0, 4], [7, 6, 5]]]
# Getting the square room of N in N-tile
matrix = int(math.sqrt(no_of_tiles + 1))
seed = 755

class IDAStar:
    # Constructor function
    def __init__(self, state, manhattan, zero_pos):
        self.state = state
        self.heuristic = manhattan
        self.zero_pos = zero_pos

    # Returns string representation of the state and manhattan distance
    def __str__(self):
        return f"state=\n{self.state}\nheuristic={int(self.heuristic)}"

    # equality method to compare the states with other states
    def __eq__(self, other):
        return np.array_equal(self.state, other.state)

    # Representation of __str__ on console
    def __repr__(self):
        return f"state=\n{self.state}\nheuristic={int(self.heuristic)}"

    # hash returns integer converted to bytes
    def __hash__(self):
        return hash(self.state.tobytes())


def custom_sort(node):
    return node.heuristic


def next_nodes(node):
    zero = node.zero_pos
    # Blank tile positions mapping
    row, col = map(int, zero)
    # Possible directions --> LEFT, RIGHT, DOWN, UP
    directions = ((row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1))
    state_nodes = []
    # Iterates over each possible direction
    for d in directions:
        # Checks if the move is valid within the puzzle grid
        if 0 <= d[0] < N and 0 <= d[1] < N:
            # Creates copy of the current puzzle board state so that original state is not affected
            tmp_state = np.copy(node.state)
            # Fetches the position of the goal so that the blank tile moves to that direction
            goal = GLOBAL_STATE_DICT[tmp_state[d]]
            # Swapping the tiles at blank tile Index with blank tile and tile Index with numbered tile
            tmp_state[d], tmp_state[zero] = tmp_state[zero], tmp_state[d]
            # Calculate h(n) based on manhattan distance b/w tiles and the goal
            direction_goal_distance = calculate_manhattan_distance(d, goal)
            goal_distance = calculate_manhattan_distance(goal, (row, col))
            state_nodes.append(IDAStar(tmp_state, node.heuristic - direction_goal_distance + goal_distance, d))
    # Returns a list of new nodes
    return sorted(state_nodes, key=custom_sort)


# Calculates the manhattan distance
def calculate_manhattan_distance(x, y):
    return abs(y[0] - x[0]) + abs(y[1] - x[1])


# Calculates h(n) heuristic cost
def calculate_manhattan_heuristic(state):
    distance = 0
    for x in range(N):
        for y in range(N):
            # Fetches the vertex number of current pos of the state passed as parameter
            number = state[x][y]
            # Checks if the vertex is not in a goal position and not the blank tile
            if number != GOAL_STATE[x][y] and number != 0:
                # Calculation of manhattan distance from cur. pos. and goal pos. and returns the total distance
                goal = GLOBAL_STATE_DICT[number]
                distance += calculate_manhattan_distance((x, y), goal)
    return distance


def search_goal(path, g_actual_score, threshold):
    global gn
    cur_node = list(path.keys())[-1]
    # Calculate the f_score by adding the actual + heuristic scores
    f_score = g_actual_score + cur_node.heuristic
    # If the depth i.e g(n) surpasses 30 then return False
    if g_actual_score > 30:
        gn = g_actual_score
        return False
    # If total est. cost exceeds given threshold then prune the cur. branch
    if f_score > threshold:
        return f_score
    # If the cur. state is goal state, return True
    if np.array_equal(cur_node.state, GOAL_STATE):
        return True
    # This initialised the minimum cost calculated for the search
    minimum = float('inf')
    # Recursively invoke search_goal() for every move to perform the same
    for node in next_nodes(cur_node):
        nodes_explored.append(node)
        if node not in path:
            path[node] = None
            tmp = search_goal(path, g_actual_score + 1, threshold)
            if tmp == True:
                return True
            if tmp < minimum:
                minimum = tmp
            path.popitem()
    # Finally returns the min. cost during search
    return minimum


def solve_attempt(initial_state):
    # Pos. of the blank tile
    zero = np.where(initial_state == 0)
    # Gets the state, heuristic value (h(n)) and the pos of blank tile
    initial_node = IDAStar(initial_state, calculate_manhattan_heuristic(initial_state), zero)
    # Initialises the threshold with heurisitic value of the state
    threshold = initial_node.heuristic
    # path dict. with initial node as the key
    path = {initial_node: None}
    while 1:
        # Searches for the goal state
        tmp = search_goal(path, 0, threshold)
        if tmp == True:
            # returns the states once the solution is found
            print(path.keys())
            return path.keys()
        elif tmp == float('inf'):
            # returns False if the goal is not found within max no. of moves / depth
            return False
        elif tmp == False:
            # returns False again if the limit is reached
            return False
        threshold = tmp


def random_states_generator(n):
    global initial_state
    global seed

    # Seed 755 as per my last 3 numbers of my student ID
    random.seed(seed)
    # Deep copy initial state
    state = copy.deepcopy(initial_state)
    deep_copy_state = state
    for _ in range(1, 11):
        final_list = []
        # Shuffling the initial state list 10 times in a loop
        random.shuffle(initial_state)
        for j in range(0, len(initial_state), n):
            final_list.append(initial_state[j:j + n])
            # Checks when the final shuffled list reaches the length of self.matrix i.e 3x3
            if len(final_list) == matrix:
                # yields or returns the the list one by one which is invoked by get_random_states() below
                yield final_list
            else:
                pass
        # Mechanism to reset the initial state to original figures at the end of every iteration
        """ This is because if not done, then the random.shuffle will shuffle the generated 
        random state instead of the original state """
        copy_state = copy.deepcopy(deep_copy_state)
        copied_state = copy_state
        initial_state = copied_state


def get_random_states():
    # Gets the final list from function above
    x = random_states_generator(matrix)
    state_counter = 1
    state_dict = {}
    for i in x:
        start_states_array = i
        # Stores the states in a form of a dictionary
        state_dict[state_counter] = start_states_array
        state_counter += 1
    return state_dict


# Clears the outfile first before running the code to solve puzzle
def clear_csv(file_name):
    fo = open(file_name, "w")
    fo.writelines("")
    fo.close()


def solve_puzzle(start_state=dict, goal_state=None, filename="IDASTAR_output.csv"):
    global GOAL_STATE
    global N
    global GLOBAL_STATE_DICT
    global g_state
    global nodes_explored
    global solution_found
    global seed

    # This condition is to solve only one puzzle passed in the argument in __main__
    if isinstance(start_state, list):
        GOAL_STATE = np.array(goal_state[2])
        goal_state_list = goal_state[2]
        print("GOAL STATE")
        print(GOAL_STATE)
        N = len(GOAL_STATE)
        GLOBAL_STATE_DICT = {goal_state_list[r][c]: (r, c) for r in range(N) for c in range(N)}
        # Creates the start state puzzle tile board
        puzzle = np.array(start_state[2])
        nodes_explored = []

        warnings.filterwarnings('ignore')
        print('Puzzle:\n', puzzle)
        t0 = pc()
        try:
            path = solve_attempt(puzzle)
            solution_found = 1
            # Starts the time to calculate total computation time
            t1 = pc()
            print(f'State Number 1 depth:{len(path)} runtime:{round(t1 - t0, 3)} s')
            print(f"Nodes Explored: {len(nodes_explored)}")
            print()
            # Writes the data as per assessment brief in csv file
            with open(filename, "a", newline='') as csvfile:
                # CSV headers
                fieldnames = ['Seed', 'Case Number', 'Case Start State', 'Solution Found', 'No. of moves',
                              'No. of Nodes opened', 'Computing Time']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                is_file_empty = os.stat(filename).st_size
                if is_file_empty == 0:
                    writer.writeheader()
                # Writes data
                writer.writerow({'Seed': seed, 'Case Number': 1, 'Case Start State': start_state[2],
                                 'Solution Found': solution_found, 'No. of moves': len(path),
                                 'No. of Nodes opened': len(nodes_explored),
                                 'Computing Time': str(round(t1 - t0, 3)) + 's'})
                csvfile.close()
        except TypeError:
            # If solution is not found within 30 moves / depth
            print(f"Unable to solve the puzzle for State Number 1 within 30 moves")
            solution_found = 0
            t1 = pc()
            print(f'Depth: Exceeded 30 moves runtime:{round(t1 - t0, 3)} s')
            print(f"Nodes Explored: {len(nodes_explored)}")
            print()
            with open(filename, "a", newline='') as csvfile:
                fieldnames = ['Seed', 'Case Number', 'Case Start State', 'Solution Found', 'No. of moves',
                              'No. of Nodes opened', 'Computing Time']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                is_file_empty = os.stat(filename).st_size
                if is_file_empty == 0:
                    writer.writeheader()
                writer.writerow({'Seed': seed, 'Case Number': 1, 'Case Start State': start_state[2],
                                 'Solution Found': solution_found, 'No. of moves': gn,
                                 'No. of Nodes opened': len(nodes_explored),
                                 'Computing Time': str(round(t1 - t0, 3)) + 's'})
                csvfile.close()
    else:
        GOAL_STATE = np.array(g_state[2])
        goal_state_list = g_state[2]
        print("GOAL STATE")
        print(GOAL_STATE)
        N = len(GOAL_STATE)
        GLOBAL_STATE_DICT = {goal_state_list[r][c]: (r, c) for r in range(N) for c in range(N)}
        # Runs as per assessment brief for 10 random states as per seed 755
        start_states = get_random_states()
        for k, v in start_states.items():
            final_state_list = []
            # Finds blank tile position
            blank_tile_index = np.where(np.array(v) == 0)
            row, column = blank_tile_index[0][0], blank_tile_index[1][0]
            final_state_list.append(row)
            final_state_list.append(column)
            # Creates a final start state list to show in CSV as per assessment brief
            final_state_list.append(v)
            # Creates the puzzle tile board
            puzzle = np.array(v)
            nodes_explored = []
            # Ignore warning to not show on console
            warnings.filterwarnings('ignore')
            print('Puzzle:\n', puzzle)
            # Start computation time
            t0 = pc()
            try:
                path = solve_attempt(puzzle)
                solution_found = 1
                # End computation time
                t1 = pc()
                print(f'State Number {k} depth:{len(path)} runtime:{round(t1 - t0, 3)} s')
                print(f"Nodes Explored: {len(nodes_explored)}")
                print()
                with open(filename, "a", newline='') as csvfile:
                    # CSV headers
                    fieldnames = ['Seed', 'Case Number', 'Case Start State', 'Solution Found', 'No. of moves',
                                  'No. of Nodes opened', 'Computing Time']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    is_file_empty = os.stat(filename).st_size
                    if is_file_empty == 0:
                        writer.writeheader()
                    # Writes data as per brief
                    writer.writerow({'Seed': seed, 'Case Number': k, 'Case Start State': final_state_list,
                                     'Solution Found': solution_found, 'No. of moves': len(path),
                                     'No. of Nodes opened': len(nodes_explored),
                                     'Computing Time': str(round(t1 - t0, 3))+'s'})
                    csvfile.close()
            except TypeError:
                # If solution is not found within 30 moves / depth
                print(f"Unable to solve the puzzle for State Number {k} within 30 moves")
                solution_found = 0
                t1 = pc()
                print(f'Depth: Exceeded 30 moves runtime:{round(t1 - t0, 3)} s')
                print(f"Nodes Explored: {len(nodes_explored)}")
                print()
                with open(filename, "a", newline='') as csvfile:
                    fieldnames = ['Seed', 'Case Number', 'Case Start State', 'Solution Found', 'No. of moves',
                                  'No. of Nodes opened', 'Computing Time']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    is_file_empty = os.stat(filename).st_size
                    if is_file_empty == 0:
                        writer.writeheader()
                    writer.writerow({'Seed': seed, 'Case Number': k, 'Case Start State': final_state_list,
                                     'Solution Found': solution_found, 'No. of moves': gn,
                                     'No. of Nodes opened': len(nodes_explored),
                                     'Computing Time': str(round(t1 - t0, 3))+'s'})
                    csvfile.close()


clear_csv("IDASTAR_output.csv")
# solve_puzzle(start_state=[2, 2, [[4, 7, 5], [3, 8, 1], [6, 2, 0]]],
#             goal_state=[1, 1, [[1, 2, 3], [8, 0, 4], [7, 6, 5]]])
solve_puzzle()
