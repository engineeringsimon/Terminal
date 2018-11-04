import unittest
import MyGameState as gs
import random

class TestStringMethods(unittest.TestCase):
    def setUp(self):
        self.g = gs.GameState()
    def test_arena_points(self):
        self.assertIsNotNone(gs.arena_points)
        self.assertEqual(len(gs.arena_points), 420)
        
    def test_my_side(self):
        self.assertIsNotNone(gs.my_side_points)
        self.assertEqual(len(gs.my_side_points), 210)
        self.assertTrue(gs.my_side_points < gs.arena_points)
        
    def test_enemy_side(self):
        self.assertIsNotNone(gs.enemy_side_points)
        self.assertEqual(len(gs.enemy_side_points), 210)
        self.assertTrue(gs.enemy_side_points < gs.arena_points)
        
    def test_edge_points(self):
        self.assertIsNotNone(gs.edge_points)
        self.assertEqual(len(gs.edge_points), gs.HALF_ARENA * 4)
        self.assertTrue(gs.edge_points < gs.arena_points)
        
    def test_my_edge_points(self):
        self.assertIsNotNone(gs.my_edge_points)
        self.assertEqual(len(gs.my_edge_points), gs.HALF_ARENA * 2)
        self.assertTrue(gs.my_edge_points < gs.my_side_points)
        
    def test_enemy_edge_points(self):
        self.assertIsNotNone(gs.enemy_edge_points)
        self.assertEqual(len(gs.enemy_edge_points), gs.HALF_ARENA * 2)
        self.assertTrue(gs.enemy_edge_points < gs.enemy_side_points)
        
    def test_range_lookups(self):
        self.assertIsNotNone(gs.points_within_3_5)
        self.assertIsNotNone(gs.points_within_5_5)
        self.assertEqual(len(gs.points_within_3_5), 420)
        self.assertEqual(len(gs.points_within_5_5), 420)
        
    def test_add_destructor(self):
        self.do_add_unit(gs.DESTRUCTOR)
        
    def test_add_encryptor(self):
        self.do_add_unit(gs.ENCRYPTOR)
        
    def test_add_filter(self):
        self.do_add_unit(gs.FILTER)
     
    def do_add_unit(self, unit_type):
        location = random.choice(list(gs.arena_points))
        isOk = self.g.add_unit(location, unit_type)
        self.assertTrue(isOk)
        self.assertIsNotNone(self.g.units)
        self.assertEqual(len(self.g.units), 1)
        unit = self.g.units[location]
        self.assertEqual(unit.type, unit_type) 
        
        isOk = self.g.add_unit(location, unit_type)
        self.assertFalse(isOk)        
        
    def test_add_ping(self):
        self.do_add_unit(gs.PING)
        
    def test_add_emp(self):
        self.do_add_unit(gs.EMP)
        
    def test_add_scrambler(self):
        self.do_add_unit(gs.SCRAMBLER)
     
    def do_add_unit_to_wall(self, unit_type):
        location = random.choice(list(gs.arena_points))
        isOk = self.g.add_unit(location, unit_type)
        self.assertTrue(isOk)
        self.assertIsNotNone(self.g.units)
        self.assertEqual(len(self.g.units), 1)
        unit = self.g.units[location]
        self.assertEqual(unit.type, unit_type) 
        
        isOk = self.g.add_unit(location, unit_type)
        self.assertFalse(isOk)        
        



if __name__ == '__main__':
    unittest.main()