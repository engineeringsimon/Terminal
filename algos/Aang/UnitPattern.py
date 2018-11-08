# -*- coding: utf-8 -*-
"""
Created on Sun Nov  4 14:04:33 2018

@author: user
"""

import random
import MyGameState as gs

# Dumb wall
attempted_skybison = '''
..FFFFFFFFFFFFFFFFFFFFFFFFFF
 ..DDDEDEDEDEDEDEDEDEDEDDDD 
  ........................ 
   ..EEEEEEEEE...........
    ..EEEE.............. 
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

# minimal
ecstacy_of_gold = '''
............................
 ..D....................D.. 
  ..D..................D.. 
   ......................
    ....D....D.....D.... 
     ...E....E.....E... 
      ....E.....E..... 
       ......E....... 
        ..E.....E... 
         ....E..... 
          ........ 
           ...... 
            .... 
             .. 
''' 

class UnitPattern:
    def __init__(self):
        self.g = gs.GameState()
        self.desired_layout_string = ecstacy_of_gold
        
        # load the game state from a text string above
        self.gap = []
        lines = self.desired_layout_string.split("\n")[1:]
        for loc in gs.my_side_points:
            (x, y) = loc
            character = lines[gs.HALF_ARENA - 1 - y][x]
            if character == "G":
                self.gap.append(loc)
                continue
            if character in gs.unit_code:
                self.g.add_unit((x, y), gs.unit_code[character])   
                
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
                        line += gs.reverse_unit_code[unit.type]
                else:
                    line += " "
            lines.append(line)
        return "\n".join(lines)
    
    def unit_locations(self):
        # return the locations of all the units in priority order
        # order is by y coordinate + random number in range +/- 1
        locations = [x for x in self.g.units.keys()]
        locations.sort(key=lambda x: x[1] + random.uniform(-1.0, 1.0), reverse=True)
        #random.shuffle(locations)
        return locations
    
    def unit_type_at(self, loc):
        return self.g.unit_at(loc).type
    
if __name__ == "__main__":
    u = UnitPattern()
    print(u)