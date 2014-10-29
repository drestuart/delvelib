'''
Created on Mar 12, 2013

@author: dstu
'''

import Const as C
import delvelibConst as DC
import colors
import Game as G
import keys
import pygcurse
import pygame
from pygame.locals import *
import sys
from PanelClass import *
import textwrap
from DungeonFeatureClass import downStair, upStair, Stair, Door
import database as db
import os.path
import TileClass as T
import MapTileClass as MT


fontpath = os.path.join("modules", "delvelib", "fonts", "FreeMono.ttf")

class UI(object):

    def __init__(self, **kwargs):
        self.currentLevel = kwargs.get('level', None)
        self.player = kwargs.get('player', None)
        self.fullscreen = kwargs.get('fullscreen', False)

        self.window = pygcurse.PygcurseWindow(C.SCREEN_WIDTH, C.SCREEN_HEIGHT, C.TITLE, #font = self.font,
                                              fgcolor = colors.colorDefaultFG, bgcolor = colors.colorDefaultBG,
                                              fullscreen = self.fullscreen)
        
        self.fontsize = kwargs.get('fontsize')
        self.font = kwargs.get('font')
        if self.font:
            fontpath = "modules/delvelib/fonts/" + self.font
        else:
            fontpath = None
            
        self.window.font = pygame.font.Font(fontpath, self.fontsize)
            
        self.window.autoblit = False
        self.window.autoupdate = False
        self.window.autodisplayupdate = False
        
        # Set up UI panels
        self.mapPanel = MapPanel(self.currentLevel, C.MAP_PANEL_DIMS, self.window)
        self.messagePanel = MessagePanel(C.MESSAGE_PANEL_DIMS, self.window)
        self.charPanel = CharacterPanel(C.CHAR_PANEL_DIMS, self.window)

        pygame.key.set_repeat(300, 150)
        
    def gameLoop(self):
        
        self.clock = pygame.time.Clock()
        
        # Draw UI panels
        self.clearScreen()
        self.charPanel.draw(self.player.getX(), self.player.getY(), self.currentLevel.getDepth())
        self.messagePanel.displayMessages()
        
        self.currentLevel.setupEventListeners()
        
        self.currentLevel.computeFOV(self.player.getX(), self.player.getY())
        self.drawLevel()
        self.drawWindow()
        
        # Set up a DRAWSCREEN heartbeat
        pygame.time.set_timer(DC.CHECKTILEDESC, DC.CHECKTILEDESCDELAY)
        
        pygame.event.set_blocked([MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, KEYUP])
        
        while True:
            # Handle framerate
            self.clock.tick(C.LIMIT_FPS)
            
            # get framerate with:
                #self.clock.get_fps()

#            print "Loop"

            for event in pygame.event.get(): #[QUIT, KEYDOWN, KEYUP, DC.DRAWSCREEN]
                
                redrawScreen = False
                
                if event.type == QUIT:
                    self.quit()
                
#                 elif event.type == MOUSEMOTION:
#                     desc = self.getTileDescUnderMouse()
#                     self.messagePanel.setSingleMessage(desc)
#                     redrawScreen = self.messagePanel.messageChanged

                elif event.type == KEYDOWN:
                    redrawScreen = True
                    
                    player_action = None
                    key = event.key
                    key_mods = pygame.key.get_mods()

                    player_action = self.handleKeys(key, event, key_mods)
                    
                    if player_action == 'exit':
                        print "Got a QUIT command"
                        pygame.quit()
                        sys.exit()
                    
                    elif player_action == 'took-turn':
                        for cr in self.currentLevel.creatures:
                            if cr is not self.player:
                                cr.takeTurn() 
                                
                elif event.type == DC.CHECKTILEDESC:
                    redrawScreen = False
                    
                # Check if there's a new tile description to show
                desc = self.getTileDescUnderMouse()
                
                self.messagePanel.setSingleMessage(desc)
                if self.messagePanel.messageChanged:
                    self.messagePanel.singleMessageShow()

                # Refresh window                
                if redrawScreen:
                    self.clearScreen()
                    self.charPanel.draw(self.player.getX(), self.player.getY(), self.currentLevel.getDepth())
                    self.messagePanel.displayMessages()
                    
