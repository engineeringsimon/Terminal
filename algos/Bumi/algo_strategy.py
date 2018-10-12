import gamelib
import random
import math
import warnings
from sys import maxsize

"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips: 

Additional functions are made available by importing the AdvancedGameState 
class from gamelib/advanced.py as a replcement for the regular GameState class 
in game.py.

You can analyze action frames by modifying algocore.py.

The GameState.map object can be manually manipulated to create hypothetical 
board states. Though, we recommended making a copy of the map to preserve 
the actual current map state.
"""

'''
Idea for strategy

make copies of of the game state. 
- Do a monte carlo simulation?
- do several random attacks by enemy.
- pick worst one
- do several random defences + attacks
- pick best one

or

- pick random action
-- do many random responses from current state by enemy and evaluate the state after a turn
- repeat for many actions

so the trick will be approximating the outcome of the next turn


'''

import copy

class PointHistogram:
    def __init__(self):
        self.ps = {}
        
    def add(self, key, value):
        if key in self.ps:
            self.ps[key] += value
        else:
            self.ps[key] = value
            
    def value(self, key):
        if key in self.ps:
            return self.ps[key]
        return 0
        
    def sorted_keys(self):
        k = [x for x in self.ps.keys()]
        k.sort(key=lambda x: self.ps[x], reverse=True)
        return k
        
# D = DESTRUCTOR, F=FILTER, E=ENCRYPTOR

funnel_layout= '''
DD........................DD
 DD......................DD 
  F...D....D....D....D...F 
   F....................F 
    F....D....D....D...F 
     F................F 
      F..............F 
       F...D....D...F 
        F..........F 
         F........F 
          ........ 
           ...... 
            .... 
             .. 
'''      
  
advance_wall_layout= '''
FFFFFFFFFFFFFFFFFFFFFFFFFFFF
 DD....D....D....D....D..DD 
  DD...E....E....E....E.DD 
   F....................F 
    F....D....D....D...F 
     F................F 
      F..............F 
       F...D....D...F 
        F..........F 
         F........F 
          ........ 
           ...... 
            .... 
             .. 
'''  

  
timid_wall_layout= '''
FF........................FF
 DFF....................FFD 
  DDF................F.DDD 
   .DFFFFFFFFFFFFFFFF..DD 
    .D.D.DEDEDEDEDED..EE 
     .................. 
      ................ 
       ..........D... 
        ............ 
         .....D.... 
          ........ 
           ...... 
            .... 
             .. 
''' 

#Gyatso
sneak_attack_layout= '''
FF......................FD..
 FF....................FD.. 
  DDF................FFE.. 
   DDFFFFFFFFFFFFFFFFFE.. 
    DD.D.D.D.D.D.D.DDE.. 
     F..............E.. 
      F............E.. 
       F.....D....E.. 
        F........E.. 
         F......F.. 
          F....F.. 
           F..F.. 
            .... 
             X. 
''' 

# Gyatso
sneak_attack_layout= '''
FF......................FD..
 FF....................FD.. 
  DDF................FFE.. 
   DDFFFFFFFFFFFFFFFFFE.. 
    DD.D.D.D.D.D.D.DDE.. 
     F..............E.. 
      F............E.. 
       F.....D....E.. 
        F........E.. 
         F......F.. 
          F....F.. 
           F..F.. 
            .... 
             X. 
''' 


# Paku
venus_flytrap_layout= '''
FFF.....................FD..
 DDFF..................FD.. 
  DDFF...............FFD.. 
   DDFFFF.FFFFFFF.FFFEE.. 
    DD.D...D...D...DDE.. 
     ..........D....E.. 
      ..D..........E.. 
       ......D....E.. 
        .........E.. 
         .......F.. 
          .....F.. 
           FFFF.. 
            .... 
             X. 
'''  

# Bumi
bumi_layout = '''
FFF......................FFF
 DFF....................FFD 
  ...D................D... 
   .....D..........D..... 
    .......D....D....... 
     .................. 
      ................ 
       S............S 
        ............ 
         .......... 
          ........ 
           ...... 
            .... 
             XX 
''' 

# Bumi2
bumi2_layout = '''
F........................F..
 F......................F.. 
  F....................F.. 
   F..................F.. 
    F................F.. 
     F..............F.. 
      F............F.. 
       F..........F.. 
        FDDDDD...F.. 
         .......F.. 
          FFFFFF.. 
           ...... 
            .... 
             .. 
''' 

# Test
test_layout = '''
............................
 .......................... 
  ........................ 
   ...................... 
    .................... 
     .................. 
      ........D....... 
       .............. 
        ............ 
         .......... 
          ........ 
           ...... 
            .... 
             XX 
''' 

'''
    Idea for stategy:
    Make fields of:
    - areas covered by enemy destructors
    - areas covered by friendly destructors
    - enemy paths
    - friendly paths
    - areas within striking range of enemy EMP
    - areas that an EMP could hit enemy units
    - 
'''

   
desired_layout = bumi2_layout   

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        random.seed()
        self.turn_count = 0
        self.name = "Bumi"
        self.all_arena_locations = []
        self.is_printing_debug = True
        
    def debug_print(self, str):
        if self.is_printing_debug:
            gamelib.debug_write(str)

    def on_game_start(self, config):
        """ 
        Read in config and perform any initial setup here 
        """
        self.debug_print('Configuring {}...'.format(self.name))
        self.config = config
        global FILTER, ENCRYPTOR, DESTRUCTOR, PING, EMP, SCRAMBLER
        FILTER = config["unitInformation"][0]["shorthand"]
        ENCRYPTOR = config["unitInformation"][1]["shorthand"]
        DESTRUCTOR = config["unitInformation"][2]["shorthand"]
        PING = config["unitInformation"][3]["shorthand"]
        EMP = config["unitInformation"][4]["shorthand"]
        SCRAMBLER = config["unitInformation"][5]["shorthand"]
        
        self.stability = {
                PING: 15,
                EMP: 5,
                SCRAMBLER: 40,
                FILTER: 60,
                ENCRYPTOR: 30,
                DESTRUCTOR: 75
                }
        self.my_unit_code = {
                'D': DESTRUCTOR,
                'F': FILTER,
                'E': ENCRYPTOR,
                'X': EMP,
                'P': PING,
                'S': SCRAMBLER
                }
        self.desired_layout_string = desired_layout
        self.placement_hist = PointHistogram()
        self.enemy_destructor_coverage = PointHistogram()
        self.friendly_destructor_coverage = PointHistogram()
        self.enemy_emp_coverage = PointHistogram()
        self.enemy_path_hist = PointHistogram()
        self.friendly_path_hist = PointHistogram()
        
        
    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        self.game_state = gamelib.AdvancedGameState(self.config, turn_state)
        self.debug_print('Performing turn {} of the {} strategy'.format(self.game_state.turn_number, 
                                self.name))
        #game_state.suppress_warnings(True)  #Uncomment this line to suppress warnings.

        if (self.game_state.turn_number == 0):
            self.execute_first_turn()
        
        self.execute_strategy()

        self.print_map()
        
        self.game_state.submit_turn()

        
    def execute_first_turn(self):
        self.all_arena_locations = self.all_valid_map_locations()
        self.friendly_edge_locations = self.friendly_edge_locations()
        
        #My Side
        self.my_side = []
        for i in range(self.game_state.ARENA_SIZE):
            for j in range(self.game_state.HALF_ARENA):
                location = [i,j]
                if self.game_state.game_map.in_arena_bounds(location):
                    self.my_side.append(location)

        # Make a lookup of all the points within 3.5 of each point and put them in a dictionary
        self.destructor_range_points = {}
        for location in self.all_arena_locations:
            x = location[0]
            y = location[1]
            self.destructor_range_points[x, y] = self.game_state.game_map.get_locations_in_range((x, y), 3.5)

        # Make a lookup of all the points within 4.5 of each point and put them in a dictionary
        self.emp_range_points = {}
        for location in self.all_arena_locations:
            x = location[0]
            y = location[1]
            self.emp_range_points[x, y] = self.game_state.game_map.get_locations_in_range((x, y), 4.5)

        # covert layout string to layout
        i = 0
        lines = self.desired_layout_string.split("\n")[1:]
        for line in lines:
            self.debug_print("{}: {}".format(i, line))
            i += 1
        self.desired_layout = {}
        for loc in self.my_side:
            x = loc[0]
            y = loc[1]
            character = lines[self.game_state.HALF_ARENA - 1 - y][x]
            if character in self.my_unit_code:
                self.desired_layout[x, y] = self.my_unit_code[character]
        
        self.enemy_edges = self.game_state.game_map.get_edge_locations(self.game_state.game_map.TOP_RIGHT) + self.game_state.game_map.get_edge_locations(self.game_state.game_map.TOP_LEFT)
        
        self.gap = []
        for i in range(self.game_state.game_map.HALF_ARENA):
            self.gap.append([i + self.game_state.game_map.HALF_ARENA - 1, i])
            self.gap.append([i + self.game_state.game_map.HALF_ARENA, i])
        
    def execute_strategy(self):
        self.update_field_calcs()
        self.build_defences()
        self.place_destructors()
        self.place_attackers()
        
    def update_field_calcs(self):
        self.update_destructor_coverage()
        self.update_enemy_paths()
        self.update_friendly_paths()
        self.update_enemy_emp_coverage()
        
    def update_enemy_emp_coverage(self):
        self.enemy_emp_coverage = PointHistogram()
        for (key, value) in self.enemy_path_hist.ps.items():
            emp_points = self.emp_range_points[key]
            for loc in emp_points:
                self.enemy_emp_coverage.add((loc[0], loc[1]), value)

    def update_enemy_paths(self):
        self.enemy_path_hist = PointHistogram()
        avail_enemy_launch_loc = [x for x in self.enemy_edges if not self.game_state.contains_stationary_unit(x)]
        random.shuffle(avail_enemy_launch_loc)
        launch_locs = avail_enemy_launch_loc #[:4]
        paths = [self.game_state.find_path_to_edge(x, self.calc_destination(x))
                    for x in launch_locs]
        ph = self.enemy_path_hist        
        for path in paths:
            for loc in path:
                ph.add((loc[0], loc[1]), 1)
         
    def update_friendly_paths(self):
        launch_locations = self.available_launch_locations() 
        launch_info = [(x, self.calc_destination(x)) for x in launch_locations]
        paths = [self.game_state.find_path_to_edge(loc, destination) for (loc, destination) in launch_info]
        self.friendly_paths = paths
        self.friendly_path_hist = PointHistogram()
        for path in paths:
            for loc in path:
                self.friendly_path_hist.add((loc[0], loc[1]), 1)
 
    def update_destructor_coverage(self):
        self.enemy_destructor_coverage = PointHistogram()
        self.friendly_destructor_coverage = PointHistogram()
        for location in self.all_arena_locations:
            units = self.game_state.game_map[location[0], location[1]]
            if units and len(units) > 0 and units[0].unit_type == DESTRUCTOR:
                for x in self.destructor_range_points[location[0], location[1]]:
                    if units[0].player_index == 0: # friendly
                        self.friendly_destructor_coverage.add((x[0], x[1]), 1)
                    else:
                        self.enemy_destructor_coverage.add((x[0], x[1]), 1)
    
    def place_destructors(self):
        potential_locations = self.enemy_path_hist.sorted_keys()
        destructor_points = [x for x in potential_locations if [x[0], x[1]] in self.my_side and [x[0], x[1]] not in self.gap]

        for loc in destructor_points:
            isOk = self.place_unit(DESTRUCTOR, loc)
            if not isOk:
                break
    
    def eval_friendly_path(self, path):
        num_in_range_points = 0
        for loc in path:
            num_in_range_points += self.enemy_destructor_coverage.value((loc[0], loc[1]))

        is_successful = path[-1] in self.enemy_edges
        return (num_in_range_points, is_successful)
    
    def place_attackers(self):
        path_info = [(self.eval_friendly_path(x), x[0]) for x in self.friendly_paths]
        path_info.sort(key=lambda x: x[0][0])
        num_in_range_points = path_info[0][0][0]
        is_successful = path_info[0][0][1]
        loc = path_info[0][1]
        
        if num_in_range_points <= 2 and is_successful:
            self.place_unit(PING, loc, 100)
            #self.debug_print("PING!")
        elif num_in_range_points > 60 and is_successful:
            self.place_unit(SCRAMBLER, loc, 2)
            self.place_unit(EMP, loc, 100)
            #self.debug_print("SCRAMBLER! etc.")
        else:
            self.place_unit(EMP, loc, 100)
            #self.debug_print("EMP!")
        
    def enemy_destructor_locations(self):
        locations = []
        for i in range(self.game_state.ARENA_SIZE):
            for j in range(self.game_state.HALF_ARENA, self.game_state.ARENA_SIZE):
                if self.is_destructor_at_loc([i, j]):
                    locations.append([i, j])
        return locations
        
    def calc_destination(self, loc):
        if loc in self.game_state.game_map.get_edge_locations(self.game_state.game_map.BOTTOM_LEFT):
            return self.game_state.game_map.TOP_RIGHT
        elif loc in self.game_state.game_map.get_edge_locations(self.game_state.game_map.BOTTOM_RIGHT):
            return self.game_state.game_map.TOP_LEFT
        elif loc in self.game_state.game_map.get_edge_locations(self.game_state.game_map.TOP_RIGHT):
            return self.game_state.game_map.BOTTOM_LEFT
        return self.game_state.game_map.BOTTOM_RIGHT
    
    def all_attacking_launch_positions(self):
        locations = [loc for loc in self.desired_layout if self.desired_layout[loc] in [EMP, SCRAMBLER, PING]]
        if len(locations) == 0:
            return [13, 0]
        return locations
    
    def choose_attacking_position(self):
        locations = [loc for loc in self.desired_layout if self.desired_layout[loc] in [EMP, SCRAMBLER, PING]]
        if len(locations) == 0:
            return [13, 0]
        (x, y) = random.choice(locations)
        self.debug_print("choosing {}, from {}".format((x,y), locations))
        return [x, y]

    def available_launch_locations(self):
        return [x for x in self.friendly_edge_locations if not self.game_state.contains_stationary_unit(x)]
        
    def random_available_edge(self):
        locations = self.available_launch_locations()
        return random.choice(locations)
        
    def build_defences(self):
        locations = [loc for loc in self.desired_layout if not self.game_state.contains_stationary_unit(loc)]
        random.shuffle(locations)
        locations.sort(key=lambda x: x[1], reverse=True)
        for loc in locations:
            unit_id = self.desired_layout[loc[0], loc[1]]
            if unit_id in [DESTRUCTOR, FILTER, ENCRYPTOR]:  
                if unit_id == FILTER and self.placement_hist.value((loc[0], loc[1])) > 0:
                    unit_id = DESTRUCTOR    
                isOk = self.place_unit(unit_id, loc)
                if not isOk: 
                    break            
    
        
    def is_destructor_at_loc(self, loc):
        units = self.game_state.game_map[loc[0], loc[1]]
        if units == None or len(units) == 0:
            return False
        unit = units[0]
        return unit.unit_type == DESTRUCTOR
        
    def place_unit(self, unit_type, location, num=1):
        number_placed = 0
        while number_placed < num:
            if self.game_state.number_affordable(unit_type) > 0:
                if self.game_state.can_spawn(unit_type, location):
                    self.game_state.attempt_spawn(unit_type, location)  
                    number_placed += 1
                    self.placement_hist.add((location[0], location[1]), 1)
                else:
                    break
            else:
                break
        return number_placed > 0
                    
    def place_unit_random_edge(self, unit_type, num=1):
        number_placed = 0
        while number_placed < num:
            if self.game_state.number_affordable(unit_type) > 0:
                location = random.choice(self.friendly_edge_locations)
                if self.game_state.can_spawn(unit_type, location):
                    self.game_state.attempt_spawn(unit_type, location)  
                    number_placed += 1
                else:
                    return
            else:
                return

    
    def all_valid_map_locations(self):
        all_locations = []
        for i in range(self.game_state.ARENA_SIZE):
            for j in range(self.game_state.ARENA_SIZE):
                if (self.game_state.game_map.in_arena_bounds([i, j])):
                    all_locations.append([i, j])
        return all_locations

    def my_side_valid_locations(self):
        locations = []
        for i in range(self.game_state.ARENA_SIZE):
            for j in range(self.game_state.HALF_ARENA):
                if (self.game_state.game_map.in_arena_bounds([i, j])):
                    locations.append([i, j])
        return locations
    
    def friendly_edge_locations(self):
        locations = self.game_state.game_map.get_edge_locations(self.game_state.game_map.BOTTOM_LEFT)
        locations += self.game_state.game_map.get_edge_locations(self.game_state.game_map.BOTTOM_RIGHT)
        return locations
    
    def print_map(self):
        unit_character = {
                PING: 'P',
                EMP: 'X',
                SCRAMBLER: 'S',
                FILTER: 'F',
                DESTRUCTOR: "D",
                ENCRYPTOR: "E"
                }
        my_health = int(self.game_state.my_health)
        enemy_health = int(self.game_state.enemy_health)
        self.debug_print("Goody: {}".format("*"*my_health))
        self.debug_print("Baddy: {}".format("*"*enemy_health))
        
        gm = self.game_state.game_map
        for j in range(self.game_state.ARENA_SIZE):
            row = ":"
            for i in range(self.game_state.ARENA_SIZE):
                x = i
                y = self.game_state.ARENA_SIZE - j - 1
                if not gm.in_arena_bounds([x, y]):
                    row += "  "
                    continue
                a = gm[x, y]
                if not a or len(a) == 0:
                    if self.enemy_path_hist.value((x, y)) > 0:
                        row += "_ " #"{} ".format(self.enemy_path_hist.value((x, y)))
                    else:
                        row += ". "
                else: 
                    character = unit_character[a[0].unit_type]
                    if a[0].player_index == 1:
                        character = character.lower()
                    row += character + " "
            self.debug_print(row)
    
    def register_new_unit(self, location, stability):
        x = location[0]
        y = location[1]
        if (x,y) in self.added_stability:
            self.added_stability[x, y] += stability
        else:
            self.added_stability[x, y] = stability
            
    def damage_sustained_at_loc(self, location):
        x = location[0]
        y = location[1]        
        if (x,y) in self.added_stability:
            unit_list = game_state.game_map[x, y]
            if len(unit_list) == 0:
                return self.added_stability[x, y]
            else:
                return self.added_stability[x, y] - unit_list[0].stability
        return 0

if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
