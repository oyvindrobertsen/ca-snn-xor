class Neuron():
    def __init__(self, weights):
        self.weights = weights
        self.counters = [0] * len(weights)

    def step(self, input_vec):
        for i in range(len(self.weights)):
            if (self.weights[i] != 0 and self.weights[i] != self.counters[i]):
                self.counters[i] += input_vec[i]
        if self.weights == self.counters:
            self.counters = [0] * len(self.weights)
            return 1
        else:
            return 0

    def __repr__(self):
        return ' '.join(map(str, zip(self.weights, self.counters)))
            

class SNNLayer():
    def __init__(self, n_neurons, weights):
        self.neurons = []
        n_prev_neurons = len(weights) // n_neurons
        for i in range(n_neurons):
            self.neurons.append(Neuron(weights[i*n_prev_neurons:(i+1)*n_prev_neurons]))

    def step(self, input_vec):
        return [neuron.step(input_vec) for neuron in self.neurons]
            
    def __repr__(self):
        return ' | '.join(list(map(lambda n: n.__repr__(), self.neurons)))
        

class SNN():
    def __init__(self, topology, weights):
        self.weights = weights
        self.layers = [SNNLayer(topology[i], weights[i]) for i in range(len(topology))]
        self.activation_values = [[0 for neuron in range(layer)] for layer in topology]

    def step(self, input_vec):
        new_activation_values = []
        new_activation_values.append(self.layers[0].step(input_vec))
        for i in range(1, len(self.layers)):
            new_activation_values.append(self.layers[i].step(self.activation_values[i-1]))
        self.activation_values = new_activation_values
        return self.activation_values[-1]

    def __repr__(self):
        return '\n'.join(list(map(lambda l: l.__repr__(), self.layers)))

        