#                     self.currentLevel.computeFOV(self.player.getX(), self.player.getY())
                    self.drawLevel()
                
                # Draw everything
                self.drawWindow()
    
    def quit(self):
        print "Got a QUIT event"
        pygame.quit()
        sys.exit()
    
    def drawWindow(self):
        self.window.update()
        self.window.blittowindow()
        
    def clearWindow(self):
        self.window.surface.fill((0,0,0))
        self.drawWindow()
        
    def showCenteredText(self, lines, showtime):
        pygame.event.clear()
        swidth = C.SCREEN_WIDTH
        clines = []
        
        for line in lines:
            clines.append(line.center(swidth))
        
        startingy = (C.SCREEN_HEIGHT - len(lines))/2
        y = startingy
        
        for line in clines:
            self.window.putchars(line, 0, y, colors.white, colors.blankBackground)
            y += 1
        
        self.drawWindow()
        
        waited = 0
        
        while waited <= showtime:
            waited += pygame.time.delay(20)
            if pygame.event.peek([KEYDOWN, KEYUP]):
                pygame.event.clear()
                self.clearWindow()
                return False
        
        return True
        
    
    def fadeInImage(self, imgpath, loadTime, alphaSteps):
        pygame.event.clear()
        alphaMax = 255
        fadeInDelay = int(loadTime/alphaSteps)
        
        # Load and scale the logo image
        image = pygame.image.load(imgpath).convert()
        imageWidth, imageHeight = image.get_width(), image.get_height()
        imageRatio = float(imageHeight)/imageWidth
        
        windowWidth, windowHeight = self.window.pixelsize
        
        newWidth = int(windowWidth*.9)
        newHeight = int(newWidth*imageRatio)
        
        image = pygame.transform.scale(image, (newWidth, newHeight))
        
        # Logo postioning -- centered
        logox, logoy = ((windowWidth - newWidth)/2, (windowHeight - newHeight)/2)
        
        # Fade in logo
        for i in range(alphaSteps):
            # Check for key events and end if detected
            if pygame.event.peek([KEYDOWN, KEYUP]):
                pygame.event.clear()
                self.clearWindow()
                return False
            
            self.window.surface.fill((0,0,0))
            
            alpha = i*alphaMax/alphaSteps
            image.set_alpha(alpha)
            
            self.window.surface.blit(image, (logox, logoy))
            self.drawWindow()
            pygame.time.delay(fadeInDelay)
        
        return True
    
    def singleChoiceMenu(self, title, options, width = C.MENU_WIDTH):
        
        menu = MenuPanel(self.window, options = options, width = width, title = title, shadow = pygcurse.SOUTHEAST)
        return menu.getSingleChoice()
        
    def displayTextWindow(self, title, x, y, width, lines):
#        raise Exception("Deprecated (displayTextWindow)")
        linesToDisplay = []
        for line in lines:
            wrappedLines = textwrap.wrap(line, width - 4)
            for wline in wrappedLines:
                wline = wline.ljust(width)
                linesToDisplay.append(wline)
                
        height = len(linesToDisplay) + 2 + 2*C.MENU_MARGIN
        
        # Attempt to center
        x = (C.SCREEN_WIDTH - width)/2
        y = (C.SCREEN_HEIGHT - height)/2
        
        box = pygcurse.PygcurseTextbox(self.window, (x, y, width, height), fgcolor='white', bgcolor='black', #border = '='
                                       wrap=True, margin=C.MENU_MARGIN, caption=title, shadow = pygcurse.SOUTHEAST)   
        
        box.text = "\n".join(linesToDisplay)
        
        for line in box.text.split("\n"):
            print "| " + line + " |"
        box.update()
        self.drawWindow()        
    
    def showPlayerInventory(self):
        title = C.PLAYER_INVENTORY_HEADER
        inv = self.player.getInventory()
        
        height = inv.length()
        
        lines = []
        
        for item in inv.getItems():
            text = item.getDescription()
            lines.append(text)
        
        self.displayTextWindow(title, C.MENU_X, C.MENU_Y, C.MENU_WIDTH, lines)
        
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
        
        index = self.singleChoiceMenu(header, lines, C.MENU_WIDTH)
        
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
        
        index = self.singleChoiceMenu(header, lines, C.MENU_WIDTH)
        
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
        
        index = self.singleChoiceMenu(header, lines, C.MENU_WIDTH)
        
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
        
        index = self.singleChoiceMenu(header, lines, C.MENU_WIDTH)
        
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
        
        index = self.singleChoiceMenu(header, lines, C.MENU_WIDTH)
        
        # Do nothing... yet
        return None
    
    
    def pickUpItemMenu(self, inventory):
        #show a singleChoiceMenu with each item of the inventory as an option
        if inventory.length() == 0:
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
        
    def handleKeys(self, key, event, key_mods):

        if key == K_ESCAPE:
            return "exit"
            
