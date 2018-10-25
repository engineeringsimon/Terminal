import random
import gamelib
import os
import copy
import pickle

from ReducedGameState import *
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
        
        # list of numbers is the number of neurons at each layer, length of array is number of layers.
        self.neural_network = NeuralNetwork.FeedforwardNetwork(layers = [10, 10, 10, 10, 10, 10, 10, 10])
        
    def next_defence_move(self, state): # ReducedGameState
        state_float_array = state.float_array()
        outputs = self.neural_network.calculate_output(state_float_array)
        # covert outputs to an actual best move
        # one of the possible moves needs to be do nothing
        # perhaps ensure that we choose the best move that doesn't have a piece there already.
        
        # possibile moves should be to remove units too, if there is one there.
        
        # do nothing
        return None
    
    def next_attack_move(self, state): 
        state_float_array = state.float_array()
        outputs = self.neural_network.calculate_output(state_float_array)
        return None # Do nothing
        
    def randomise(self):
        self.neural_network.randomise()
        
    def mutate(self):
        self.neural_network.mutate(0.02)
