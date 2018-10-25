import gamelib
import random
import math
import warnings
from sys import maxsize
import KataraStrategyData

from ReducedGameState import *

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

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        random.seed()
        self.turn_count = 0
        self.name = "Katara"
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

        self.strategy = KataraStrategyData.Make(self.my_side, self.friendly_edge_locations)
       
    def execute_strategy(self):
        for i in range(100):
            # Get Game State: Map, health of both, resources of both, round that we are up to
            state = ReducedGameState(self.game_state)
            if state.my_cores < 1.0:
                break
                
            # Pass to strategy and get moves
            defence_move = self.strategy.next_defence_move(state)
            
            # execute moves
            if defence_move:
                self.execute_defence_move(defence_move)
            else:
                break
        
        for i in range(100):
            # Get Game State: Map, health of both, resources of both, round that we are up to
            state = ReducedGameState(self.game_state)
            if state.my_bits < 1.0:
                break
                
            # Pass to strategy and get moves
            attack_move = self.strategy.next_attack_move(state)
            
            # execute moves
            if attack_move:
                self.execute_attack_move(attack_move)
            else:
                break
    
    def execute_defence_move(self, move):
        # move in format (unit_type, (x, y))
        pass
        
    def execute_attack_move(self, move):
        # move in format (unit_type, (x, y))
        pass
     
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
        self.debug_print("Goody: {} {}".format("*"*my_health, my_health))
        self.debug_print("Baddy: {} {}".format("*"*enemy_health, enemy_health))
        
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
                    row += ". "
                else: 
                    character = unit_character[a[0].unit_type]
                    if a[0].player_index == 1:
                        character = character.lower()
                    row += character + " "
            self.debug_print(row)

if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
