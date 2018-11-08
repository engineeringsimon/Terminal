# -*- coding: utf-8 -*-
"""
Created on Sun Nov  4 19:56:35 2018

@author: user
"""

import gamelib
import MyGameState as gs
import random
from UnitPattern import UnitPattern

class LookaheadStrategy:
    def __init__(self, algo):
        self.detected_enemy_spawns = {}
        self.latest_spawn_event = None
        self.algorithm = algo
        self.desired_unit_pattern = UnitPattern()
        
    def debug_print(self, s):
        self.algorithm.debug_print(s)
    
    def register_spawn(self, spawn_event):
        if spawn_event.player_id == 2 and spawn_event.is_attacker():
            key = (spawn_event.location, spawn_event.unit_type())
            if key in self.detected_enemy_spawns:
                self.detected_enemy_spawns[key] += 1
            else:
                self.detected_enemy_spawns[key] = 1
                    
            self.latest_spawn_event = spawn_event
            self.debug_print("{}: {}".format(spawn_event, self.detected_enemy_spawns[key]))

    def execute(self, game_state):
        self.game_state = game_state

        if (self.game_state.turn_number == 0):
            self._execute_first_turn()
        else:
            self._execute_strategy()
    
    def _execute_first_turn(self):
        self.debug_print(self.desired_unit_pattern)
        self.debug_print("Let's wait and see what the other player is going to do")
        
        # launch 5 random scramblers for fun
        launch_locations = random.sample(gs.my_edge_points, 5)
        for loc in launch_locations:
            self.place_single_unit(gs.SCRAMBLER, loc)
        
    
    def _execute_strategy(self):
        self.place_defenders_in_pattern()
        isOk = True
        while isOk:
            lower_edge_points = [(x,y) for (x,y) in gs.my_edge_points if y < 6]
            loc = random.choice(lower_edge_points)
            unit_type = random.choice([gs.PING, gs.EMP, gs.SCRAMBLER])
            isOk = self.place_single_unit(unit_type, loc)
        
        g = gs.GameState()
        g.init_from_game(self.game_state)
        self.debug_print(g)


    def place_defenders_in_pattern(self):
        locations = self.desired_unit_pattern.unit_locations()
        for (x, y) in locations:
            if not self.game_state.contains_stationary_unit([x, y]):
                unit_type = self.desired_unit_pattern.unit_type_at((x, y))
                self.debug_print(unit_type)
                isOk = self.place_single_unit(unit_type, (x, y))
                if not isOk:
                    return
        
    
    def place_single_unit(self, unit_type, location):
        (x, y) = location
        location = [x, y]
        #self.debug_print("Placing {} @ {}".format(unit_type, location))
        if self.game_state.number_affordable(unit_type) > 0:
            if self.game_state.can_spawn(unit_type, location):
                self.game_state.attempt_spawn(unit_type, location)  
                #self.debug_print("Ok")
                return True
            else:
                #self.debug_print("Can't spawn")
                pass
        else:
            #self.debug_print("Can't afford")
            pass
        #self.debug_print("Fail")
        return False
#            
#    def num_bits(self):
#        return self.game_state.get_resource(self.game_state.BITS)
#    
#    def num_cores(self):
#        return self.game_state.get_resource(self.game_state.CORES)
    