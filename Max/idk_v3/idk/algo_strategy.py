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

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        random.seed()

    def on_game_start(self, config):
        """ 
        Read in config and perform any initial setup here 
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global FILTER, ENCRYPTOR, DESTRUCTOR, PING, EMP, SCRAMBLER
        FILTER = config["unitInformation"][0]["shorthand"]
        ENCRYPTOR = config["unitInformation"][1]["shorthand"]
        DESTRUCTOR = config["unitInformation"][2]["shorthand"]
        PING = config["unitInformation"][3]["shorthand"]
        EMP = config["unitInformation"][4]["shorthand"]
        SCRAMBLER = config["unitInformation"][5]["shorthand"]
        self.last_attacker = EMP
		
    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        #game_state.suppress_warnings(True)  #Uncomment this line to suppress warnings.

        self.Maxs_strategy(game_state)

        game_state.submit_turn()

    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safey be replaced for your custom algo.
    """
    def Maxs_strategy(self, game_state):
        """
        Build the C1 logo. Calling this method first prioritises
        resources to build and repair the logo before spending them 
        on anything else.
        """
        self.Build_Walls(game_state)
        self.build_defences(game_state)
        self.deploy_attackers(game_state)
        self.Build_more_walls(game_state)
        self.build_more_defences(game_state)
        self.build_enc(game_state)
		
		
		

    def Build_Walls(self, game_state):
        firewall_locations = [[0,13 ], [1, 13], [2,13], [9, 10], [10, 10], [11, 10], [16, 10], [16,10],[17,10], [18,10], [25,13], [26,13], [27,13]]
        for location in firewall_locations:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)
          
        firewall_locations = [[2, 12], [10, 9], [17, 9], [25,12]]
        for location in firewall_locations:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)

    def build_defences(self, game_state):
        firewall_locations = [[8, 11], [19, 11]]
        for location in firewall_locations:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)


    def deploy_attackers(self, game_state):
        next_attacker = PING
        if self.last_attacker == PING:
            next_attacker = EMP
        while game_state.number_affordable(next_attacker) > 0:
            if game_state.can_spawn(next_attacker, [24, 10]):
                game_state.attempt_spawn(next_attacker, [24,10])
			
        self.last_attacker  = next_attacker

    def Build_more_walls(self, game_state):
        firewall_locations = [[7,12],[8,12],[9,12],[10,12],[11,12],[12,12],[13,12],[14,12],[15,12],[16,12],[17,12],[18,12],[19,12],[20,12],[21,12],[22,12],[23,12],[24,12],[6,12],[5,12],[4,12]]
        for location in firewall_locations:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)
	
    def build_more_defences (self, game_state):
            firewall_locations = [[7,11],[8,11],[9,11],[10,11],[11,11],[12,11],[13,11],[14,11],[15,11],[16,11],[17,11],[18,11],[19,11],[20,11],[21,11],[22,11],[23,11],[24,11],[6,11],[5,11],[1,12],[2,11],[3,10],[4,9],[5,8], [6, 7], [7, 6], [8, 5], [9, 4], [27, 13], [26, 12], [25, 11], [23, 9]]
            for location in firewall_locations:
                if game_state.can_spawn(DESTRUCTOR, location):
                    game_state.attempt_spawn(DESTRUCTOR, location)
                    
    def build_enc (self, game_state):
        firewall_locations = [[6, 10], [7, 10], [8, 10], [7, 9], [8, 9], [9, 9], [8, 8], [9, 8], [10, 8]]
        for location in firewall_locations:
            if game_state.can_spawn(ENCRYPTOR, location):
                game_state.attempt_spawn(ENCRYPTOR, location)    

if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
