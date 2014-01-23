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
import pygame

game = 0
myUI = 0

def message(msg):
    game.message(msg)

class Game(object):
    
    fontsize = None

    def __init__(self, **kwargs):
        global game
        game = self
        
        if pygame.init() != (6,0):
            print "Error starting pygame"
        
        db.saveDB.start(True)
        
        self.fontsize = kwargs.get('fontsize')
    
        seed = 1155272238
        print seed
        random.seed(seed)
        
#         d1 = L.DungeonLevel(name = "Test", width = C.MAP_WIDTH, height = C.MAP_HEIGHT, depth = 1, defaultFloorType = T.StoneFloor,
#                           defaultWallType = T.RockWall, defaultTunnelFloorType = T.RockTunnel, defaultTunnelWallType = T.RockWall)

        d1 = L.CaveLevel(name = "Test", width = C.MAP_WIDTH, height = C.MAP_HEIGHT, depth = 1, defaultFloorType = T.RockTunnel, defaultWallType = T.RockWall)
        
        d1.buildLevel()
        player = P.Player()
        d1.placeCreatureAtRandom(player)
        
        orc1 = Cr.Orc()
        d1.placeCreatureAtRandom(orc1)
        
    #    orc2 = Cr.Orc()
    #    d1.placeCreatureAtRandom(orc2)
        
        db.saveDB.save(d1)
        
        global myUI
        myUI = ui.UI(level = d1, player = player, fontsize = self.fontsize)
        
    def play(self):
        myUI.gameLoop()
        db.saveDB.save(myUI.getCurrentLevel())
        
    def message(self, msg):
        myUI.message(msg)



