import gamelib

class ReducedGameState:
    def __init__(self, game_state):
        self.map = game_state.game_map
        self.my_health = game_state.my_health
        self.enemy_health = game_state.enemy_health
        self.my_cores = game_state.get_resource(game_state.CORES, 0)
        self.enemy_cores = game_state.get_resource(game_state.CORES, 1)
        self.my_bits = game_state.get_resource(game_state.BITS, 0)
        self.enemy_bits = game_state.get_resource(game_state.BITS, 1)
        
    def float_array(self):
        return [0.0, 0.0]