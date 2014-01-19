'''
Created on Mar 12, 2013

@author: dstu
'''

from Import import *
import Const as C
import colors
import Game as G
import keys
import pygcurse
import pygame
from pygame.locals import *
import sys
from PanelClass import *

# TODO Abstract out all pygcurse calls into an interface class

class UI(object):

    def __init__(self, **kwargs):
        self.currentLevel = kwargs.get('level', None)
        self.player = kwargs.get('player', None)
        self.fullscreen = kwargs.get('fullscreen', False)
        self.font = kwargs.get('font', None)

        self.window = pygcurse.PygcurseWindow(C.SCREEN_WIDTH, C.SCREEN_HEIGHT, C.TITLE, font = self.font,
                                              fgcolor = colors.colorDefaultFG, bgcolor = colors.colorDefaultBG,
                                              fullscreen = self.fullscreen)
        self.window.autoblit = False
        
        # Set up UI panels
        self.mapConsole = Panel(C.MAP_PANEL_DIMS, self.window)
        self.messagePanel = MessagePanel(C.MESSAGE_PANEL_DIMS, self.window)
        self.charPanel = CharacterPanel(C.CHAR_PANEL_DIMS, self.window)

        pygame.key.set_repeat(500, 250)
        
    def gameLoop(self):
        
        self.clock = pygame.time.Clock()
#        while not libtcod.console_is_window_closed():
        while True:
            for event in pygame.event.get():
                
                redrawMap = False
                
                if event.type == MOUSEMOTION:
                    desc = self.getTileDescUnderMouse()
                    if desc:
                        pass
                        # TODO print tile description to screen

                elif event.type in (KEYDOWN, KEYUP):
                    redrawMap = True
                    
                    player_action = None
                    key = event.key
                    player_action = self.handleKeys(key)
                    if player_action == 'exit':
                        print "Got a QUIT command"
                        pygame.quit()
                        sys.exit()
                    
                    elif player_action == 'took-turn':
                        for cr in self.currentLevel.creatures:
                            if cr is not self.player:
                                cr.takeTurn() 
                
                if redrawMap:
    
                    self.charPanel.draw()
                    self.messagePanel.displayMessages()
                    
                    self.currentLevel.computeFOV(self.player.getX(), self.player.getY(), 0)
                    self.clearMap()
                    self.drawLevel()
                
                
                # Draw everything
                #print "Drawing"
                self.window.blittowindow()
                
                # Handle framerate
                self.clock.tick(C.LIMIT_FPS)
                
                # get framerate with:
                #self.clock.get_fps()
        self.window.update()
    
    def singleChoiceMenu(self, title, options, width):

        height = len(options)
        
        lines = []
        letter_index = ord('a')
        for option in options:
            text = '(' + chr(letter_index) + ') ' + option
            lines.append(text)
            letter_index += 1

        self.displayTextWindow(title, C.MENU_X, C.MENU_Y, C.MENU_WIDTH, height, lines)
        
        key, keyStr = keys.waitForInput()
     
        #convert the ASCII code to an index; if it corresponds to an option, return it
        index = key - ord('a')
        if index >= 0 and index < len(options): 
            return index
        
        return None
    
    def displayTextWindow(self, title, x, y, width, height, lines):
#        window = libtcod.console_new(width, height + 2)
        
        box = pygcurse.PygcurseTextbox(self.window, (x, y, width, height), fgcolor='white', bgcolor='black', 
                                       border='=', wrap=True, margin=1, caption=title)
        box.text = "\n".join(lines)
        box.update()
        
#        libtcod.console_set_default_foreground(window, libtcod.white)
        
