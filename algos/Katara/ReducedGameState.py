ARENA_SIZE = 28
HALF_ARENA = 14
FILTER = "FF"
ENCRYPTOR = "EF"
DESTRUCTOR = "DF"
PING = "PI"
EMP = "EI"
SCRAMBLER = "SI"

def in_arena_bounds(x, y):
    a = x + y
    b = y - x
    if a < 13:
        return False
    if a > 41:
        return False
    if b > 14:
        return False
    if b < -14:
        return False
    return True

def bar_graph_array(value, max_value):
    array = []
    for i in range(max_value):
        if value >= i:
            array.append(1.0)
        else:
            array.append(0.0)
    return array
    
def input_size():
    i = 0
    for x in range(ARENA_SIZE):
        for y in range(ARENA_SIZE):
            if in_arena_bounds(x, y):
                i += 3
                    
    # now for my health
    i += 30
    i += 30
    
    # bits
    i += 30
    i += 30
    
    # cores
    i += 50
    i += 50
   
    return i


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
        # for each field point Destructor, Encryptor, Filter
        # health like a bar chart 1100000 is 2, 1110000 is 3
        # same with cores and bits
        
        array = []
        
        for x in range(ARENA_SIZE):
            for y in range(ARENA_SIZE):
                if in_arena_bounds(x, y):
                    units = self.map[x, y]
                    if units and len(units) > 0:
                        unit = units[0]
                        if unit.unit_type == DESTRUCTOR:
                            array.append(1.0)
                        else: 
                            array.append(0.0)
                            
                        if unit.unit_type == ENCRYPTOR:
                            array.append(1.0)
                        else: 
                            array.append(0.0)
                        
                        if unit.unit_type == FILTER:
                            array.append(1.0)
                        else: 
                            array.append(0.0)
                    else:
                        array += [0.0, 0.0, 0.0]
                        
        # now for my health
        array += bar_graph_array(self.my_health, 30)
        array += bar_graph_array(self.enemy_health, 30)
        
        # bits
        array += bar_graph_array(self.my_bits, 30)
        array += bar_graph_array(self.enemy_bits, 30)
        
        # cores
        array += bar_graph_array(self.my_cores, 50)
        array += bar_graph_array(self.enemy_cores, 50)
        
        return array
        
    def input_size(self):
        return len(self.float_array())