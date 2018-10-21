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
    
def random_defender():
    return random.choice([FILTER, ENCRYPTOR, DESTRUCTOR])

def surrounding_locations(location_tuple, radius=1):
    (x, y) = location_tuple
    locations = []
    for i in range(x - radius, x + radius + 1):
        for j in range(y - radius, y + radius + 1):
            if i == x and j == y:
                continue
            locations.append((i, j))
    return locations
    
class TophStrategyData:
    def __init__(self, my_side, friendly_edge_locations):
        self.friendly_edge_locations = friendly_edge_locations
        self.my_side = my_side
        
    def randomise(self):
        self.desired_layout = layout_from_string(desired_layout_str, self.my_side)
    
    def mutate(self):
        '''
            The following methods of mutation can be used on the layout:
            Addition of a new unit
            Deletion of an existing unit
            Move an existing unit to an adjacent point
            Morph a unit type
            
            Note that this is for defense only right now
        '''
        ADD = 0
        DELETE = 1
        MOVE = 2
        MORPH = 3
        
        mutation_type = random.choice([ADD, DELETE, MOVE, MORPH])
        if mutation_type == ADD:
            self.add_random_defender()
        elif mutation_type == DELETE:
            self.remove_random_defender()
        elif mutation_type == MOVE:
            self.move_random_defender()
        else:
            self.morph_random_defender()
        
    def add_random_defender(self):
        available_locations = [(loc[0], loc[1]) for loc in self.my_side if (loc[0], loc[1]) not in self.desired_layout]
        location = random.choice(available_locations)
        unit_type = random_defender()
        self.desired_layout[location] = unit_type

    def remove_random_defender(self):
        occupied_locations = [loc for loc in self.desired_layout.keys()]
        location = random.choice(occupied_locations)
        self.desired_layout.pop(location)
        
    def move_random_defender(self):
        occupied_locations = [loc for loc in self.desired_layout.keys()]
        start_location = random.choice(occupied_locations)
        surrounding_loc = surrounding_locations(start_location)
        avail_surr_loc = [loc for loc in surrounding_loc if [loc[0], loc[1]] in self.my_side]
        if len(avail_surr_loc) == 0:
            return
        end_location = random.choice(avail_surr_loc)
        self.desired_layout[end_location] = self.desired_layout[start_location]
        self.desired_layout.pop(start_location)
        
    def morph_random_defender(self):
        occupied_locations = [loc for loc in self.desired_layout.keys()]
        location = random.choice(occupied_locations)
        old_defender = self.desired_layout[location]
        while self.desired_layout[location] == old_defender:
            self.desired_layout[location] = random_defender()