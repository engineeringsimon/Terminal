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
   
desired_layout = advance_wall_layout   

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        random.seed()
        self.turn_count = 0
        self.name = "JongJong"
        self.all_arena_locations = []
        self.my_side_locations = []
        self.placed_units = []
        self.added_stability = {}
        self.num_encryp_plus_destruct = 0

    def on_game_start(self, config):
        """ 
        Read in config and perform any initial setup here 
        """
        gamelib.debug_write('Configuring {}...'.format(self.name))
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
                'E': ENCRYPTOR
                }
        self.desired_layout_string = desired_layout
        
    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        self.placed_units = []
        self.game_state = gamelib.AdvancedGameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of the {} strategy'.format(self.game_state.turn_number, 
                                self.name))
        #game_state.suppress_warnings(True)  #Uncomment this line to suppress warnings.

        if (self.game_state.turn_number == 0):
            self.execute_first_turn()
        
        self.execute_strategy()

        self.print_map()
        
        self.game_state.submit_turn()

        
    def execute_first_turn(self):
        self.all_arena_locations = self.all_valid_map_locations()
        self.my_side_locations = self.my_side_valid_locations()
        self.friendly_edge_locations = self.friendly_edge_locations()
       
        self.gap_path = []
#        for i in range(2, game_state.ARENA_SIZE):
#            for j in range(game_state.HALF_ARENA):
#                if not game_state.game_map.in_arena_bounds([i,j]):
#                    continue
#                elif (i + j) <= game_state.HALF_ARENA:
#                    self.gap_path.append([i,j])
#                elif (i - j) >= (game_state.HALF_ARENA - 1):
#                    self.gap_path.append([i,j])
#            
        self.desired_filter_locations = [x for x in self.friendly_edge_locations if x[1] > 2]
        
