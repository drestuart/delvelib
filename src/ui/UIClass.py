'''
Created on Mar 12, 2013

@author: dstu
'''

from Import import *
import Const as C
import colors
import os.path
import textwrap

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
        self.panel = libtcod.console_new(C.PANEL_WIDTH, C.PANEL_HEIGHT)

        self.msgs = []
        
    
    def render_bar(self, x, y, totalWidth, name, value, maximum, barColor, backColor):
        #render a bar (HP, experience, etc). first calculate the width of the bar
        barWidth = int(float(value) / maximum * totalWidth)
     
        #render the background first
        libtcod.console_set_default_background(self.panel, backColor)
        libtcod.console_rect(self.panel, x, y, totalWidth, 1, False, libtcod.BKGND_SCREEN)
     
        #now render the bar on top
        libtcod.console_set_default_background(self.panel, barColor)
        if barWidth > 0:
            libtcod.console_rect(self.panel, x, y, barWidth, 1, False, libtcod.BKGND_SCREEN)
            
        #finally, some centered text with the values
        libtcod.console_set_default_foreground(self.panel, libtcod.white)
        libtcod.console_print_ex(self.panel, x + totalWidth / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
            name + ': ' + str(value) + '/' + str(maximum))
        
    def message(self, newMsg, color = colors.white):
        #split the message if necessary, among multiple lines
        newMsgLines = textwrap.wrap(newMsg, C.MSG_WIDTH)
     
        for line in newMsgLines:
            #if the buffer is full, remove the first line to make room for the new one
            if len(self.msgs) == C.MSG_HEIGHT:
                del self.msgs[0]
     
            #add the new line as a tuple, with the text and the color
            self.msgs.append( (line, color) )
    
    
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
            
            #prepare to render the GUI panel
            libtcod.console_set_default_background(self.panel, libtcod.black)
            libtcod.console_clear(self.panel)
            
            y = 1
            for (line, color) in self.msgs:
                libtcod.console_set_default_foreground(self.panel, color)
                libtcod.console_print_ex(self.panel, C.MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
                y += 1
         
            #show the player's stats
#            render_bar(1, 1, BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp,
#                libtcod.light_red, libtcod.darker_red)
         
            #blit the contents of "panel" to the root console
            libtcod.console_blit(self.panel, 0, 0, C.SCREEN_WIDTH, C.PANEL_HEIGHT, 0, C.PANEL_X, C.PANEL_Y)
            
            self.currentLevel.computeFOV(self.player.getX(), self.player.getY(), 0)

#            print "Drawing"
            self.currentLevel.draw()
    #        libtcod.console_blit(mapConsole, 0, 0, C.MAP_WIDTH, C.MAP_HEIGHT, 0, 0, 0)
            libtcod.console_blit(self.mapConsole, 0, 0, C.MAP_WIDTH, C.MAP_HEIGHT, 0, C.MAP_X, C.MAP_Y)
    
            libtcod.console_flush()
            
            for cr in self.currentLevel.creatures:
                cr.takeTurn()
            
#            self.player.takeTurn()
            
            self.currentLevel.clear()
            
            player_action = handle_keys()
            if player_action == 'exit':
                break
        
    
    
    