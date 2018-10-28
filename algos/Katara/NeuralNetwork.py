import random
import math

def squish(x):
    return 1.0 / (1.0 + math.exp(-x)) # signmoid function https://en.wikipedia.org/wiki/Sigmoid_function

class LayerWeights:
    def __init__(self, input_size, output_size):
        self.num_inputs = input_size
        self.num_outputs = output_size
        self.gains = [[0.0] * output_size] * input_size
        self.offset = [0.0] * input_size
        self.max_gain = 1.0
        self.min_gain = -self.max_gain
        
    def calculate_output(self, input_float_list):    
        #print("len(input_float_list) = {}".format(len(input_float_list)))
        #print("len(self.gains) = {}".format(len(self.gains)))
        #print("self.num_inputs = {}".format(self.num_inputs))
        #print("self.num_outputs = {}".format(self.num_outputs))
        assert len(input_float_list) == len(self.gains)
        
        raw_outputs = []
        for iOutput in range(self.num_outputs):
            output = 0.0
            for iInput in range(self.num_inputs):
                output += self.gains[iInput][iOutput] * input_float_list[iInput]
                output += self.offset[iInput]
                squished_output = squish(output)
            raw_outputs.append(squished_output)
        
        assert(len(raw_outputs) == self.num_outputs)
        return raw_outputs
        
    def __repr__(self):
        return "Layer (in: {}, out: {})".format(self.num_inputs, self.num_outputs)
        
    def randomise(self):
        self.gains = [[random.uniform(self.min_gain, self.max_gain) for i in range(self.num_outputs)] for j in range(self.num_inputs)]
        self.offset = [random.uniform(self.min_gain, self.max_gain) for i in range(self.num_inputs)]
        
    def mutate(self, standard_deviation):
        for a in self.gains:
            for b in a:
                b += random.normalvariate(0.0, standard_deviation)
                if b > self.max_gain:
                    b = self.max_gain
                elif b < self.min_gain:
                    b = self.min_gain
        for b in self.offset:
            b += random.normalvariate(0.0, standard_deviation)
            if b > self.max_gain:
                b = self.max_gain
            elif b < self.min_gain:
                b = self.min_gain
                
class FeedforwardNetwork:
    def __init__(self, layers):
        self.layer_sizes = layers
        self.node_layers = []
        for size in self.layer_sizes:
            self.node_layers.append([0.0] * size)
            
        self.num_layers = len(self.layer_sizes)
        self.connections = []
        for i in range(1, self.num_layers):
            self.connections.append(LayerWeights(self.layer_sizes[i - 1], self.layer_sizes[i]))
        
    def calculate_output(self, input_float_list):
        # output is a list of floats of the length of the last layer
        assert len(input_float_list) == len(self.node_layers[0]), "Input length = {}, layer 0 = {}, ls {}".format(len(input_float_list), len(self.node_layers[0]), self.layer_sizes)
        self.node_layers[0] = input_float_list
        
        for i in range(1, self.num_layers):
            #print("working on layer {} of {}, {}".format(i, self.num_layers, len(self.connections)))
            w = self.connections[i - 1]
            self.node_layers[i] = w.calculate_output(self.node_layers[i - 1])

        return self.node_layers[-1].copy()
        
    def randomise(self):
        for c in self.connections:
            c.randomise()
        
    def mutate(self, standard_deviation):
        for c in self.connections:
            c.mutate(standard_deviation)
        
        