#        elif event.type == KEYUP:
        elif event.type == KEYDOWN:
            
            keyStr = pygame.key.name(key)
            direc = keys.getMovementDirection(key, keyStr)
            
            # Move
            if direc:
                dx, dy = direc
                
                # Move camera
                if (KMOD_CTRL & key_mods):
                    self.mapPanel.moveCamera(dx, dy)
                    return 'didnt-take-turn'
                    
                # Move player
                moveres = self.player.move(dx, dy)
                if moveres == True:
                    # Reset map camera
                    self.mapPanel.resetCameraOffset()
                    return 'took-turn'
                elif isinstance(moveres, MT.MapTile):
                    self.enterNewLevel(self.player, moveres)
 
            elif keyStr == '.': # Wait
                if (KMOD_SHIFT & key_mods): # '>' key
                    if self.takeStairs():
                        return 'took-turn'
                else:
                    G.message("Waiting")
                    return 'took-turn'
            
            elif keyStr == ',': # Pick up items
                if (KMOD_SHIFT & key_mods): # '<' key
#                     if self.goToPreviousLevel():
                    if self.takeStairs():
                        return 'took-turn'
                    
                else:
                    inv = self.player.getTile().getInventory()
                    if inv:
                        item = self.pickUpItemMenu(inv)
                        if item:
    #                        inv.removeItem(item)
                            self.player.pickUpItem(item)
                        
                        return 'took-turn'
                
            elif keyStr == 'c': # Close a door
                if self.closeAdjacentDoor(self.player):
                    return 'took-turn'
                return 'didnt-take-turn'
            
            elif keyStr == 'o': # Open a door 
                if self.openAdjacentDoor(self.player):
                    return 'took-turn'
                return 'didnt-take-turn'   
            
            elif keyStr == 'W':  # Wear something
                self.wearMenu()                
                return 'didnt-take-turn'
            
            elif keyStr == 'w':  # Wield something
                self.wieldMenu()                
                return 'didnt-take-turn'
                        
            elif keyStr == 'e':  # Eat something
                self.eatMenu()                
                return 'didnt-take-turn'
                            
            elif keyStr == 'i':
                self.showPlayerInventory()
                return 'didnt-take-turn'
            
        else:
            return 'didnt-take-turn'
    
    def message(self, newMsg):
        self.messagePanel.addMessage(newMsg)
        self.messagePanel.displayMessages()
        self.drawWindow()
        
    def getCurrentLevel(self):
        return self.currentLevel
    
    def setCurrentLevel(self, lvl):
        self.currentLevel = lvl
        self.mapPanel.setLevel(lvl)
        lvl.load()
        
    def getPlayer(self):
        return self.player
    
    def setPlayer(self, c):
        self.player = c
        
    def clearScreen(self):
        self.mapPanel.clear()
        self.messagePanel.clear()
        self.charPanel.clear()
        
    def drawLevel(self):
        # Get all tiles to draw from level class
        # TODO implement windowing for larger maps
        playerx, playery = self.player.getX(), self.player.getY()
        self.mapPanel.drawLevel(playerx, playery)
        
    def getTileDescUnderMouse(self):
    
        #return a string with the tiles of all objects under the mouse
        (mousex, mousey) = pygame.mouse.get_pos()
        
        # get cell coords
        (x, y) = self.window.getcoordinatesatpixel(mousex, mousey, onscreen=True)
     
        if (x, y) == (None, None):
            return ''
        
        # Check if the mouse is inside the map pane
        if self.mapPanel.containsPoint(x, y):
