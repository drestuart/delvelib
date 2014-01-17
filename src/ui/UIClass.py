'''
Created on Mar 12, 2013

@author: dstu
'''

from Import import *
import Const as C
import colors
import os.path
import textwrap
import Game as G
import keys
import Util as U

#libtcod = importLibtcod()


#FONTS_DIR = os.path.join("..", "..", "fonts")
FONTS_DIR = os.path.join("fonts")
DEFAULT_FONT = os.path.join(FONTS_DIR, "arial12x12.png")

# TODO get keyboard and mouse input 
#key = libtcod.Key()
#mouse = libtcod.Mouse()



class UI(object):

    def __init__(self, **kwargs):
        self.currentLevel = kwargs.get('level', None)
        self.player = kwargs.get('player', None)
        self.panel = libtcod.console_new(C.PANEL_WIDTH, C.PANEL_HEIGHT)

        self.msgs = []
    
    def singleChoiceMenu(self, header, options, width):
        
        #calculate total height for the header (after auto-wrap) and one line per option
        header_height = libtcod.console_get_height_rect(self.mapConsole, 0, 0, width, C.SCREEN_HEIGHT, header)
        height = len(options) + header_height
     
        lines = []
        letter_index = ord('a')
        for option in options:
            text = '(' + chr(letter_index) + ') ' + option
            lines.append(text)
            letter_index += 1

        self.displayTextWindow(header, C.MENU_X, C.MENU_Y, C.MENU_WIDTH, height, lines)
        
        key = libtcod.console_wait_for_keypress(True)
     
        #convert the ASCII code to an index; if it corresponds to an option, return it
        index = key.c - ord('a')
        if index >= 0 and index < len(options): 
            return index
        
        return None
    
    def displayTextWindow(self, header, x, y, width, height, lines):
        window = libtcod.console_new(width, height + 2)
        
        libtcod.console_set_default_foreground(window, libtcod.white)
        
        def addBorder(line):
            line = line.ljust(width - 4)
            line = "= " + line + " ="
            return line
        
        header = addBorder(header)
        
        libtcod.console_print_ex(window, 0, 0, libtcod.BKGND_NONE, libtcod.LEFT, "="*width)
        libtcod.console_print_rect_ex(window, 0, 1, width, height + 2, libtcod.BKGND_NONE, libtcod.LEFT, header)
        
        header_height = libtcod.console_get_height_rect(self.mapConsole, 0, 0, width, C.SCREEN_HEIGHT, header)
        
        # Print each line
        y = header_height + 1
        for line in lines:
            # Formatting
            line = addBorder(line)
            
            libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
            y += 1
        
        libtcod.console_print_ex(window, 0, height + 1 , libtcod.BKGND_NONE, libtcod.LEFT, "="*width)
        
        libtcod.console_blit(window, 0, 0, width, height + 2, 0, C.MENU_X, C.MENU_Y, 1.0, 0.7)
        libtcod.console_flush()
        
    
    def showPlayerInventory(self):
        header = C.PLAYER_INVENTORY_HEADER
        inv = self.player.getInventory()
        
        header_height = libtcod.console_get_height_rect(self.mapConsole, 0, 0, C.MENU_WIDTH, C.SCREEN_HEIGHT, header)
        height = inv.length() + header_height
        
        lines = []
        
        for item in inv.getItems():
            text = item.getDescription()
            lines.append(text)
        
        self.displayTextWindow(header, C.MENU_X, C.MENU_Y, C.MENU_WIDTH, height, lines)
        
        key = libtcod.console_wait_for_keypress(True)
        
        # Do nothing... yet
        return None
        
    
    def wearMenu(self):
        header = C.WEAR_MENU_HEADER
        inv = self.player.getInventory()
        
        lines = []
        
        for item in inv.getItems():
            if type(item).getWearable():
                text = item.getDescription()
                lines.append(text)
        
#        self.displayTextWindow(header, C.MENU_X, C.MENU_Y, C.MENU_WIDTH, height, lines)
        index = self.singleChoiceMenu(header, lines, C.MENU_WIDTH)
        
