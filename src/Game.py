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
from pubsub import pub

game = 0
myUI = 0

def message(msg):
    game.message(msg)

class Game(object):
    
    fontsize = None

    def __init__(self, **kwargs):
        global game
        game = self
        self.debug = kwargs.get('debug', False)
        
        if self.debug:
            pub.subscribe(self.debugListener, 'event')
                
        if pygame.init() != (6,0):
            print "Error starting pygame"
        
        db.saveDB.start(True)
        
        self.fontsize = kwargs.get('fontsize')
    
        seed = 1155272238
        print seed
        random.seed(seed)
        
        d1 = L.DungeonLevel(name = "Test Dungeon", width = C.MAP_WIDTH, height = C.MAP_HEIGHT, depth = 1, defaultFloorType = T.StoneFloor,
                           defaultWallType = T.RockWall, defaultTunnelFloorType = T.RockTunnel, defaultTunnelWallType = T.RockWall)

        d2 = L.CaveLevel(name = "Test Cave", width = C.MAP_WIDTH, height = C.MAP_HEIGHT, depth = 2, defaultFloorType = T.RockTunnel, defaultWallType = T.RockWall)
        
        d1.buildLevel()
        d2.buildLevel()
        
        player = P.Player()
        d1.placeOnUpStair(player)
        
        orc1 = Cr.Orc()
        d1.placeCreatureAtRandom(orc1)
        
        orc2 = Cr.Orc()
        d1.placeCreatureAtRandom(orc2)
        
        db.saveDB.save(d1)
        db.saveDB.save(d2)
        
        d1.setNextLevel(d2)
        d2.setPreviousLevel(d1)
        
        print d1.id, "=>", d2.id
#        print d2.previousLevelId, "=>", d1.nextLevelId
        
        global myUI
        myUI = ui.UI(level = d1, player = player, fontsize = self.fontsize)
        
    def debugListener(self,topic=pub.AUTO_TOPIC, **args):
        print 'Got an event of type: ' + topic.getName()
        print '  with data: ' + str(args)
        
    def play(self):
        myUI.gameLoop()
        db.saveDB.save(myUI.getCurrentLevel())
        
    def message(self, msg):
        if self.debug: print msg
        myUI.message(msg)



