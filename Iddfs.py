import math
import random
import time


class Iddfs(object):
    def __init__(self):
        self.no_of_tiles = 8
        self.initial_state = list(reversed(range(self.no_of_tiles + 1)))
        self.goal_state = [1, 1, [[1, 2, 3], [8, 0, 4], [7, 6, 5]]]
        self.states = []
        self.matrix = int(math.sqrt(self.no_of_tiles + 1))
        self.UP = 'up'
        self.DOWN = 'down'
        self.LEFT = 'left'
        self.RIGHT = 'right'

    def random_states_generator(self, n):
        random.seed(755)
        for _ in range(1, 11):
            final_list = []
            random.shuffle(self.initial_state)
            for j in range(0, len(self.initial_state), n):
                final_list.append(self.initial_state[j:j + n])
                if len(final_list) == self.matrix:
                    yield final_list
                else:
                    pass

    def get_random_states(self):
        x = self.random_states_generator(self.matrix)
        state_counter = 1
        state_dict = {}
        for i in x:
            start_states_array = i
            state_dict[state_counter] = start_states_array
            state_counter += 1
        return state_dict

    def find_blank_space(self, board):
        """Return an [x, y] list of the blank space's location."""
        for x in range(self.matrix):
            for y in range(self.matrix):
                if board[y * self.matrix + x] == 0:
                    return [x, y]

    def display_board(self, board):
        for y in range(self.matrix):  # Iterate over each row.
            for x in range(self.matrix):  # Iterate over each column.
                if board[y * self.matrix + x] == 0:
                    print('_ ', end='')  # Display blank tile.
                else:
                    print(str(board[y * self.matrix + x]).rjust(2) + ' ', end='')
            print()  # Print a newline at the end of the row.

    def make_move(self, board, move):
        """Modify `board` in place to carry out the slide in `move`."""
        bx, by = self.find_blank_space(board)
        blank_index = by * self.matrix + bx
        tile_index = 0
        if move == self.UP:
            tile_index = (by + 1) * self.matrix + bx
        elif move == self.LEFT:
            tile_index = by * self.matrix + (bx + 1)
        elif move == self.DOWN:
            tile_index = (by - 1) * self.matrix + bx
        elif move == self.RIGHT:
            tile_index = by * self.matrix + (bx - 1)

        # Swap the tiles at blankIndex and tileIndex:
        board[blank_index], board[tile_index] = board[tile_index], board[blank_index]

    def undo_move(self, board, move):
        """Do the opposite move of `move` to undo it on `board`."""
        if move == self.UP:
            self.make_move(board, self.DOWN)
        elif move == self.DOWN:
            self.make_move(board, self.UP)
        elif move == self.LEFT:
            self.make_move(board, self.RIGHT)
        elif move == self.RIGHT:
            self.make_move(board, self.LEFT)

    def get_valid_moves(self, board, prev_move=None):
        """Returns a list of the valid moves to make on this board. If
        prevMove is provided, do not include the move that would undo it."""

        blank_x, blank_y = self.find_blank_space(board)

        valid_moves = []
        if blank_y != self.matrix - 1 and prev_move != self.DOWN:
            # Blank space is not on the bottom row.
            valid_moves.append(self.UP)

        if blank_x != self.matrix - 1 and prev_move != self.RIGHT:
            # Blank space is not on the right column.
            valid_moves.append(self.LEFT)

        if blank_y != 0 and prev_move != self.UP:
            # Blank space is not on the top row.
            valid_moves.append(self.DOWN)

        if blank_x != 0 and prev_move != self.LEFT:
            # Blank space is not on the left column.
            valid_moves.append(self.RIGHT)

        return valid_moves

    def solve(self, board, max_move, goal_state):
        """Attempt to solve the puzzle in `board` in at most `maxMoves`
        moves. Returns True if solved, otherwise False."""
        print('Attempting to solve in ', max_move, 'moves...')
        solution_moves = []  # A list of UP, DOWN, LEFT, RIGHT values.
        solved = self.attempt_move(board, solution_moves, max_move, None, goal_state)

        if solved:
            self.display_board(board)
            for move in solution_moves:
                print('Move', move)
                self.make_move(board, move)
                print()  # Print a newline.
                self.display_board(board)
                print()  # Print a newline.

            print('Solved in', len(solution_moves), 'moves:')
            print(', '.join(solution_moves))
            return True  # Puzzle was solved.
        else:
            return False

    def attempt_move(self, board, moves_made, moves_remaining, prev_move, goal_state):
        """A recursive function that attempts all possible moves on `board`
        until it finds a solution or reaches the `maxMoves` limit.
        Returns True if a solution was found, in which case `movesMade`
        contains the series of moves to solve the puzzle. Returns False
        if `movesRemaining` is less than 0."""

        if moves_remaining < 0:
            # BASE CASE - Ran out of moves.
            return False

        if board == goal_state:
            # BASE CASE - Solved the puzzle.
            return True

        # RECURSIVE CASE - Attempt each of the valid moves:
        for move in self.get_valid_moves(board, prev_move):
            # Make the move:
            self.make_move(board, move)
            moves_made.append(move)

            if self.attempt_move(board, moves_made, moves_remaining - 1, move, goal_state):
                # If the puzzle is solved, return True:
                self.undo_move(board, move)  # Reset to the original puzzle.
                return True

            # Undo the move to set up for the next move:
            self.undo_move(board, move)
            moves_made.pop()  # Remove the last move since it was undone.
        return False  # BASE CASE - Unable to find a solution.

    def solve_puzzle(self, start_state=dict, goal_state=None):
        if isinstance(start_state, list):
            puzzle_board = ([item for sublist in start_state[2] for item in sublist])
            start_time = time.time()
            moves = 1
            goal_state_list = ([item for sublist in goal_state[2] for item in sublist])
            while True:
                if self.solve(puzzle_board, max_move=moves, goal_state=goal_state_list):
                    break  # Break out of the loop when a solution is found.
                else:
                    moves += 1
                    if moves > 30:
                        print(f"Unable to solve the puzzle in {moves} moves. Proceeding with next state")
                        break
            print('Run in', round(time.time() - start_time, 3), 'seconds.')
        else:
            start_states_dict = self.get_random_states()
            goal_state_list = ([item for sublist in self.goal_state[2] for item in sublist])
            for k, v in start_states_dict.items():
                puzzle_board = ([item for sublist in v for item in sublist])
                start_time = time.time()
                moves = 1
                while True:
                    if self.solve(puzzle_board, max_move=moves, goal_state=goal_state_list):
                        break  # Break out of the loop when a solution is found.
                    else:
                        moves += 1
                        if moves > 30:
                            print(f"Unable to solve the puzzle in {moves} moves. Proceeding with next state")
                            break
                print('Run in', round(time.time() - start_time, 3), 'seconds.')


if __name__ == "__main__":
    obj = Iddfs()
    # obj.solve_puzzle(start_state=[2, 2, [[4, 7, 5], [3, 8, 1], [6, 2, 0]]],
    #                goal_state=[1, 1, [[1, 2, 3], [8, 0, 4], [7, 6, 5]]])
    obj.solve_puzzle()
