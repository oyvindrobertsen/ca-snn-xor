 # -*- coding: utf-8 -*-

import numpy as np
 
def ca_format(states):
    return ''.join(map(lambda s: '█' if s else ' ', states))

class OneDimCA():
    def __init__(self, initial_state, lut):
        self.state = np.array(initial_state)
        self.lut = lut
        assert len(lut.keys()[0]) % 2
        self.neighborhood_distance = (len(self.lut.keys()[0]) - 1) // 2

    def get_element(self, i):
        if i < 0 or i >= len(self.state):
            return 0
        return self.state[i]

    def get_neighborhood(self, i):
        return [self.get_element(j) for j in range(i-self.neighborhood_distance, i+self.neighborhood_distance+1)]

    def step(self):
        nd = self.neighborhood_distance
        new_state = []
        for i in range(len(self.state)):
            neighborhood = self.get_neighborhood(i)
            new_state.append(self.lut[''.join(map(str, neighborhood))])
        self.state = np.array(new_state)

    def print_state(self):
        print ca_format(self.state)