#        key = libtcod.console_wait_for_keypress(True)
        
        # Do nothing... yet
        return None
    
    def wieldMenu(self):
        header = C.WIELD_MENU_HEADER
        inv = self.player.getInventory()
        
        lines = []
        
        for item in inv.getItems():
            if type(item).getWieldable():
                text = item.getDescription()
                lines.append(text)
        
#        self.displayTextWindow(header, C.MENU_X, C.MENU_Y, C.MENU_WIDTH, height, lines)
        index = self.singleChoiceMenu(header, lines, C.MENU_WIDTH)
        
#        key = libtcod.console_wait_for_keypress(True)
        
        # Do nothing... yet
        return None
    
    def quaffMenu(self):
        header = C.QUAFF_MENU_HEADER
        inv = self.player.getInventory()
        
        lines = []
        
        for item in inv.getItems():
            if type(item).getDrinkable():
                text = item.getDescription()
                lines.append(text)
        
#        self.displayTextWindow(header, C.MENU_X, C.MENU_Y, C.MENU_WIDTH, height, lines)
        index = self.singleChoiceMenu(header, lines, C.MENU_WIDTH)
        
#        key = libtcod.console_wait_for_keypress(True)
        
        # Do nothing... yet
        return None
    
    def readMenu(self):
        header = C.READ_MENU_HEADER
        inv = self.player.getInventory()
        
        lines = []
        
        for item in inv.getItems():
            if type(item).getReadable():
                text = item.getDescription()
                lines.append(text)
        
#        self.displayTextWindow(header, C.MENU_X, C.MENU_Y, C.MENU_WIDTH, height, lines)
        index = self.singleChoiceMenu(header, lines, C.MENU_WIDTH)
        
#        key = libtcod.console_wait_for_keypress(True)
        
        # Do nothing... yet
        return None
    
    def eatMenu(self):
        header = C.EAT_MENU_HEADER
        inv = self.player.getInventory()
        
        lines = []
        
        for item in inv.getItems():
            if type(item).getEdible():
                text = item.getDescription()
                lines.append(text)
        
#        self.displayTextWindow(header, C.MENU_X, C.MENU_Y, C.MENU_WIDTH, height, lines)
        index = self.singleChoiceMenu(header, lines, C.MENU_WIDTH)
        
#        key = libtcod.console_wait_for_keypress(True)
        
        # Do nothing... yet
        return None
    
    def zapMenu(self):
        header = C.ZAP_MENU_HEADER
        inv = self.player.getInventory()
        
        lines = []
        
        for item in inv.getItems():
            if type(item).getZappable():
                text = item.getDescription()
                lines.append(text)
        
#        self.displayTextWindow(header, C.MENU_X, C.MENU_Y, C.MENU_WIDTH, height, lines)
        index = self.singleChoiceMenu(header, lines, C.MENU_WIDTH)
        
#        key = libtcod.console_wait_for_keypress(True)
        
        # Do nothing... yet
        return None
    
    
    def pickUpItemMenu(self, inventory):
        #show a singleChoiceMenu with each item of the inventory as an option
        if inventory.length() == 0:
#            lines = ['Inventory is empty.']
            return None
        else:
            items = inventory.getItems()
            lines = [item.getDescription() for item in items]
        
        header = C.PICK_UP_ITEM_MENU_HEADER
        index = self.singleChoiceMenu(header, lines, C.MENU_WIDTH)
     
        #if an item was chosen, return it
        if index is None or inventory.length() == 0:
            return None
        
        return inventory.pop(index)
    
    def selectItemMenu(self, inventory):
        #show a singleChoiceMenu with each item of the inventory as an option
        if inventory.length() == 0:
#            options = ['Inventory is empty.']
            return None
        else:
            items = inventory.getItems()
            options = [item.getDescription() for item in items]
        
        header = C.PICK_UP_ITEM_MENU_HEADER
        index = self.singleChoiceMenu(header, options, C.MENU_WIDTH)
     
        #if an item was chosen, return it
        if index is None or inventory.length() == 0:
            return None
        
        return inventory.getItem(index)
        
    def handleKeys(self, key):
     
        if key.vk == libtcod.KEY_ESCAPE:
            return "exit"
            
        elif key.pressed:
            
            direc = keys.getMovementDirection(key)
            
            keyStr = U.get_key(key)
            
            # Move
            if direc:
                dx, dy = direc
                if self.player.move(dx, dy):
                    return 'took-turn'
 
            elif key.vk == libtcod.KEY_KPDEC or keyStr == '.': # Wait
                return 'took-turn'
            
            elif keyStr == ',': # Pick up items
                if self.player.getTile().getInventory():
