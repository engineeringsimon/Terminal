import random
import gamelib
import os
import copy
import pickle

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

        
# Dumb wall
dumb_wall_layout = '''
FFFFFFFFFFFFFFFFFFFFFFFFFFFF
 .......................... 
  ........................ 
   ......................
    .................... 
     .................. 
      ................ 
       .............. 
        ............ 
         .......... 
          ........ 
           ...... 
            .... 
             .. 
''' 
desired_layout_str = dumb_wall_layout 

def Make(my_side, friendly_edge_locations):
    if os.path.exists(base_strategy_path):
        with open(base_strategy_path, 'rb') as f:
            strategy = pickle.load(f)
    else:
        strategy = TophStrategyData(my_side, friendly_edge_locations)
        strategy.randomise()
        with open(base_strategy_path, 'wb') as f:
            pickle.dump(strategy, f)
            
    mutated_strategy = copy.deepcopy(strategy)
    mutated_strategy.mutate()
    with open(mutated_strategy_path, 'wb') as f:
        pickle.dump(mutated_strategy, f)
    
    return strategy
    
def layout_from_string(layout_string, my_side):
    my_unit_code = {
        'D': DESTRUCTOR,
        'F': FILTER,
        'E': ENCRYPTOR,
        'X': EMP,
        'P': PING,
        'S': SCRAMBLER
        }    
    i = 0
    lines = layout_string.split("\n")[1:]
    desired_layout = {}
    for loc in my_side:
        x = loc[0]
        y = loc[1]
        character = lines[HALF_ARENA - 1 - y][x]
        if character in my_unit_code:
            desired_layout[x, y] = my_unit_code[character]
    return desired_layout
    
class TophStrategyData:
    def __init__(self, my_side, friendly_edge_locations):
        self.friendly_edge_locations = friendly_edge_locations
        self.my_side = my_side
        
    def randomise(self):
        self.desired_layout = layout_from_string(desired_layout_str, self.my_side)
    
    def mutate(self):
        pass
      

    