#        def addBorder(line):
#            line = line.ljust(width - 4)
#            line = "= " + line + " ="
#            return line
#        
#        title = addBorder(title)
#        
#        libtcod.console_print_ex(window, 0, 0, libtcod.BKGND_NONE, libtcod.LEFT, "="*width)
#        libtcod.console_print_rect_ex(window, 0, 1, width, height + 2, libtcod.BKGND_NONE, libtcod.LEFT, title)
#        
#        header_height = libtcod.console_get_height_rect(self.mapConsole, 0, 0, width, C.SCREEN_HEIGHT, title)
#        
#        # Print each line
#        y = header_height + 1
#        for line in lines:
#            # Formatting
#            line = addBorder(line)
#            
#            libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
#            y += 1
#        
#        libtcod.console_print_ex(window, 0, height + 1 , libtcod.BKGND_NONE, libtcod.LEFT, "="*width)
#        
#        libtcod.console_blit(window, 0, 0, width, height + 2, 0, C.MENU_X, C.MENU_Y, 1.0, 0.7)
#        libtcod.console_flush()
        
    
    def showPlayerInventory(self):
        title = C.PLAYER_INVENTORY_HEADER
        inv = self.player.getInventory()
        
#        header_height = libtcod.console_get_height_rect(self.mapConsole, 0, 0, C.MENU_WIDTH, C.SCREEN_HEIGHT, title)
        height = inv.length()
        
        lines = []
        
        for item in inv.getItems():
            text = item.getDescription()
            lines.append(text)
        
        self.displayTextWindow(title, C.MENU_X, C.MENU_Y, C.MENU_WIDTH, height, lines)
        
#        key = libtcod.console_wait_for_keypress(True)
        key, keyStr = keys.waitForInput()
        
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
     
        if key == K_ESCAPE:
            return "exit"
            
        elif key.pressed:
            
            direc = keys.getMovementDirection(key)
            
            keyStr = pygame.key.name(key)
            
            # Move
            if direc:
                dx, dy = direc
                if self.player.move(dx, dy):
                    return 'took-turn'
 
            elif key.vk == K_KP_PERIOD or keyStr == '.': # Wait
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
        raise Exception("Deprecated UI.handleKeysOld")
#         if key.vk == libtcod.KEY_ESCAPE:
#             return 'exit'  #exit game
#         else:
#             return self.player.AI.takeTurn(key)
        
    

        
    def message(self, newMsg):
        self.messagePanel.addMessage(newMsg)
        
    def getCurrentLevel(self):
        return self.currentLevel
    
    def setCurrentLevel(self, lvl):
        self.currentLevel = lvl
        
    def clearMap(self):
        # TODO clear map pane with pygcurse
#        raise Exception("NYI UIClass.clearMap()")
        pass # Is this a thing we need?
    
    def drawLevel(self):
        # Get all tiles to draw from level class
        # TODO implement windowing for larger maps
        tilesToDraw = self.currentLevel.getTilesToDraw()
        
        for (x, y, symbol, color, background) in tilesToDraw:
            self.mapConsole.putChar(symbol, x, y, color, background)
        
        
    def getTileDescUnderMouse(self):
     
        #return a string with the tiles of all objects under the mouse
        (mousex, mousey) = pygame.mouse.get_pos()
        
        # get cell coords
        (x, y) = self.window.getcoordinatesatpixel(mousex, mousey, withinBoundaries=True)
     
#        tiles = [tile for tile in self.currentLevel.getTiles()
#            if tile.getX() == x and tile.getY() == y and self.currentLevel.isInFOV(x, y)]
#     
#        return tiles[0].getDescription()
        
#        if x >= 0 and x < C.MAP_WIDTH and y >= 0 and y < C.MAP_HEIGHT:
        # Check if the mouse is inside the map pane
        if self.mapConsole.collidepoint(mousex, mousey):
#            print "Reading tile", (x, y)
#            G.game.message( "Reading tile " + str(x) + ", " + str(y) )
            tile = self.currentLevel.getTile(x, y)
            if self.currentLevel.isInFOV(x, y):
                return tile.getDescription()
            else:
                return ''
        else:
            return ''
        
    
            
            
        
    
    
    