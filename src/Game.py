'''
Created on Mar 10, 2013

@author: dstu
'''

import Const as C
import CreatureClass as Cr
import DungeonFeatureClass as F
import LevelClass as L
import RoomClass as R
import InventoryClass as I
import TileClass as T
import PlayerClass as P
import UIClass as ui
import database as db
import random
import colors

game = 0
myUI = 0

class Game(object):

    def __init__(self, **kwargs):
        global game
        game = self
        
        db.saveDB.start(True)
    
        seed = 1155272238
        print seed
        random.seed(seed)
        
        d1 = L.DungeonLevel(name = "Test", depth = 1, defaultFloorType = T.StoneFloor,
                          defaultWallType = T.RockWall, defaultTunnelFloorType = T.RockTunnel, defaultTunnelWallType = T.RockWall)
        
        d1.buildLevel()
        player = P.Player()
        d1.placeCreatureInRandomRoom(player)
        
        orc1 = Cr.Orc()
        d1.placeCreatureInRandomRoom(orc1)
        
    #    orc2 = Cr.Orc()
    #    d1.placeCreatureInRandomRoom(orc2)
        
        db.saveDB.save(d1)
        
        global myUI
        myUI = ui.UI(level = d1, player = player)
#        myUI.createWindow()
        
    def play(self):
        myUI.gameLoop()
        db.saveDB.save(myUI.getCurrentLevel())
        
    def message(self, msg, color = colors.white):
        self.myUI.message(msg, color)



