# -*- coding: utf-8 -*-
"""
Created on Sun Nov  4 14:04:33 2018

@author: user
"""

import MyGameState as gs
import random

# Dumb wall
dumb_wall_layout = '''
FFFFFFFFFFFFFFFFFFFFFFFFF.FF
 .......................... 
  D...EDEDEDEDEDEDEDEDEDDD 
   ......................
    .................... 
     .................. 
      ................ 
       .............. 
        ............ 
         .......... 
          ........ 
           ...... 
            .... 
             .. 
''' 

unit_code = {
            'D': gs.DESTRUCTOR,
            'F': gs.FILTER,
            'E': gs.ENCRYPTOR,
            'X': gs.EMP,
            'P': gs.PING,
            'S': gs.SCRAMBLER
            }

reverse_unit_code = {}
for character in unit_code:
    reverse_unit_code[unit_code[character]] = character


class UnitPattern:
    def __init__(self):
        self.g = gs.GameState()
        self.desired_layout_string = dumb_wall_layout
        
        # load the game state from a text string above
        self.gap = []
        lines = self.desired_layout_string.split("\n")[1:]
        for loc in gs.my_side_points:
            (x, y) = loc
            character = lines[gs.HALF_ARENA - 1 - y][x]
            if character == "G":
                self.gap.append(loc)
                continue
            if character in unit_code:
                self.g.add_unit((x, y), unit_code[character])   
                
    def __repr__(self):
        lines = []
        for y in range(gs.HALF_ARENA - 1, -1, -1):
            line = "|   "
            for x in range(gs.ARENA_SIZE):
                if gs.is_in_arena(x, y):
                    unit = self.g.unit_at((x, y))
                    if (x, y) in self.gap:
                        line += "G"
                    elif unit == None:
                        line += "."
                    else:
                        line += reverse_unit_code[unit.type]
                else:
                    line += " "
            lines.append(line)
        return "\n".join(lines)
    
    def unit_locations(self):
        # return the locations of all the units in priority order
        # order is by y coordinate + random number in range +/- 1
        locations = [x for x in self.g.units.keys()]
        locations.sort(key=lambda x: x[1] + random.uniform(-1.0, 1.0), reverse=True)
        return locations
    
    def unit_type_at(self, loc):
        if loc in self.g.units:
            return self.g.units[loc].type
        return None
    
if __name__ == "__main__":
    u = UnitPattern()
    print(u)