import random


class FeedforwardNetwork:
    def __init__(self, layers):
        self.layers = layers
        
    def calculate_output(self, input_float_list):
        # output is a list of floats of the length of the last layer
        
        return [0.0 for i in range(self.layers[-1])]
        
    def randomise(self):
        pass
        
    def mutate(self, standard_deviation):
        pass
        
        