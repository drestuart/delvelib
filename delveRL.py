'''
Created on Mar 10, 2013

@author: dstu
'''

from Import import *
libtcod = importLibtcod()

import Const as C
import CreatureClass as Cr
import DungeonFeatureClass as F
import LevelClass as L
import RoomClass as R
import TileClass as T
import PlayerClass as P
import UIClass as ui
import database as db
import random


def main():
    
    print '-=delveRL=-'
    
    db.saveDB.start(True)
    
    seed = 1155272238
    print seed
    random.seed(seed)
    
    d1 = L.DungeonLevel(name = "Test", depth = 1, defaultFloorType = T.StoneFloor,
                      defaultWallType = T.RockWall, defaultTunnelFloorType = T.RockTunnel, defaultTunnelWallType = T.RockWall)
    
#    d1.buildLevel()
    d1.buildLevelNew()
    player = P.Player()
    d1.placeCreatureInRandomRoom(player)
    
    orc1 = Cr.Orc()
    d1.placeCreatureInRandomRoom(orc1)
    
#    orc2 = Cr.Orc()
#    d1.placeCreatureInRandomRoom(orc2)
    
    db.saveDB.save(d1)

    print len(d1.creatures), "creatures"

    myUI = ui.UI(level = d1, player = player)
    myUI.createWindow()
    myUI.gameLoop()



if __name__ == '__main__':
    main()