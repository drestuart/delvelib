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
import pygcurse
import pygame
from pygame.locals import *
from string import join
import sys
from pygcurse import PygcurseWindow


# TODO Abstract out all pygcurse calls into an interface class

class Panel(object):
    def __init__(self, dims, window, margin = 0):
        (self.x, self.y, self.width, self.height) = dims
        self.window = window
        self.margin = margin
        
        # TODO handle margin
        
    def putChars(self, chars, x, y, fgcolor = None, bgcolor = None, indent = False):
        # Add offset for this window
        cellx = x + self.x
        celly = y + self.y
        
        self.window.putChars(chars, cellx, celly, fgcolor, bgcolor, indent)
        
    def putChar(self, char, x, y, fgcolor = None, bgcolor = None, indent = False):
        # Add offset for this window
        cellx = x + self.x
        celly = y + self.y
        
        self.window.putChar(char, cellx, celly, fgcolor, bgcolor, indent)
        

class MessagePanel(Panel):
    # TODO implement multi-color messages
    def __init__(self, *args):
        super(MessagePanel, self).__init__(*args)
        self.messages = []
    
    def addMessage(self, message, color = colors.colorMessagePanelFG):
        #split the message if necessary, among multiple lines
        messageLines = textwrap.wrap(message, self.width)
     
        for line in messageLines:
            #if the buffer is full, remove the first line to make room for the new one
            if len(self.msgs) == self.height:
                del self.msgs[0]
     
            #add the new line as a tuple, with the text and the color
            self.messages.append( (line, color) )
            
            # TODO indent multiline messages
        
    def displayMessages(self):
        y = 0
        for (line, color) in self.messages:
            self.putChars(line, 0, y, color)
            y += 1
        
class CharacterPanel(Panel):
    def __init__(self, *args):
        super(CharacterPanel, self).__init__(*args)
        
    # TODO implement character panel rendering
    def render(self):
        pass



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

        # TODO let the currentLevel call some functions and we'll handle the actual drawing
        
        # TODO set FPS limit
        
        pygame.key.set_repeat(500, 250)
        
    def gameLoop(self):
        
        self.clock = pygame.time.Clock()
#        while not libtcod.console_is_window_closed():
        while True:
            for event in pygame.event.get():
                
                redrawMap = False
                
                # TODO check event type
                if event.type == MOUSEMOTION:
                    desc = self.getTileDescUnderMouse()
                    if desc:
                        pass
                        # TODO print tile description to screen

    #            libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse)
    #            libtcod.console_clear(self.mapConsole)
    
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
                    self.clearMap()
    #                self.currentLevel.clear()
    
                    
                    #prepare to render the GUI panel
                    libtcod.console_set_default_background(self.panel, libtcod.black)
                    libtcod.console_clear(self.panel)
                    
                    y = 1
                    for (line, color) in self.msgs:
                        libtcod.console_set_default_foreground(self.panel, color)
                        libtcod.console_print_ex(self.panel, C.MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
                        y += 1
                 
                    #show the player's stats
#                    self.render_bar(1, 1, C.BAR_WIDTH, 'HP', 15, 20, colors.lightRed, colors.darkRed)
                    self.charPanel.render()
                    
                    self.currentLevel.computeFOV(self.player.getX(), self.player.getY(), 0)
                    # TODO Draw the level map
                    self.drawLevel()
                
                
                # Draw everything
                #print "Drawing"
                self.window.blittowindow()
                
                # Handle framerate
                self.clock.tick(C.LIMIT_FPS)
                
                # get framerate with:
                #self.clock.get_fps()
                
                
    
    def singleChoiceMenu(self, title, options, width):
        # TODO implement with pygcurse textbox
        
        #calculate total height for the title (after auto-wrap) and one line per option
#        header_height = libtcod.console_get_height_rect(self.mapConsole, 0, 0, width, C.SCREEN_HEIGHT, title)
#        height = len(options) + header_height
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
        
    
    def render_bar(self, x, y, totalWidth, name, value, maximum, barColor, backColor):
        #render a bar (HP, experience, etc). first calculate the width of the bar
        barWidth = max( int(float(value) / maximum * totalWidth), totalWidth)
        raise Exception("NYI UIClass.renderBar")
     
#        #render the background first
#        libtcod.console_set_default_background(self.panel, backColor)
#        libtcod.console_rect(self.panel, x, y, totalWidth, 1, False, libtcod.BKGND_SCREEN)
#     
#        #now render the bar on top
#        libtcod.console_set_default_background(self.panel, barColor)
#        if barWidth > 0:
#            libtcod.console_rect(self.panel, x, y, barWidth, 1, False, libtcod.BKGND_SCREEN)
#            
#        #finally, some centered text with the values
#        libtcod.console_set_default_foreground(self.panel, libtcod.white)
#        libtcod.console_print_ex(self.panel, x + totalWidth / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
#            name + ': ' + str(value) + '/' + str(maximum))
        
    def message(self, newMsg, color = colors.white):
        # TODO Implement message bar in pygcurse
        
        self.messagePanel.addMessage(newMsg)
        
    
    
    

        
        
    def getCurrentLevel(self):
        return self.currentLevel
    
    def setCurrentLevel(self, lvl):
        self.currentLevel = lvl
#        self.currentLevel.setMapConsole(self.mapConsole)
        
    def clearMap(self):
        # TODO clear map pane with pygcurse
        raise Exception("NYI UIClass.clearMap()")
    
    def putChar(self, x, y, symbol, color, background):
        # TODO
        raise Exception("NYI UIClass.putChar()")
    
    def drawLevel(self):
        # TODO
        raise Exception("NYI UIClass.drawLevel()")
        
    def getTileDescUnderMouse(self):
#        global mouse
     
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
        
    
            
            
        
    
    
    