from __future__ import division

import random
import operator
import os

from subprocess import call
from itertools import imap
from datetime import datetime
from utils import *
from ea import Individual, EARunner

desired = [0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0]
devnull = open(os.devnull, 'w')

def hamming_distance(seq1, seq2):
    assert len(seq1) == len(seq2)
    return sum(imap(operator.ne, seq1, seq2))


# [[1, 1, 2, 0, 1, 1, 2, 2, 0, 0, 0, 0, 3, 0, 1, 0], [1, 0, 0, 0, 0, 0, 1, 0], [1, 1]] GG?

def create_random_weight_config():
        weights = []
        weights.append([random.randint(0, 1) for _ in range(16)])
        weights.append([random.randint(0, 1) for _ in range(8)])
        weights.append([random.randint(0, 1) for _ in range(2)])
        return weights

class CASNNXORProblem(Problem):

    def fitness(self, phenotype):
        print "Evaluating fitness for: "
        print phenotype
        # Write weights
        with open('weights', 'w') as f:
            for layer in phenotype:
                f.write(' '.join(map(str, layer)) + '\n')

        # Run simulation
        call(["sbt \"test:run-main plan9.CASNNXOR\""], cwd="../", shell=True, stdout=devnull, stderr=devnull)

        # Read results
        with open('results', 'r') as f:
            readouts = map(lambda st: int(st.strip()), f.readlines())

        # Calculate fitness
        ret = 1 - (hamming_distance(readouts, desired) / len(readouts))
        print "Fitness: ", ret
        return ret

    def create_initial_population(self, population_size):
        return [Individual(create_random_weight_config()) for _ in range(population_size)]

    def geno_to_pheno(self, genotype):
        return genotype

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
    problem = CASNNXORProblem()
    population_size = 10
    generations = 30
    crossover_rate = 0.8
    mutation_rate = 0.4
    adult_selection = generational_mixing
    adult_to_child_ratio = 0.5
    parent_selection = sigma_scaling_selection
    k = 8
    epsilon = 0.05
    crossover_function = braid
    mutation_function = per_genome_component
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