#                    item = self.player.getTile().getInventory().pop(0)
                    
                    inv = self.player.getTile().getInventory()
                    item = self.pickUpItemMenu(inv)
                    if item:
#                        inv.removeItem(item)
                        self.player.pickUpItem(item)
                    
                    return 'took-turn'
                
            elif keyStr == 'W':  # Wear something
                self.wearMenu()                
                return 'didnt-take-turn'
            
            elif keyStr == 'w':  # Wield something
                self.wieldMenu()                
                return 'didnt-take-turn'
            
            elif keyStr == 'q':  # Quaff something
                self.quaffMenu()                
                return 'didnt-take-turn'
            
            elif keyStr == 'r':  # Read something
                self.readMenu()                
                return 'didnt-take-turn'
            
            elif keyStr == 'e':  # Eat something
                self.eatMenu()                
                return 'didnt-take-turn'
            
            elif keyStr == 'z':  # Zap something
                self.zapMenu()                
                return 'didnt-take-turn'
                
            elif keyStr == 'i':
                self.showPlayerInventory()
                return 'didnt-take-turn'
            
        else:
            return 'didnt-take-turn'
    
    def handleKeysOld(self, key):
     
        if key.vk == libtcod.KEY_ESCAPE:
            return 'exit'  #exit game
        else:
            return self.player.AI.takeTurn(key)
        
    
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
        
    def getTileDescUnderMouse(self):
#        global mouse
     
        #return a string with the tiles of all objects under the mouse
        (x, y) = (mouse.cx, mouse.cy)
     
#        tiles = [tile for tile in self.currentLevel.getTiles()
#            if tile.getX() == x and tile.getY() == y and self.currentLevel.isInFOV(x, y)]
#     
#        return tiles[0].getDescription()
        
        if x >= 0 and x < C.MAP_WIDTH and y >= 0 and y < C.MAP_HEIGHT:
#            print "Reading tile", (x, y)
#            G.game.message( "Reading tile " + str(x) + ", " + str(y) )
            tile = self.currentLevel.getTile(x, y)
            if self.currentLevel.isInFOV(x, y):
                return tile.getDescription()
            else:
                return ''
        
        else:
            return ''
        
    def gameLoop(self):
        
        while not libtcod.console_is_window_closed():
            
            player_action = None
            
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
            self.render_bar(1, 1, C.BAR_WIDTH, 'HP', 15, 20, libtcod.light_red, libtcod.darker_red)
            
            #display description of the tile under the mouse
            libtcod.console_set_default_foreground(self.panel, libtcod.light_gray)
            desc = self.getTileDescUnderMouse()
            if desc:
                libtcod.console_print_ex(self.panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, desc)
                    
            #blit the contents of "panel" to the root console
            libtcod.console_blit(self.panel, 0, 0, C.SCREEN_WIDTH, C.PANEL_HEIGHT, 0, C.PANEL_X, C.PANEL_Y)
            
            self.currentLevel.computeFOV(self.player.getX(), self.player.getY(), 0)

#            print "Drawing"
            self.currentLevel.draw()
    #        libtcod.console_blit(mapConsole, 0, 0, C.MAP_WIDTH, C.MAP_HEIGHT, 0, 0, 0)
            libtcod.console_blit(self.mapConsole, 0, 0, C.MAP_WIDTH, C.MAP_HEIGHT, 0, C.MAP_X, C.MAP_Y)
    
            libtcod.console_flush()
            
#            for cr in self.currentLevel.creatures:
#                cr.takeTurn()

            player_action = self.handleKeys(key)
            if player_action == 'exit':
                break
            
            elif player_action == 'took-turn':
                for cr in self.currentLevel.creatures:
                    if cr is not self.player:
                        cr.takeTurn()
            
#            self.player.takeTurn()
            
            self.currentLevel.clear()
            
            
        
    
    
    