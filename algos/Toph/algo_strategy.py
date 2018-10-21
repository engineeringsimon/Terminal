import gamelib
import random
import math
import warnings
from sys import maxsize
import TophStrategyData

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

blank_layout = '''
............................
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


# Bumi3
adaptive_wall_layout = '''
F..........................F
 F........................F 
  F......................F 
   FFFFFFFFFFFFFFFFFFFFFF
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

# Dumber wall
dumber_wall_layout = '''
............................
 .......................... 
  ........................ 
   ......................
    FFFFFFFFFFFFFFFFFFFF 
     ..E............E.. 
      ................ 
       .............. 
        ............ 
         .......... 
          ........ 
           ...... 
            .... 
             .. 
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

   
desired_layout = dumb_wall_layout   

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        random.seed()
        self.turn_count = 0
        self.name = "Toph"
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

        self.gap = []

        self.enemy_edges = self.game_state.game_map.get_edge_locations(self.game_state.game_map.TOP_RIGHT) + self.game_state.game_map.get_edge_locations(self.game_state.game_map.TOP_LEFT)
            
        # initialise the test attack paths
        # a test attack path is a combination of launch location (one for left other for right)
        # (launch location, [list of points on path]) i.e. ([x,y], [[x0,y0], [x1,y1], ... , [xn, yn]])
        self.attack_paths = []
        # left to right
        # for a in [0..26]
        self.left_attack_launch_loc = [4, 9]
        self.right_attack_launch_loc = self.mirror(self.left_attack_launch_loc)
        for a in [0, 5, 10, 16, 22, 27]:
            l_r_path = self.left_to_right_attack_path(a)
            r_l_path = self.right_to_left_attack_path(a)
            self.attack_paths.append((self.left_attack_launch_loc, l_r_path))
            self.attack_paths.append((self.right_attack_launch_loc, r_l_path))
            
        self.best_attack_index_log = []
        self.num_destructors_placed = 0
        self.num_encrytors_placed = 0
        self.strategy = TophStrategyData.Make(self.my_side, self.friendly_edge_locations)
        self.desired_layout = self.strategy.desired_layout
        
    def left_to_right_attack_path(self, offset):
        line0 = [(x, x - 13 + offset) for x in range(self.game_state.game_map.ARENA_SIZE)]
        line1 = [(x, x - 14 + offset) for x in range(self.game_state.game_map.ARENA_SIZE)]
        lines = line0 + line1
        path = [(x, y) for (x, y) in lines if (x + y) >= 13 and (x + y) <= 41]
        return path
            
    def right_to_left_attack_path(self, offset):
        line0 = [(x, 13 + offset - x) for x in range(self.game_state.game_map.ARENA_SIZE)]
        line1 = [(x, 14 + offset - x) for x in range(self.game_state.game_map.ARENA_SIZE)]
        lines = line0 + line1
        path = [(x, y) for (x, y) in lines if (y - x) >= -14 and (y - x) <= 14]
        return path
            
        
    def mirror(self, loc):
        x = loc[0]
        y = loc[1]
        mirror_x = self.game_state.game_map.ARENA_SIZE - 1 - x
        return [mirror_x, y]
        
    def execute_strategy(self):
        self.update_field_calcs()
        self.update_gap_from_attack_paths()
        self.remove_gap_defenses()
        self.build_defences()
        
        if self.num_encrytors_placed * 1 >= self.num_destructors_placed:
            self.place_destructors(100)
            self.place_attackers()
        else:
            launch_loc = self.place_attackers()
            self.place_encryptors(launch_loc, 100)
        
    
    def remove_gap_defenses(self):
        for loc in self.gap:
            x = loc[0]
            y = loc[1]
            if y >= self.game_state.game_map.HALF_ARENA:
                continue
            if self.game_state.contains_stationary_unit(loc):
                self.game_state.attempt_remove(loc)
    
    def update_gap_from_attack_paths(self):
        (start_loc, attack_path) = self.attack_paths[self.min_attack_path_index]
        self.gap = [[x, y] for (x, y) in attack_path]
        
        
    def update_field_calcs(self):
        self.update_destructor_coverage()
        self.update_enemy_paths()
        self.update_friendly_paths()
        self.update_enemy_emp_coverage()
        self.update_attack_path_damage()
        
    def update_attack_path_damage(self):
        self.attack_path_damage = {}
        n = len(self.attack_paths)
        for i in range(n):
            (launch_loc, path) = self.attack_paths[i]
            (damage_in_range, is_successful) = self.eval_friendly_path(path)
            self.attack_path_damage[i] = damage_in_range
            
        self.best_attack_index_log.append(min(self.attack_path_damage, key=lambda i: self.attack_path_damage[i]))
        if len(self.best_attack_index_log) < 3:
            self.min_attack_path_index = self.best_attack_index_log[-1]
        elif self.best_attack_index_log[-1] == self.best_attack_index_log[-2]:# and self.best_attack_index_log[-1] == self.best_attack_index_log[-3]:
            self.min_attack_path_index = self.best_attack_index_log[-1] # change if the last 3 were the same
            
        self.debug_print("Attack Damage = {}".format(self.attack_path_damage))
        
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
    
    def place_destructors(self, max_num=100):
        potential_locations = self.enemy_path_hist.sorted_keys()
        destructor_points = [x for x in self.my_side 
                                if [x[0], x[1]] not in self.gap 
                                    and x[1] >= 7 
                                    and not self.game_state.contains_stationary_unit(x)]
                                    
        coverage = [(loc, self.coverage_of(self.enemy_path_hist, loc)) for loc in destructor_points]
        coverage.sort(key=lambda x: x[1], reverse=True)
        count = 0
        for (loc, coverage) in coverage:
            if self.game_state.contains_stationary_unit(loc):
                continue
            isOk = self.place_unit(DESTRUCTOR, loc)
            if not isOk:
                break
            self.num_destructors_placed += 1
            count += 1
            if count >= max_num:
                break
                
    def coverage_of(self, histogram, loc):
        x = loc[0]
        y = loc[1]
        covered_points = self.destructor_range_points[x, y]
        sum = 0
        for point in covered_points:
            px = point[0]
            py = point[1]
            sum += histogram.value((px, py))
        return sum
        
    def place_encryptors(self, launch_loc, max_num=100):
        num_placed = 0
        potential_paths = [path for path in self.friendly_paths if launch_loc in path]
        if len(potential_paths) == 0:
            self.place_destructors()
            return
        path = potential_paths[0]
        
        # choose rows 8 and 9
        potential_locations = [loc for loc in self.my_side 
                                    if loc[1] <= 9 
                                        and loc not in self.gap 
                                        and loc not in path]
                                        
        evaluated_points = []                                        
        
        for loc in potential_locations:
            if self.game_state.contains_stationary_unit(loc):
                continue
            x = loc[0]
            y = loc[1]
            # calc coverage of encryptor at loc for the path points
            covered_points = self.destructor_range_points[x, y]
            covered_path_points = [loc for loc in path if loc in covered_points]
            evaluated_points.append((loc, len(covered_path_points)))
            
        evaluated_points.sort(key=lambda x: x[1] + x[0][1]*0.01, reverse=True)
        for loc, num_covered in evaluated_points:
            isOk = self.place_unit(ENCRYPTOR, loc)
            if not isOk:
                break    
            num_placed += 1
            self.num_encrytors_placed += 1
            if num_placed >= max_num:
                break
    
    def eval_friendly_path(self, path):
        damage_in_range = 0
        for loc in path:
            damage_in_range += self.enemy_destructor_coverage.value((loc[0], loc[1])) * 75
            unit = self.game_state.contains_stationary_unit(loc)
            if not unit: 
                continue
            if unit.unit_type == ENCRYPTOR or unit.unit_type == FILTER:
                damage_in_range += unit.stability

        is_successful = path[-1] in self.enemy_edges
        return (damage_in_range, is_successful)
        
    def place_attackers(self):
        # my_health = self.game_state.my_health
        # enemy_health = self.game_state.enemy_health
        # if (my_health < 20.0 and enemy_health > my_health) or (enemy_health - my_health) > 6.0:
            # self.tweaked_place_attackers()
            # return
            
        (start_loc, attack_path) = self.attack_paths[self.min_attack_path_index]
        damage_in_range = self.attack_path_damage[self.min_attack_path_index]
        num_affordable_emp = self.game_state.number_affordable(EMP)
        
        edge_points = [[x, y] for (x, y) in attack_path if [x, y] in self.friendly_edge_locations]
        #if len(edge_points) > 0:
        attack_start = min(edge_points, key=lambda loc: abs(start_loc[0] - loc[0]) + abs(start_loc[1] - loc[1]))
        #else:
        #    attack_start = start_loc
        
        self.debug_print("Damage in Range = {}".format(damage_in_range))
        
        self.place_unit(EMP, attack_start, 100)
        
        # if damage_in_range <= 100:
            # self.place_unit(PING, attack_start, 100)
        # elif damage_in_range < 1000 and num_affordable_emp >= 2:
            # self.place_unit(EMP, attack_start, 100)
        # elif damage_in_range < 2000 and num_affordable_emp >= 4:
            # self.place_unit(EMP, attack_start, 100)
        # elif num_affordable_emp >= 5:
            # self.place_unit(EMP, attack_start, 100)
            
        return attack_start
        
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
        return [x, y]

    def available_launch_locations(self):
        return [x for x in self.friendly_edge_locations if not self.game_state.contains_stationary_unit(x)]
        
    def random_available_edge(self):
        locations = self.available_launch_locations()
        return random.choice(locations)
        
    def build_defences(self):
        locations = [(x, y) for (x, y) in self.desired_layout 
                         if not self.game_state.contains_stationary_unit([x, y]) 
                            and [x, y] not in self.gap]
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
                    # num_attack_paths = len(self.attack_paths)
                    # path_index = self.game_state.turn_number % num_attack_paths
                    (start_loc, attack_path) = self.attack_paths[self.min_attack_path_index]
                    if (x, y) in attack_path:
                        row += "a "
                    elif self.enemy_destructor_coverage.value((x, y)) > 0:
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