#        for i in range(game_state.ARENA_SIZE):
#            location = [i, game_state.HALF_ARENA - 1 - max([0, min([i-3, 3, game_state.ARENA_SIZE - 4 - i])])]
#            if location not in self.gap_path:
#                self.desired_filter_locations.append(location)
#        self.desired_filter_locations.reverse()
#        
#        self.emp_start_location = [13,0]
#        self.desired_destroyer_locations = [[x[0], x[1] - 1] 
#                            for x in self.desired_filter_locations 
#                            if game_state.game_map.in_arena_bounds([x[0], x[1] - 1])]
#        
        self.my_side = []
        for i in range(self.game_state.ARENA_SIZE):
            for j in range(self.game_state.HALF_ARENA):
                location = [i,j]
                if self.game_state.game_map.in_arena_bounds(location):
                    self.my_side.append(location)
        # Make a lookup of all the points within 3.5 of each point and put them in a dictionary
        
        self.destructor_range_points = {}
        for i in range(self.game_state.ARENA_SIZE):
            for j in range(self.game_state.ARENA_SIZE):
                location = [i,j]
                if self.game_state.game_map.in_arena_bounds(location):
                    self.destructor_range_points[i, j] = self.game_state.game_map.get_locations_in_range(location, 3.5)
        
        i = 0
        lines = self.desired_layout_string.split("\n")[1:]
        for line in lines:
            gamelib.debug_write("{}: {}".format(i, line))
            i += 1
        self.desired_layout = {}
        for loc in self.my_side:
            x = loc[0]
            y = loc[1]
            character = lines[self.game_state.HALF_ARENA - 1 - y][x]
            if character in self.my_unit_code:
                self.desired_layout[x, y] = self.my_unit_code[character]
            
        
    def execute_strategy(self):
        self.build_defences()
    
        loc = self.random_available_edge()
        self.place_unit(EMP, loc, 4)
        self.place_unit(SCRAMBLER, loc, 100)
        
    def random_available_edge(self):
        locations = [x for x in self.friendly_edge_locations if not self.game_state.contains_stationary_unit(x)]
        return random.choice(locations)
        
    def build_defences(self):
        locations = [loc for loc in self.desired_layout if not self.game_state.contains_stationary_unit(loc)]
        random.shuffle(locations)
        locations.sort(key=lambda x: x[1], reverse=True)
        for loc in locations:
            isOk = self.place_unit(self.desired_layout[loc[0], loc[1]], loc)
            if not isOk: 
                break            
        
    # def place_destructors_on_enemy_paths(self):
        # self.enemy_path_point_dist = self.get_all_enemy_path_points(self.game_state)
        # possible_destructor_loc = [(x[0], x[1]) for x in self.my_side if not self.game_state.contains_stationary_unit(x)]
        # # existing_destructor_loc = [(x[0], x[1]) for x in self.my_side if self.is_destructor_at_loc(x)]
        # # existing_destructor_coverage = 0
        # # for (x, y) in existing_destructor_loc:
            # # for loc in self.destructor_range_points[x, y]
                # # existing_destructor_coverage += self.enemy_path_point_dist.value(loc)
        # possible_destructor_coverage = []
        # for loc in possible_destructor_loc:
            # coverage = 0
            # for covered_point in self.destructor_range_points[loc]:
                # coverage += self.enemy_path_point_dist.value(loc)
            # possible_destructor_coverage.append((loc, coverage))
        # possible_destructor_coverage.sort(key=lambda x: x[1], reverse=True)
        
        # for (loc, count) in possible_destructor_coverage:
            # isOk = self.place_unit(DESTRUCTOR, loc)
            # if not isOk: 
                # break
    
        
    def is_destructor_at_loc(self, loc):
        units = self.game_state.game_map[x[0], x[1]]
        if len(units) == 0:
            return False
        unit = units[0]
        return unit.unit_type == DESTRUCTOR
    # def super_slow_strategy(self):
        # work out all possible paths of enemy dudes attacking us
        # baseline_state = copy.deepcopy(self.game_state)
        # baseline_effectiveness = self.defensive_effectiveness(baseline_state)
        # gamelib.debug_write("Sum of attacks = {}".format(baseline_effectiveness))
    
        # empty_points = [x for x in self.my_side if x[1] > 10 and not baseline_state.contains_stationary_unit(x)]
        # destructor_eff = {}
        # for loc in empty_points:
            # temp_game_state = copy.deepcopy(self.game_state)
            # temp_game_state.game_map.add_unit(DESTRUCTOR, loc, 0)
            # x = loc[0]
            # y = loc[1]
            # destructor_eff[x, y] = self.defensive_effectiveness(temp_game_state)
        
        # best_destructor_loc = max(destructor_eff, key=lambda i: destructor_eff[i])
        # gamelib.debug_write("Best point = {} with effectiveness = {}".format(best_destructor_loc, destructor_eff[best_destructor_loc]))
        
        
    # def defensive_effectiveness(self, temp_game_state):
        # self.enemy_path_point_dist = self.get_all_enemy_path_points(temp_game_state)
        
        # calculate how many of these points are currently attacked by destructors
        # path_point_info = {}
        # sum_of_attacks = 0
        # for ((x, y), count) in self.enemy_path_point_dist.items():
            # attacking_destructors = temp_game_state.get_attackers([x, y], 1) # number of attackers of the enemy
            # num_attackers = len(attacking_destructors)
            # path_point_info[x, y] = (count, num_attackers)
            # sum_of_attacks += count * num_attackers
        # return sum_of_attacks
        
    def get_all_enemy_path_points(self, temp_game_state):
        gm = temp_game_state.game_map
        
        # starting location, end edge
        path_ids = [(start_loc, gm.BOTTOM_LEFT) 
                        for start_loc in gm.get_edge_locations(gm.TOP_RIGHT) 
                        if not temp_game_state.contains_stationary_unit(start_loc)]
        path_ids += [(start_loc, gm.BOTTOM_RIGHT) 
                        for start_loc in gm.get_edge_locations(gm.TOP_LEFT) 
                        if not temp_game_state.contains_stationary_unit(start_loc)]
        
        paths = [temp_game_state.find_path_to_edge(start_loc, target_edge) for (start_loc, target_edge) in path_ids]
        points = []
        for x in paths:
            points += x
        # points is a list of 2 element lists
        # now to convert this to a dictionary with the coordinate as key (x, y)
        # and the number of instances in the paths as the value
        
        point_dist = PointHistogram()
        for loc in points:
            point_dist.add((loc[0], loc[1]), 1)
                   
        #gamelib.debug_write("{} points reduce to {} unique points.".format(len(points), len(point_dist)))
        return point_dist
        
    def place_defence_unit(self, unit_type, location, num=1):
        number_placed = 0
        while number_placed < num:
            if self.game_state.number_affordable(unit_type) > 0:
                if self.game_state.can_spawn(unit_type, location) and location not in self.gap_path:
                    self.game_state.attempt_spawn(unit_type, location)  
                    self.register_new_unit(location, self.stability[unit_type])
                    number_placed += 1
                else:
                    return number_placed > 0
            else:
                return number_placed > 0
        return number_placed > 0
            
    def place_unit(self, unit_type, location, num=1):
        number_placed = 0
        while number_placed < num:
            if self.game_state.number_affordable(unit_type) > 0:
                if self.game_state.can_spawn(unit_type, location):
                    self.game_state.attempt_spawn(unit_type, location)  
                    number_placed += 1
                    self.placed_units.append(location)
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
        
    def build_filters(self):
        for loc in self.desired_filter_locations:
            self.place_defence_unit(FILTER, loc)
        
    def build_destructors(self):
        for i in range(3):
            if (self.num_encryp_plus_destruct % 3) == 2:
                loc = self.calculate_best_encryptor_loc()
                #gamelib.debug_write("Encryptor => {}".format(loc))
                isOk = self.place_defence_unit(ENCRYPTOR, loc)
            else:
                loc = self.calculate_best_destructor_loc()
                #gamelib.debug_write("Destructor => {}".format(loc))
                isOk = self.place_defence_unit(DESTRUCTOR, loc)
                
            if isOk:
                self.placed_units.append(loc)
                self.num_encryp_plus_destruct += 1
            else:
                break
            
    def calculate_best_destructor_loc(self):
        potential_locations = [(x, self.destructor_goodness(x)) 
                                for x in self.my_side 
                                if not self.game_state.contains_stationary_unit(x) 
                                        and x not in self.gap_path
                                        and x not in self.placed_units]
        potential_locations.sort(key=lambda x: x[1], reverse=True)
        (loc, goodness) = potential_locations[0]
        return loc

    def calculate_best_encryptor_loc(self):
        potential_locations = [(x, self.encryptor_goodness(x)) 
                                for x in self.my_side 
                                if not self.game_state.contains_stationary_unit(x) 
                                        and x not in self.gap_path
                                        and x not in self.placed_units]
        potential_locations.sort(key=lambda x: x[1], reverse=True)
        (loc, goodness) = potential_locations[0]
        return loc
    
    def encryptor_goodness(self, location):
        x = location[0]
        y = location[1]
        
        FRONT = 0
        RIGHT = 1
        TOO_CLOSE = 2
        GAP_PATH = 3
        NO_GAP = 4
        ENEMY_DAMAGE = 5
        
        ws ={
                FRONT: 1,
                RIGHT: 1,
                TOO_CLOSE: 0,
                GAP_PATH: 1,
                NO_GAP: 1,
                ENEMY_DAMAGE: 0
                }
        
        front = y
        right = x
        
        too_close = 0
        
        filters_above = [1 for a in self.desired_filter_locations if a[0] == x and a[1] > y ]
        
        if len(filters_above):
            too_close = -1
        
        
        # get all the points within range of this destructor
        loc_in_range = self.game_state.game_map.get_locations_in_range(location, 3.5)
        num_gap_path_covered = len([1 for x in loc_in_range if x in self.gap_path])
        
        no_gap_penalty = 0
        if num_gap_path_covered == 0:
            no_gap_penalty = -1

        nearby_units =[]
        for x in loc_in_range:
            nearby_units += self.game_state.game_map[x[0], x[1]]
