import math
import random


class IDAStar(object):
    def __init__(self):
        self.no_of_tiles = 8
        self.initial_state = list(reversed(range(self.no_of_tiles + 1)))
        self.goal_state = [1, 1, [[1, 2, 3], [8, 0, 4], [7, 6, 5]]]
        self.matrix = int(math.sqrt(self.no_of_tiles + 1))

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


if __name__ == "__main__":
    obj = IDAStar()
    print(obj.get_random_states())