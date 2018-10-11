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


   
desired_layout = venus_flytrap_layout   

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        random.seed()
        self.turn_count = 0
        self.name = "Paku"
        self.all_arena_locations = []

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
                'E': ENCRYPTOR,
                'X': EMP,
                'P': PING,
                'S': SCRAMBLER
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
        for i in range(self.game_state.ARENA_SIZE):
            for j in range(self.game_state.ARENA_SIZE):
                location = [i,j]
                if self.game_state.game_map.in_arena_bounds(location):
                    self.destructor_range_points[i, j] = self.game_state.game_map.get_locations_in_range(location, 3.5)

        # covert layout string to layout
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
        self.place_attackers()
    
    def place_attackers(self):
        loc = self.choose_attacking_position() #self.random_available_edge()
        # work out destination of this location
        destination = self.calc_destination(loc)
        
        # calc path
        path = self.game_state.find_path_to_edge(loc, destination)
        #gamelib.debug_write("Path = {}".format(path))
        enemy_edges = self.game_state.game_map.get_edge_locations(self.game_state.game_map.TOP_RIGHT) + self.game_state.game_map.get_edge_locations(self.game_state.game_map.TOP_LEFT)
        is_successful = path[-1] in enemy_edges
        gamelib.debug_write("Successful path = {}, end = {}".format(is_successful, path[-1]))
        
        # calc damage from enemy near path
        # collect all the destructor that are enemies
        enemy_destructor_locations = self.enemy_destructor_locations()
        num_in_range_points = 0
        for location in enemy_destructor_locations:
            x = location[0]
            y = location[1]
            for a in self.destructor_range_points[x, y]:
                if a in path:
                    num_in_range_points += 1
        gamelib.debug_write("In Range = {}".format(num_in_range_points))
        
        if num_in_range_points <= 2 and is_successful:
            self.place_unit(PING, loc, 100)
            gamelib.debug_write("PING!")
        else:
            self.place_unit(EMP, loc, 100)
            gamelib.debug_write("EMP!")
        
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
        return self.game_state.game_map.TOP_LEFT
        
    def choose_attacking_position(self):
        locations = [loc for loc in self.desired_layout if self.desired_layout[loc] in [EMP, SCRAMBLER, PING]]
        if len(locations) == 0:
            return [13, 0]
        (x, y) = random.choice(locations)
        gamelib.debug_write("choosing {}, from {}".format((x,y), locations))
        return [x, y]
            
        
    def old_place_attackers(self):
        # enumerate all the attacking paths
        bottom_left = [(x[0], x[1]) 
                        for x in self.game_state.game_map.get_edge_locations(self.game_state.game_map.BOTTOM_LEFT) 
                        if not self.game_state.contains_stationary_unit(x)]
        bottom_right = [(x[0], x[1]) 
                        for x in self.game_state.game_map.get_edge_locations(self.game_state.game_map.BOTTOM_RIGHT) 
                        if not self.game_state.contains_stationary_unit(x)]
        bottom_left_paths = [self.game_state.find_path_to_edge(x, self.game_state.game_map.TOP_RIGHT)
                                for x in bottom_left]
        bottom_right_paths = [self.game_state.find_path_to_edge(x, self.game_state.game_map.TOP_LEFT)
                                for x in bottom_right]
        successful_paths = [x for x in bottom_left_paths 
                            if x[-1] in self.game_state.game_map.get_edge_locations(self.game_state.game_map.TOP_RIGHT)]   
        successful_paths += [x for x in bottom_right_paths 
                            if x[-1] in self.game_state.game_map.get_edge_locations(self.game_state.game_map.TOP_LEFT)]
                                  
        # now work out which of the successful paths has the least destructor involvement
        
        
    def random_available_edge(self):
        locations = [x for x in self.friendly_edge_locations if not self.game_state.contains_stationary_unit(x)]
        return random.choice(locations)
        
    def build_defences(self):
        locations = [loc for loc in self.desired_layout if not self.game_state.contains_stationary_unit(loc)]
        random.shuffle(locations)
        locations.sort(key=lambda x: x[1], reverse=True)
        for loc in locations:
            unit_id = self.desired_layout[loc[0], loc[1]]
            if unit_id in [DESTRUCTOR, FILTER, ENCRYPTOR]:                    
                isOk = self.place_unit(self.desired_layout[loc[0], loc[1]], loc)
                if not isOk: 
                    break            
    
        
    def is_destructor_at_loc(self, loc):
        units = self.game_state.game_map[loc[0], loc[1]]
        if units == None or len(units) == 0:
            return False
        unit = units[0]
        return unit.unit_type == DESTRUCTOR
        
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