#        
#        friendly_damages = [x.max_stability - x.stability for x in nearby_units if x.player_index == 0]
        enemy_damages = [x.max_stability - x.stability for x in nearby_units if x.player_index == 1]
#        
#        num_friendly = len(friendly_damages)
#        num_enemy = len(enemy_damages)
        
        goodness =   ( ws[FRONT] * front 
                    + ws[RIGHT] * right 
                    + ws[TOO_CLOSE] * too_close 
                    + ws[GAP_PATH] * num_gap_path_covered 
                    + ws[ENEMY_DAMAGE] * sum(enemy_damages) 
                    + ws[NO_GAP] * no_gap_penalty
                    )
        
        #gamelib.debug_write("{}: {} + {} - {} = {}".format(location, front, too_close, num_attackers, goodness))
        return goodness

    def destructor_goodness(self, location):
        x = location[0]
        y = location[1]
        
        FRONT = 0
        TOO_CLOSE = 1
        ALREADY_COVERED = 2
        FRIENDLY_DAMAGE = 3
        ENEMY_DAMAGE = 4
        NUM_FRIENDLY = 5
        
        ws = {
                FRONT: 1, 
                TOO_CLOSE: 0, 
                ALREADY_COVERED: 8, 
                FRIENDLY_DAMAGE: 10, 
                ENEMY_DAMAGE: 0, 
                NUM_FRIENDLY: 0
                }
        
        front = y
        
        too_close = 1
        
        filters_above = [1 for a in self.desired_filter_locations if a[0] == x and a[1] > y ]
        
        if len(filters_above) == 0:
            too_close = -1       
        
        # get all the points within range of this destructor
        loc_in_range = self.game_state.game_map.get_locations_in_range(location, 3.5)
        num_attackers = sum([len(self.game_state.get_attackers(x, 1)) for x in loc_in_range])

        nearby_units = []
        for x in loc_in_range:
            nearby_units += self.game_state.game_map[x[0], x[1]]
        
        friendly_damages = [self.damage_sustained_at_loc(self.game_state, x) for x in loc_in_range]
        enemy_damages = [x.max_stability - x.stability for x in nearby_units if x.player_index == 1]
        
        num_friendly = len(friendly_damages)
        num_enemy = len(enemy_damages)
        
        goodness = (  ws[FRONT]           * front 
                    + ws[TOO_CLOSE]       * too_close 
                    - ws[ALREADY_COVERED] * num_attackers 
                    + ws[NUM_FRIENDLY]    * num_friendly 
                    + ws[FRIENDLY_DAMAGE] * sum(friendly_damages)
                    + ws[ENEMY_DAMAGE]    * sum(enemy_damages)
                    )
        
        #gamelib.debug_write("{}: fd{}, nf{}, g{}".format(location, sum(friendly_damages), num_friendly, goodness))
        return goodness
    
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
        
        gm = self.game_state.game_map
        for j in range(self.game_state.ARENA_SIZE):
            row = ":"
            for i in range(self.game_state.ARENA_SIZE):
                if not gm.in_arena_bounds([i,j]):
                    row += "  "
                    continue
                a = gm[i, self.game_state.ARENA_SIZE - j - 1]
                if not a or len(a) == 0:
                    row += ". "
                else: 
                    character = unit_character[a[0].unit_type]
                    if a[0].player_index == 1:
                        character = character.lower()
                    row += character + " "
            gamelib.debug_write(row)
    
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
