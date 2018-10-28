import random
import gamelib
import os
import copy
import pickle

from ReducedGameState import *
from OutputState import *
import NeuralNetwork


local_path = os.path.dirname(os.path.realpath(__file__))
base_strategy_filename = "baseStrategy.pickle"
mutated_strategy_filename = "mutatedStrategy.pickle"
base_strategy_path = os.path.join(local_path, base_strategy_filename)
mutated_strategy_path = os.path.join(local_path, mutated_strategy_filename)
ARENA_SIZE = 28
HALF_ARENA = 14
FILTER = "FF"
ENCRYPTOR = "EF"
DESTRUCTOR = "DF"
PING = "PI"
EMP = "EI"
SCRAMBLER = "SI"
        

def Make(my_side, friendly_edge_locations):
    if os.path.exists(base_strategy_path):
        with open(base_strategy_path, 'rb') as f:
            strategy = pickle.load(f)
    else:
        strategy = KataraStrategyData(my_side, friendly_edge_locations)
        strategy.randomise()
        with open(base_strategy_path, 'wb') as f:
            pickle.dump(strategy, f)
            
    mutated_strategy = copy.deepcopy(strategy)
    mutated_strategy.mutate()
    with open(mutated_strategy_path, 'wb') as f:
        pickle.dump(mutated_strategy, f)
    
    return strategy
    
class KataraStrategyData:
    def __init__(self, my_side, friendly_edge_locations):
        self.friendly_edge_locations = friendly_edge_locations
        self.my_side = my_side
        self.input_size = input_size()
        self.num_hidden_layers = 2
        self.hidden_layer_size = 32
        self.output_size = output_size()
        
        layer_sizes = [self.input_size]
        layer_sizes += [self.hidden_layer_size] * self.num_hidden_layers
        layer_sizes += [self.output_size]
        
        # list of numbers is the number of neurons at each layer, length of array is number of layers.
        self.neural_network = NeuralNetwork.FeedforwardNetwork(layers = layer_sizes)
        
    def update(self, state):
        self.state_float_array = state.float_array()
        self.outputs = self.neural_network.calculate_output(self.state_float_array)
        self.output_state = OutputState(self.outputs)
        
    def next_defence_move(self, state): # ReducedGameState
        return self.output_state.best_defence_move(state.occupied_locations)
    
    def next_attack_move(self, state): 
        return self.output_state.best_attack_move(state.occupied_locations)
        
    def randomise(self):
        self.neural_network.randomise()
        
    def mutate(self):
        self.neural_network.mutate(0.02)
