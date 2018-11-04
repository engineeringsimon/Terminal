import math

ARENA_SIZE = 28
HALF_ARENA = 14
FILTER = "FF"
ENCRYPTOR = "EF"
DESTRUCTOR = "DF"
PING = "PI"
EMP = "EI"
SCRAMBLER = "SI"

def is_in_arena(x, y):
    if x < 0 or x >= ARENA_SIZE or y < 0 or y >= ARENA_SIZE:
        return False
    
    a = x + y
    
    if a < (HALF_ARENA - 1) or a > (ARENA_SIZE + HALF_ARENA - 1):
        return False
        
    b = y - x
    if b > HALF_ARENA or b < -HALF_ARENA:
        return False
        
    return True

def valid_arena_point_set():
    points = set()
    for x in range(ARENA_SIZE):
        for y in range(ARENA_SIZE):
            if is_in_arena(x, y):
                points.add((x, y))
    return points

def valid_edge_points_set():
    points = set()
    for y in range(HALF_ARENA):
        points.add((13 - y, y))
        points.add((y + 14, y))
        
    for y in range(HALF_ARENA, ARENA_SIZE):
        points.add((y - HALF_ARENA, y))
        points.add((ARENA_SIZE + HALF_ARENA - 1 - y, y))
    return points

def range_between_points(loc0, loc1):
    (x0, y0) = loc0
    (x1, y1) = loc1
    return math.sqrt((x1 - x0)**2 + (y1 - y0)**2)

def points_within_range(r):
    ranges = {}
    all_points = valid_arena_point_set()
    for centre_loc in all_points:
        ranges[centre_loc] = [loc for loc in all_points if range_between_points(centre_loc, loc)]
    return ranges

# Constants and lookups
arena_points = valid_arena_point_set()
my_side_points = {(x, y) for (x, y) in arena_points if y < HALF_ARENA}
enemy_side_points = {(x, y) for (x, y) in arena_points if y >= HALF_ARENA}
edge_points = valid_edge_points_set()
my_edge_points = {(x, y) for (x, y) in edge_points if y < HALF_ARENA}
enemy_edge_points = {(x, y) for (x, y) in edge_points if y >= HALF_ARENA}
points_within_3_5 = points_within_range(3.5)
points_within_5_5 = points_within_range(5.5)

unit_stability = {
        PING: 15, 
        EMP: 5,
        SCRAMBLER: 40,
        FILTER: 60,
        ENCRYPTOR: 30,
        DESTRUCTOR: 75
        }

unit_range = {
        PING: 3.5, 
        EMP: 5.5,
        SCRAMBLER: 3.5,
        FILTER: 0,
        ENCRYPTOR: 3.5,
        DESTRUCTOR: 3.5
        }
# (defender disruption, information disruption, encryption)
unit_effect = {
        PING:       (1, 1,  0), 
        EMP:        (3, 3,  0),
        SCRAMBLER:  (0, 10, 0),
        FILTER:     (0, 0,  0),
        ENCRYPTOR:  (0, 0, 10),
        DESTRUCTOR: (4, 4,  0)
        }

# (bits, cores)
unit_cost = {
        PING:       (1, 0), 
        EMP:        (3, 0),
        SCRAMBLER:  (1, 0),
        FILTER:     (0, 1),
        ENCRYPTOR:  (0, 4),
        DESTRUCTOR: (0, 3)
        }

ENCRYPTOR_STABILITY_DECAY_PER_FRAME = 0.15
INITIAL_HEALTH = 30
NUM_CORES_PER_TRAVERSE = 2
NUM_INITIAL_CORES = 25
NUM_INITIAL_BITS = 5
BIT_DECAY_RATIO_PER_TURN = 1.0 / 3.0

INITIAL_BIT_INCREMENT_PER_TURN = 5
def bit_increment_per_turn(turn_index):
    return INITIAL_BIT_INCREMENT_PER_TURN + (turn_index // 10)

CORE_INCREMENT_PER_TURN = 4



class Unit:
    def __init__(self, unit_type):
        self.type = unit_type
        self.stability = unit_stability[unit_type]

class GameState:
    def __init__(self):
        self.units = {}
    
    def add_unit(self, location, unit_type):
        if type(location) == list:
            location = (location[0], location[1])
            
        if location in self.units:
            return False
        
        self.units[location] = Unit(unit_type)
        return True
    
    def unit_at(self, location):
        if location in self.units:
            return self.units[location]
        return None

unit_names = {
        PING: "Ping", 
        EMP: "EMP",
        SCRAMBLER: "Scrambler",
        FILTER: "Filter",
        ENCRYPTOR: "Encryptor",
        DESTRUCTOR: "Destructor"
        } 
    
class SpawnEvent:
    def __init__(self, event):
        self.loc = event[0]
        self.unit_id = event[1]
        self.id_str = event[2]
        self.player_id = event[3]
        self.x = self.loc[0]
        self.y = self.loc[1]
        self.location = (self.x, self.y)
        self.unit_codes = {
                              0: FILTER,
                              1: ENCRYPTOR,
                              2: DESTRUCTOR,
                              3: PING,
                              4: EMP,
                              5: SCRAMBLER,
                              6: "Remove"
                        }
    def name(self):
        code = self.unit_codes[self.unit_id]
        if code in unit_names:
            return unit_names[code]
        return code
    
    def is_attacker(self):
        return self.unit_id in [3,4,5]
    
    def unit_type(self):
        return self.unit_codes[self.unit_id]
        
    def __repr__(self):
        return "Player {}: {} @ {}".format(self.player_id, 
                       self.name(), 
                       self.location)



