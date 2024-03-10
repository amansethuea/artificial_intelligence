import copy
import math
import os
import random
import time
import csv
import numpy as np


class Iddfs(object):
    # Constructor function to define some class level variables
    def __init__(self):
        self.no_of_tiles = 8
        # Reversing the initial state in a list starting from 8,7,6....0
        self.initial_state = list(reversed(range(self.no_of_tiles + 1)))
        self.goal_state = [1, 1, [[1, 2, 3], [8, 0, 4], [7, 6, 5]]]
        self.states = []
        # Getting the square room of N in N-tile
        self.matrix = int(math.sqrt(self.no_of_tiles + 1))
        self.UP = 'up'
        self.DOWN = 'down'
        self.LEFT = 'left'
        self.RIGHT = 'right'
        self.nodes_explored = []
        self.solution_found = 0
        self.seed = 755

    def random_states_generator(self, n):
        # Seed 755 as per my last 3 numbers of my student ID
        random.seed(self.seed)
        # Deep copy initial state
        state = copy.deepcopy(self.initial_state)
        deep_copy_state = state
        for _ in range(1, 11):
            final_list = []
            # Shuffling the initial state list 10 times in a loop
            random.shuffle(self.initial_state)
            for j in range(0, len(self.initial_state), n):
                final_list.append(self.initial_state[j:j + n])
                # Checks when the final shuffled list reaches the length of self.matrix i.e 3x3
                if len(final_list) == self.matrix:
                    # yields or returns the the list one by one which is invoked by get_random_states() below
                    yield final_list
                else:
                    pass
            # Mechanism to reset the initial state to original figures at the end of every iteration
            """ This is because if not done, then the random.shuffle will shuffle the generated 
                random state instead of the original state """
            copy_state = copy.deepcopy(deep_copy_state)
            copied_state = copy_state
            self.initial_state = copied_state

    def get_random_states(self):
        # Gets the final list from function above
        x = self.random_states_generator(self.matrix)
        state_counter = 1
        state_dict = {}
        for i in x:
            start_states_array = i
            # Stores the states in a form of a dictionary
            state_dict[state_counter] = start_states_array
            state_counter += 1
        return state_dict

    def locate_blank_tile_pos(self, tile_board):
        # Return cordinates of the blank tile location in matrix
        for x in range(self.matrix):
            for y in range(self.matrix):
                # Checks where row and column in matrix is 0 , then returns the x, y cordinates as a list
                if tile_board[y * self.matrix + x] == 0:
                    return [x, y]

    # Display the tile board on console for better viewing and tracking
    def display_tile_board(self, board):
        for y in range(self.matrix):
            for x in range(self.matrix):
                # Find's blank tile position and displays the matrix / tile board
                if board[y * self.matrix + x] == 0:
                    print('_ ', end='')
                else:
                    # Displays the rest of the numbers on tile board by right aligning them during display
                    print(str(board[y * self.matrix + x]).rjust(2) + ' ', end='')
            print()

    def make_move_on_board(self, tile_board, tile_move):
        # Modify tile board as per move of the blank tile
        blank_x, blank_y = self.locate_blank_tile_pos(tile_board)
        blank_tile_position = blank_y * self.matrix + blank_x
        tile_pos = 0
        if tile_move == self.UP:
            # Positioning the tile position to up
            tile_pos = (blank_y + 1) * self.matrix + blank_x
        elif tile_move == self.LEFT:
            # Positioning the tile position to left
            tile_pos = blank_y * self.matrix + (blank_x + 1)
        elif tile_move == self.DOWN:
            # Positioning the tile position to down
            tile_pos = (blank_y - 1) * self.matrix + blank_x
        elif tile_move == self.RIGHT:
            # Positioning the tile position to right
            tile_pos = blank_y * self.matrix + (blank_x - 1)

        # Swapping the tiles at blank tile Index with blank tile and tile Index with numbered tile:
        tile_board[blank_tile_position], tile_board[tile_pos] = tile_board[tile_pos], tile_board[blank_tile_position]

    def undo_move_on_board(self, tile_board, tile_move):
        # Do the opposite move of make_move_on_board() to undo it on tile board
        if tile_move == self.UP:
            # If tile moves up then do the opposite move and move it down to undo it
            self.make_move_on_board(tile_board, self.DOWN)
        elif tile_move == self.DOWN:
            # If tile moves down then do the opposite move and move it up to undo it
            self.make_move_on_board(tile_board, self.UP)
        elif tile_move == self.LEFT:
            # If tile moves left then do the opposite move and move it right to undo it
            self.make_move_on_board(tile_board, self.RIGHT)
        elif tile_move == self.RIGHT:
            # If tile moves right then do the opposite move and move it left to undo ut
            self.make_move_on_board(tile_board, self.LEFT)

    def fetch_valid_moves_on_board(self, tile_board, previous_move=None):
        # This function returns a list of the valid moves to make on this board.

        blank_x, blank_y = self.locate_blank_tile_pos(tile_board)
        valid_moves_on_board = []
        if blank_y != self.matrix - 1 and previous_move != self.DOWN:
            # Verifies that the blank tile can go further down in matrix or not.
            # Appends up in the valid moves list meaning that the blank tile can be shifted up in matrix
            valid_moves_on_board.append(self.UP)

        if blank_x != self.matrix - 1 and previous_move != self.RIGHT:
            # Verifies that the blank tile can go further right in matrix or not.
            # Appends left in the valid moves list meaning that the blank tile can be shifted left in matrix
            valid_moves_on_board.append(self.LEFT)

        if blank_y != 0 and previous_move != self.UP:
            # Verifies that the blank tile can go further up in matrix or not.
            # Appends down in the valid moves list meaning that the blank tile can be shifted down in matrix
            valid_moves_on_board.append(self.DOWN)

        if blank_x != 0 and previous_move != self.LEFT:
            # Verifies that the blank tile can go further left in matrix or not.
            # Appends right in the valid moves list meaning that the blank tile can be shifted right in matrix
            valid_moves_on_board.append(self.RIGHT)

        return valid_moves_on_board

    def solve_attempt(self, tile_board, max_move, goal_state):
        # Performs the attempt to solve the n-tile puzzle in at most maximum number of moves or depth i.e 30
        # This function returns True if the puzzle if solved or else it returns False

        print('Attempting to solve in ', max_move, 'moves...')
        # This list would contain the moves i.e UP / DOWN / RIGHT / LEFT of only the path from first depth
        #    till and if solution is found
        solution_moves = []
        # Invokes attempt_move_on_board function for the tile to move as per valid moves
        puzzle_solved = self.attempt_move_on_board(tile_board, solution_moves, max_move, None, goal_state)

        if puzzle_solved:
            # If the puzzle is solved then display the start state matrix on the console
            self.display_tile_board(tile_board)
            for tile_move in solution_moves:
                # Displays which move is taken to reach to the solution / goal state
                print('Move', tile_move)
                # Performs the move on tile board
                self.make_move_on_board(tile_board, tile_move)
                print()
                # After move is perfomed on the tile board, display it on the console
                self.display_tile_board(tile_board)
                print()

            # Displays in how many moves or what depth the puzzle was solved in
            print('Solved in', len(solution_moves), 'moves:')
            print(', '.join(solution_moves))
            return True
        else:
            # Un-able to solve the puzzle in given maximum moves and returns False
            return False

    def attempt_move_on_board(self, board, moves_made, moves_remaining, prev_move, goal_state):
        # This function is called recursively to attempts all possible moves on the tile board
        # This runs until it finds a solution to solve the puzzle or reaches the maximum moves limit.
        # It returns True if a solution is found
        # It contains the series of moves to solve the puzzle. Returns False if remaining moves < 0

        if moves_remaining < 0:
            # This is a base case where the tile moves are exhausted and returns False
            return False

        if board == goal_state:
            # This is also a good base case when the current tile board matches with goal state board and returns True
            return True

        # This is the recursive case where the puzzle attempts each of the valid moves
        for move in self.fetch_valid_moves_on_board(board, prev_move):
            # Make the move once the valid move is found in the list
            self.make_move_on_board(board, move)
            # No. of nodes visited
            moves_made.append(move)
            self.nodes_explored.append(move)

            if self.attempt_move_on_board(board, moves_made, moves_remaining - 1, move, goal_state):
                # If the puzzle is solved, return True and reset the board to the original state
                self.undo_move_on_board(board, move)  # Reset to the original puzzle.
                return True

            # Undo the move to set up for the next move if the move can't be performed
            self.undo_move_on_board(board, move)
            # Removes the last tile move from the list since it was undone to get accurate visited nodes.
            moves_made.pop()
        # It is the negative base case which returns False when system unable to solve the puzzle.
        return False

    def solve_puzzle(self, start_state=dict, goal_state=None, file_name='IDDFS_output.csv'):
        # This condition is to solve only one puzzle passed in the argument in __main__
        if isinstance(start_state, list):
            # Creates the start state puzzle tile board
            puzzle_board = ([item for sublist in start_state[2] for item in sublist])
            # Starts the time to calculate total computation time
            start_time = time.time()
            # Initialised move counter to 1. move here defined the depth
            moves = 1
            # Converts the goal state into a list
            goal_state_list = ([item for sublist in goal_state[2] for item in sublist])
            while True:
                # Tries to solve the puzzle and breaks if puzzle is solved
                if self.solve_attempt(puzzle_board, max_move=moves, goal_state=goal_state_list):
                    self.solution_found = 1
                    break  # Break out of the loop when a solution is found.
                else:
                    # If puzzle isn't solved at 'move' depth then increment the move counter by 1
                    # Keeps on trying iteratively from the beginning till max limit of moves is reached i.e 30
                    moves += 1
                    if moves > 30:
                        # Breaks when depth limit is exhausted
                        print(f"Unable to solve the puzzle in {moves} moves. Proceeding with next state")
                        break
            # Calculates total computation time
            print('Run in', round(time.time() - start_time, 3), 'seconds.')
            # Writes the data into csv as per assessment brief
            self.write_csv_data(file_name, self.seed, 1, start_state, self.solution_found, moves,
                                len(self.nodes_explored), str(round(time.time() - start_time, 3)) + "s")
        else:
            # Runs as per assessment brief for 10 random states as per seed 755
            start_states_dict = self.get_random_states()
            goal_state_list = ([item for sublist in self.goal_state[2] for item in sublist])
            for k, v in start_states_dict.items():
                final_state_list = []
                blank_tile_index = np.where(np.array(v) == 0)
                # Finds blank tile position
                row, column = blank_tile_index[0][0], blank_tile_index[1][0]
                final_state_list.append(row)
                final_state_list.append(column)
                # Creates a final start state list to show in CSV as per assessment brief
                final_state_list.append(v)
                self.nodes_explored = []
                # Creates the puzzle tile board
                puzzle_board = ([item for sublist in v for item in sublist])
                start_time = time.time()
                # Initialised move counter to 1. move here defined the depth
                moves = 1
                while True:
                    # Tries to solve the puzzle and breaks if puzzle is solved
                    if self.solve_attempt(puzzle_board, max_move=moves, goal_state=goal_state_list):
                        self.solution_found = 1
                        break  # Break out of the loop when a solution is found.
                    else:
                        self.solution_found = 0
                        # If puzzle isn't solved at 'move' depth then increment the move counter by 1
                        # Keeps on trying iteratively from the beginning till max limit of moves is reached i.e 30
                        moves += 1
                        if moves > 30:
                            print(f"Unable to solve the puzzle in {moves} moves. Proceeding with next state")
                            break
                # Calculates total computation time
                print('Run in', round(time.time() - start_time, 3), 'seconds.')
                # Writes the data into csv as per assessment brief
                self.write_csv_data(file_name, self.seed, k, final_state_list, self.solution_found, moves,
                                    len(self.nodes_explored), str(round(time.time() - start_time, 3)) + "s")

    # Writes data into a csv as asked in assessment brief
    def write_csv_data(self, file_name, seed, case_no, case_start_state, solution_found, no_of_moves, nodes_opened,
                       computing_time):
        with open(file_name, 'a', newline='') as csvfile:
            fieldnames = ['Seed', 'Case Number', 'Case Start State', 'Solution Found', 'No. of moves',
                          'No. of Nodes opened', 'Computing Time']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            is_file_empty = os.stat(file_name).st_size
            if is_file_empty == 0:
                writer.writeheader()
            writer.writerow({'Seed': seed, 'Case Number': case_no, 'Case Start State': case_start_state,
                             'Solution Found': solution_found, 'No. of moves': no_of_moves,
                             'No. of Nodes opened': nodes_opened, 'Computing Time': computing_time})
            csvfile.close()

    # Clears the outfile first before running the code to solve puzzle
    def clear_csv(self, file_name):
        fo = open(file_name, "w")
        fo.writelines("")
        fo.close()


if __name__ == "__main__":
    obj = Iddfs()
    obj.clear_csv("IDDFS_output.csv")
    # obj.get_random_states()
    # obj.solve_puzzle(start_state=[2, 2, [[4, 7, 5], [3, 8, 1], [6, 2, 0]]],
    #                 goal_state=[1, 1, [[1, 2, 3], [8, 0, 4], [7, 6, 5]]])
    obj.solve_puzzle()
