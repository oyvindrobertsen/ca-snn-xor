from __future__ import division

import random
import operator
import os

from subprocess import call
from itertools import imap
from datetime import datetime
from utils import *
from ea import Individual, EARunner
from ca import OneDimCA, ca_format
from snn import SNN

rule_110 = {
    "111": 0,
    "110": 1,
    "101": 1,
    "100": 0,
    "011": 1,
    "010": 1,
    "001": 1,
    "000": 0
}

#xor_initial_states = [
#    [1]*8 + [0]*24,
#    [0]*8 + [1]*8 + [0]*16,
#    [0]*16 + [1]*8 + [0]*8,
#    [0]*24 + [1]*8
#]

xor_initial_states = [[random.randint(0,1) for _ in range(32)] for _ in range(4)]

random_initial_states = [
    [random.randint(0, 1) for _ in range(8)],
    [random.randint(0, 1) for _ in range(8)]
]

def create_random_weight_config(topology, n_input, max_val):
        weights = []
        weights.append([random.randint(0, max_val) for _ in range(n_input*topology[0])])
        for i in range(1, len(topology)):
            weights.append([random.randint(0, max_val) for _ in range(topology[i-1]*topology[i])])
        return weights

class CASNNXORProblem(Problem):

    def __init__(self, topology, n_snn_input):
        self.topology = topology
        self.n_snn_input = n_snn_input

        self.state_histories = []
        self.output_histories = []
        for i, initial_state in enumerate(xor_initial_states):
            state_readouts = []
            output_readouts = []
            print "Developing CA for |", ca_format(initial_state), "|"
            ca = OneDimCA(initial_state, rule_110)
            for _ in range(300):
                ca.step()
                state_readouts.append(ca.state)
                output_readouts.append(ca.state.take([7, 15, 23, 31]))
            self.state_histories.append(state_readouts)
            self.output_histories.append(output_readouts)

    def fitness(self, phenotype):
        #print "Evaluating fitness for: "
        #print phenotype
        if sum(phenotype.weights[-1]) == 0:
            return 0

        hit_rates = []
        for i in range(len(xor_initial_states)):
            ca_output_states = self.output_histories[i]
            for j in range(50):
                phenotype.step(ca_output_states[j])
            snn_readouts = []
            for j in range(250):
                if j % 25 == 0:
                    snn_readouts.append(phenotype.step(ca_output_states[j])[0])
                else:
                    phenotype.step(ca_output_states[j])
            expected = 0 if i in (0, 3) else 1
            hit_rate = snn_readouts.count(expected)/len(snn_readouts)
            hit_rates.append(hit_rate)
        ret = sum(hit_rates) / len(hit_rates)
        return ret

    def create_initial_population(self, population_size):
        return [Individual(create_random_weight_config(
            self.topology,
            self.n_snn_input,
            2
        )) for _ in range(population_size)]

    def geno_to_pheno(self, genotype):
        return SNN(self.topology, genotype)

    def mutate_genome_component(self, component):
        new = []
        for weight in component:
            if random.randint(0, 1):
                if random.randint(0, 1):
                    new.append(weight + 1)
                else:
                    new.append(max(weight - 1, 0))
            else:
                new.append(weight)
        return new

    def visualization(self, *args, **kwargs):
        pass

def main():
    random.seed(datetime.now())

    problem = CASNNXORProblem([4, 2, 1], 4)
    population_size = 50
    generations = 1000
    crossover_rate = 0.2
    mutation_rate = 0.9
    adult_selection = generational_mixing
    adult_to_child_ratio = 0.3
    parent_selection = sigma_scaling_selection
    k = 8
    epsilon = 0.05
    crossover_function = braid
    mutation_function = per_genome
    threshold = 1.0

    runner = EARunner(
       problem=problem,
       population_size=population_size,
       generations=generations,
       crossover_rate=crossover_rate,
       mutation_rate=mutation_rate,
       adult_selection=adult_selection,
       adult_to_child_ratio=adult_to_child_ratio,
       parent_selection=parent_selection,
       k=k,
       epsilon=epsilon,
       crossover_function=crossover_function,
       mutation_function = mutation_function,
       threshold=threshold
    ) 
    runner.solve()
    runner.plot()


if __name__ == '__main__':
    main()
