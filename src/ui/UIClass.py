'''
Created on Mar 12, 2013

@author: dstu
'''

from Import import *
import os.path
import Const as C
import colors

libtcod = importLibtcod()


#FONTS_DIR = os.path.join("..", "..", "fonts")
FONTS_DIR = os.path.join("fonts")
DEFAULT_FONT = os.path.join(FONTS_DIR, "arial12x12.png")

key = libtcod.Key()
mouse = libtcod.Mouse()

def handle_keys():
     
    if key.vk == libtcod.KEY_ESCAPE:
        return 'exit'  #exit game
    else:
        return 'didnt-take-turn'

class UI(object):

    def __init__(self, **kwargs):
        self.currentLevel = kwargs.get('level', None)
        self.player = kwargs.get('player', None)
        
    def createWindow(self):
        libtcod.console_set_custom_font(DEFAULT_FONT, libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
        libtcod.console_init_root(C.SCREEN_WIDTH, C.SCREEN_HEIGHT, C.TITLE, False)
        libtcod.sys_set_fps(C.LIMIT_FPS)
        
        self.mapConsole = libtcod.console_new(C.MAP_WIDTH, C.MAP_HEIGHT)
        self.currentLevel.setMapConsole(self.mapConsole)
        
        libtcod.console_set_default_background(0, libtcod.BKGND_NONE)
        libtcod.console_set_default_background(self.mapConsole, libtcod.BKGND_NONE)
        
        libtcod.console_set_keyboard_repeat(500, 250)
        
    def getCurrentLevel(self):
        return self.currentLevel
    
    def setCurrentLevel(self, lvl):
        self.currentLevel = lvl
        self.currentLevel.setMapConsole(self.mapConsole)
        
        
    def gameLoop(self):
        
        while not libtcod.console_is_window_closed():
            libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse)
            libtcod.console_clear(self.mapConsole)
            
            self.currentLevel.computeFOV(self.player.getX(), self.player.getY(), 0)

#            print "Drawing"
            self.currentLevel.draw()
    #        libtcod.console_blit(mapConsole, 0, 0, C.MAP_WIDTH, C.MAP_HEIGHT, 0, 0, 0)
            libtcod.console_blit(self.mapConsole, 0, 0, C.MAP_WIDTH, C.MAP_HEIGHT, 0, 0, 0)
    
            libtcod.console_flush()
            
            self.player.takeTurn()
            
            self.currentLevel.clear()
            
            player_action = handle_keys()
            if player_action == 'exit':
                break
        
    
    
    