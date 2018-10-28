import ReducedGameState
import gamelib

ARENA_SIZE = 28
HALF_ARENA = 14
FILTER = "FF"
ENCRYPTOR = "EF"
DESTRUCTOR = "DF"
PING = "PI"
EMP = "EI"
SCRAMBLER = "SI"

        
def output_size():
    i = 0
    for x in range(ARENA_SIZE):
        for y in range(HALF_ARENA):
            if ReducedGameState.in_arena_bounds(x, y):
                i += 3
    i += 3 * ARENA_SIZE
    return i

class OutputState:
    def __init__(self, output_array):
        self.size = output_size()
        assert(len(output_array) >= self.size)
        
        i = 0
        self.defence_moves = []
        for x in range(ARENA_SIZE):
            for y in range(HALF_ARENA):
                if ReducedGameState.in_arena_bounds(x, y):
                    move = (DESTRUCTOR, (x, y), output_array[i])
                    self.defence_moves.append(move)
                    i += 1
                
                    move = (ENCRYPTOR, (x, y), output_array[i])
                    self.defence_moves.append(move)
                    i += 1
                
                    move = (FILTER, (x, y), output_array[i])
                    self.defence_moves.append(move)
                    i += 1
        
        self.attack_moves = []
        for x in range(ARENA_SIZE):
            y_left = 13 - x
            y_right = x - 14
            y = max([y_left, y_right])
            
            move = (PING, (x, y), output_array[i])
            self.attack_moves.append(move)
            i += 1
            
            move = (EMP, (x, y), output_array[i])
            self.attack_moves.append(move)
            i += 1
            
            move = (SCRAMBLER, (x, y), output_array[i])
            self.attack_moves.append(move)
            i += 1
            
        self.size = i   
    
    def best_defence_move(self, occupied_locations):
        avail_moves = [(unit_type, (x, y), value) 
                                for (unit_type, (x, y), value) in self.defence_moves 
                                if (x, y) not in occupied_locations]
        
        best = max(avail_moves, key=lambda x: x[2])
        (unit_type, (x, y), value) = best
        #gamelib.debug_write("Defence {}".format(best))
        return (unit_type, (x, y))
        
    def best_attack_move(self, occupied_locations):
        avail_moves = [(unit_type, (x, y), value) 
                        for (unit_type, (x, y), value) in self.defence_moves 
                        if (x, y) not in occupied_locations]
        
        best = max(avail_moves, key=lambda x: x[2])
        (unit_type, (x, y), value) = best
        #gamelib.debug_write("Attack {}".format(best))
        return (unit_type, (x, y))        