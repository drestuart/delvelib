'''
Created on Mar 21, 2014

@author: dstuart
'''

import unittest
import testbase
from ludibrio import Mock, Stub
from TileClass import WoodWall, WoodFloor
from CreatureClass import Orc
from DungeonFeatureClass import Altar

class TestTileClass(unittest.TestCase):
 
    def setUp(self):
        self.wall = WoodWall(2, 2)
        self.floor = WoodFloor(1,2)
        
        self.orc = Orc()
        self.altar = Altar()
            
        self.tileWithCreature = WoodFloor(3, 3)
        self.tileWithCreature.setCreature(self.orc)
        
        self.tileWithFeature = WoodFloor(4, 4, feature=self.altar)
        
        self.tileWithBoth = WoodFloor(5, 4, feature=self.altar)
        self.tileWithBoth.setCreature(self.orc)
        
    def test_getSymbol(self):
        self.assertEqual(self.floor.getSymbol(), ".")
        self.assertEqual(self.wall.getSymbol(), "#")
        self.assertEqual(self.tileWithCreature.getSymbol(), "o")
        self.assertEqual(self.tileWithFeature.getSymbol(), "_")
        self.assertEqual(self.tileWithBoth.getSymbol(), "o")
        
    



if __name__ == '__main__':
    unittest.main()

