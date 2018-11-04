import gamelib
import random
import math
import warnings
from sys import maxsize
import MyGameState as gs
from UnitPattern import UnitPattern

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

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        random.seed()
        self.turn_count = 0
        self.name = "Aang"
        self.is_printing_debug = True
        self.desired_unit_pattern = UnitPattern()

    def debug_print(self, str):
        if self.is_printing_debug:
            gamelib.debug_write(str)

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
        
        self.turn_count = 0

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        self.turn_count += 1
        
        self.game_state = gamelib.AdvancedGameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of the {} strategy'.format(self.game_state.turn_number, 
                                self.name))
        #game_state.suppress_warnings(True)  #Uncomment this line to suppress warnings.

        if (self.turn_count == 1):
            self.execute_first_turn()

        self.execute_strategy()

        self.print_map()
        self.game_state.submit_turn()
        
    def execute_first_turn(self):
        self.debug_print(self.desired_unit_pattern)
        
    def execute_strategy(self):
        self.place_defenders()
        self.place_unit(EMP, [1, 12], 4)
        self.place_unit(SCRAMBLER, [13,0], 100) 

    def place_defenders(self):
        sorted_unit_locations = self.desired_unit_pattern.unit_locations()
        for loc in sorted_unit_locations:
            if not self.game_state.contains_stationary_unit(loc):
                desired_unit_type = self.desired_unit_pattern.unit_type_at(loc)
                assert desired_unit_type
                isOk = self.place_single_unit(desired_unit_type, loc)
                if not isOk:
                    return

    def place_single_unit(self, unit_type, location):
        if self.game_state.number_affordable(unit_type) > 0:
            if self.game_state.can_spawn(unit_type, location):
                self.game_state.attempt_spawn(unit_type, location)  
                return True
        return False


            
    def place_unit(self, unit_type, location, num=1):
        number_placed = 0
        while number_placed < num:
            if self.game_state.number_affordable(unit_type) > 0:
                if self.game_state.can_spawn(unit_type, location):
                    self.game_state.attempt_spawn(unit_type, location)  
                    number_placed += 1
                else:
                    return
            else:
                return
            
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
