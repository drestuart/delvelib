'''
Created on Mar 10, 2013

@author: dstu
'''

from Import import *
libtcod = importLibtcod()

import UIClass as ui
import LevelClass as L
import database as db
import Const as C
import RoomClass as R
import TileClass as T
import DungeonFeatureClass as F
import CreatureClass as Cr
import random

def main():
    
    print '-=delveRL=-'
    
    db.saveDB.start(True)
    
    seed = 1155272238
    print seed
    random.seed(seed)
    
    d1 = L.DungeonLevel(name = "Test", depth = 1, defaultFloorType = T.StoneFloor,
                      defaultWallType = T.RockWall, defaultTunnelFloorType = T.RockTunnel, defaultTunnelWallType = T.RockWall)
    
    d1.buildLevel()
    
    db.saveDB.save(d1)
#    db.saveDB.saveAll(d1.tiles)

#    randTile = d1.getRandomOpenTile()
    

    myUI = ui.UI(level=d1)
    myUI.createWindow()
    d1.computeFOV(11, 11, 0)
    myUI.gameLoop()



if __name__ == '__main__':
    main()