#            print "Reading tile", (x, y)
#            G.game.message( "Reading tile " + str(x) + ", " + str(y) )
            tile = self.currentLevel.getTile(x, y)
            if self.currentLevel.isInFOV(self.player.getX(), self.player.getY(), x, y):
                return tile.getDescription()
            else:
                return ''
        else:
            return ''
    
    def enterNewLevel(self, creature, tile):
        clevel = self.currentLevel
        toLevel = tile.getLevel()
        
        if not toLevel:
            return False
        
        db.saveDB.save(clevel)
        
        toLevel.load()
        self.setCurrentLevel(toLevel)
        toLevel.placeCreature(self.player, tile)
        toLevel.computeFOVProperties(True)
        
        return True
        
    def takeStairs(self):
        tile = self.player.getTile()
        
        if isinstance(tile, T.Tile):
            feature = tile.getFeature()
            
            if feature and isinstance(feature, Stair):
                if isinstance(feature, upStair):
                    G.message("Heading up the stairs!")
                elif isinstance(feature, downStair):
                    G.message("Heading down the stairs!")
                
                destination = feature.getDestination()
                return self.enterNewLevel(self.player, destination)
#                 if not destination:
#                     return False
#                 
#                 toLevel = destination.getLevel()
#                 
#                 if not toLevel:
#                     return False
#                 
#                 db.saveDB.save(clevel)
#                 
#                 toLevel.load()
#                 self.setCurrentLevel(toLevel)
#                 toLevel.placeCreature(self.player, destination)
#                 
#                 return True
        
        elif isinstance(tile, MT.MapTile):
            clevel = self.currentLevel
            toLevel = tile.getStartingLevel()
            
            if not toLevel:
                return False
                
            db.saveDB.save(clevel)
            
            toLevel.load()
            self.setCurrentLevel(toLevel)
            toLevel.placeCreatureAtEntrance(self.player)
            return True
            
        
        G.message("No stairs here!")
        return False
    
    
    def openAdjacentDoor(self, player):
        adjTiles = self.getCurrentLevel().getAdjacentTiles(player.getTile())
        doors = []
        
        for tile in adjTiles:
            feat = tile.getFeature()
            if feat and isinstance(feat, Door) and feat.isClosed():
                doors.append(feat)
        
        if len(doors) == 0:
            G.message("You don't see any closed doors nearby")
            return False
        
        elif len(doors) == 1:
            door = doors[0]
            door.open_()
            G.message("You open the door")
            return True
        
        else:
            G.message("In which direction?")
            key, keyStr = keys.waitForInput()
            direc = keys.getMovementDirection(key, keyStr)
            
            if direc:
                playerx, playery = player.getXY()
                doorx, doory = playerx + direc[0], playery + direc[1]
                
                for d in doors:
                    if d.getTile().getXY() == (doorx, doory):
                        d.open_()
                        G.message("You open the door")
                        return True
                G.message("You don't see a closed door there")
                return False
            else:
                return False
    
    
    def closeAdjacentDoor(self, player):
        adjTiles = self.getCurrentLevel().getAdjacentTiles(player.getTile())
        doors = []
        
        for tile in adjTiles:
            feat = tile.getFeature()
            if feat and isinstance(feat, Door) and feat.isOpen():
                doors.append(feat)
        
        if len(doors) == 0:
            G.message("You don't see any open doors nearby")
            return False
        
        elif len(doors) == 1:
            door = doors[0]
            door.close()
            G.message("You close the door")
            return True
        
        else:
            G.message("In which direction?")
            key, keyStr = keys.waitForInput()
            direc = keys.getMovementDirection(key, keyStr)
            
            if direc:
                playerx, playery = player.getXY()
                doorx, doory = playerx + direc[0], playery + direc[1]
                
                for d in doors:
                    if d.getTile().getXY() == (doorx, doory):
                        d.close()
                        G.message("You close the door")
                        return True
                G.message("You don't see an open door there")
                return False
            else:
                return False
    
    
    
    
    
    
