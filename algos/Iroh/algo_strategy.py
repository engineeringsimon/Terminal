import gamelib
import random
import math
import warnings
from sys import maxsize
from RandomStrategyData import RandomStrategyData

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
        self.name = "Iroh"
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
        self.debug_print('Performing turn {} of the {} strategy'.format(self.game_state.turn_number, self.name))
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
        
        # initialise the probabilities from the data file
        self.initialise_from_file()
    
    def initialise_from_file(self):
        self.strategy = RandomStrategyData(self.my_side, self.friendly_edge_locations, self.config)
        self.strategy.randomise()
    
    def execute_strategy(self):
        self.place_defenders()
        self.place_attackers()
        
    def place_defenders(self):
        for i in range(100):
            (location, unit_type) = self.strategy.choose_defence_move()
            if self.game_state.contains_stationary_unit(location):
                continue
            isOk = self.place_unit(unit_type, location)
            if not isOk:
                break
        
    def place_attackers(self):
        for i in range(100):
            (location, unit_type) = self.strategy.choose_attack_move()
            if self.game_state.contains_stationary_unit(location):
                continue
            isOk = self.place_unit(unit_type, location)
            if not isOk:
                break
       
        
    def place_unit(self, unit_type, location, num=1):
        number_placed = 0
        while number_placed < num:
            if self.game_state.number_affordable(unit_type) > 0:
                if self.game_state.can_spawn(unit_type, location):
                    self.game_state.attempt_spawn(unit_type, location)  
                    number_placed += 1
                else:
                    break
            else:
                break
        return number_placed > 0
        
    def mirror(self, loc):
        x = loc[0]
        y = loc[1]
        mirror_x = self.game_state.game_map.ARENA_SIZE - 1 - x
        return [mirror_x, y]
        
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
        n = self.game_state.ARENA_SIZE
        for j in range(n):
            row = "|    "
            for i in range(n):
                x = i
                y = n - j - 1
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
