'''
Created on Mar 10, 2013

@author: dstu
'''

import random

from pubsub import pub
import pygame

import Const as C
import CreatureClass as Cr
import LevelClass as L
import PlayerClass as P
import UIClass as ui
import database as db
import DungeonClass as D

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
        
        d = D.Dungeon(name = "The Dungeons of Dread", startingDepth = 1)
        d.generateLevels(4)
        
        d1 = d.getLevels()[1]
        
#         d1 = L.DungeonLevel(name = "Test Dungeon", width = C.MAP_WIDTH, height = C.MAP_HEIGHT, depth = 1)
# 
#         d2 = L.CaveLevel(name = "Test Cave", width = C.MAP_WIDTH, height = C.MAP_HEIGHT, depth = 2)
#         
#         d1.buildLevel()
#         d2.buildLevel()
#         
#         L.connectLevels(d1, d2)
#         d1.placeUpStair()
#         
        player = P.Player()
        d1.placeOnUpStair(player)
#         
#         orc1 = Cr.Orc()
#         d1.placeCreatureAtRandom(orc1)
#         
#         orc2 = Cr.Orc()
#         d1.placeCreatureAtRandom(orc2)
#         
#         db.saveDB.save(d1)
#         db.saveDB.save(d2)
        
#         d1.setNextLevel(d2)
#         d2.setPreviousLevel(d1)
        
        
        
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



