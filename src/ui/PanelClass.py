'''
Created on Jan 18, 2014

@author: dstu
'''

import Const as C
import delvelibColors as colors
from pygame.locals import *
import re
import textwrap
from symbols import *
import pygcurse
import Game as G
from OptionClass import OptionType
import pygame
from QuestClass import QuestStatus

fgdefault = colors.colorMessagePanelFG
bgdefault = colors.colorMessagePanelBG

class Panel(object):
    def __init__(self, dims, parentUI, margin = 0):
        (self.x, self.y, self.width, self.height) = dims
        self.margin = margin
        self.ui = parentUI
        
        # TODO handle margin
        
    def putChars(self, chars, x, y, fgcolor = None, bgcolor = None, indent = False):
        # Add offset for this window
        cellx = x + self.x
        celly = y + self.y
        self.ui.window.putchars(chars, cellx, celly, fgcolor, bgcolor)
        
    def putChar(self, char, x, y, fgcolor = None, bgcolor = None, indent = False):
        # Add offset for this window
        cellx = x + self.x
        celly = y + self.y
        self.ui.window.putchar(char, cellx, celly, fgcolor, bgcolor)
        
    def containsPoint(self, x, y):
        return (x >= self.x) and (x < self.x + self.width) and \
                (y >= self.y) and (y < self.y + self.height)
    
    def clear(self):
        self.ui.window.erase((self.x, self.y, self.width, self.height))

    def getLevel(self):
        return self.ui.getCurrentLevel()

class MessagePanel(Panel):
    def __init__(self, *args):
        super(MessagePanel, self).__init__(*args)
        self.messages = []
        self.singleMessage = ''
        self.messageWindowHeight = self.height - 2
        self.messageChanged = False
        self.lastMessageShown = 0
    
    def addMessage(self, message):

        colorpat = re.compile(r'(<.*?>)')
        m = re.search(colorpat, message)
            
        if not m:
            self.messages.append([(message, fgdefault, bgdefault)])
        
        else:
            chunks = re.split(colorpat, message)
            lines = [[]]
            fg = fgdefault
            bg = bgdefault
            charsAdded = 0
    
            while len(chunks) > 0:
                chunk = chunks.pop(0)
                colorspecpat = re.compile(r'^<(.*)>$')
                cm = re.search(colorspecpat, chunk)
                
                # If it's a normal word, add it to the message list
                if not cm:
                    if len(chunk) > 0:
                        words = chunk.split()
                        for word in words:
                            if len(word) + charsAdded > self.width:
                                charsAdded = 0
                                lines.append([])
                        
                            lines[-1].append( (word, fg, bg) )
                            charsAdded += len(word)
                
                else:
                    text = cm.groups()
                    
                    words = text[0].split()
                    
                    # Set fg and bg variables
                    fgpat = re.compile(r'fg=(.*)')
                    bgpat = re.compile(r'bg=(.*)')
                    tuplepat = re.compile(r'^\(.+\)$')
                    commapat = ','
                    
                    for word in words:
                        
                        if word == 'default':
                            fg = fgdefault
                            bg = bgdefault
                            continue
                        
                        fgm = re.match(fgpat, word)
                        if fgm:
                            fgStr = fgm.group(1)
                            
                            if re.match(tuplepat, fgStr):
                                # Convert to tuple
                                fg = tuple(int(s) for s in re.split(commapat, fgStr[1:-1]))
                            else:
                                # no tuple
                                fg = fgStr
                            
                            continue
                        
                        
                        bgm = re.match(bgpat, word)
                        if bgm:
                            bgStr = bgm.group(1)
                            
                            if re.match(tuplepat, bgStr):
                                # Convert to tuple
                                bg = tuple(int(s) for s in re.split(commapat, bgStr[1:-1]))
                            else:
                                # no tuple
                                bg = bgStr
                            
                            continue
                            
            self.messages += lines
    
    
    def setSingleMessage(self, message=''):
        # Fix to keep long messages from spilling over
        # TODO: something smarter
        if len(message) > self.width:
            message = message[:self.width]
        
        if message != self.singleMessage:
            self.singleMessageClear()
            self.singleMessage = message.ljust(self.width)
            self.messageChanged = True
        else:
            self.messageChanged = False
            
    def singleMessageClear(self):
        clearst = ' ' * self.width
        self.putChars(clearst, 0, 0, colors.blankBackground, colors.blankBackground)
        
    def singleMessageShow(self):
        # Show single-line message at the top of the panel
        self.putChars(self.singleMessage, 0, 0, colors.colorMapPanelFG, colors.colorMessagePanelBG)
        
    def crapBomb(self):
        for i in range(30):
            self.addMessage("Crap " + str(i))
        
    def displayMessages(self):
        self.singleMessageShow()

        while True:
            self.clear()
            paging = False
            numMessagesToShow = len(self.messages) - self.lastMessageShown - 1
            
            if numMessagesToShow > self.messageWindowHeight:
                messagesToShow = self.messages[self.lastMessageShown:self.lastMessageShown + self.messageWindowHeight]
                messagesToShow.append([("-- More --", fgdefault, bgdefault)]);
                paging = True
            else:
                messagesToShow = self.messages[-self.messageWindowHeight:]
                            
            y = 1
            for line in messagesToShow:
                charsPrinted = 0
                wordsPrinted = 0
                wordsInLine = 0

                for (text, fg, bg) in line:
                    wordsInLine += len(text.split())
                
                for (text, fg, bg) in line:
                    words = text.split()
                    
                    # TODO Maybe don't need this if the word-wrap code in addMessage() is working?
                    # Probably do need it to deal with different-colored words though
                    for word in words:
                        if len(word) + charsPrinted > self.width:
                            y += 1
                            charsPrinted = 0
                        
                        if wordsPrinted < wordsInLine - 1:
                            word = word + ' '
                            
                        self.putChars(word, charsPrinted, y, fgcolor=fg, bgcolor=bg)
                        charsPrinted += len(word)
                        wordsPrinted += 1
                        
                y += 1
            if paging:
                self.lastMessageShown += self.messageWindowHeight - 1
                self.ui.drawLevel()
                self.ui.drawWindow()
                self.ui.waitForInput()
                continue
            else:
                self.lastMessageShown = len(self.messages)
                break
        
class CharacterPanel(Panel):
    def __init__(self, *args):
        super(CharacterPanel, self).__init__(*args)
        
    def draw(self):
        maxHP = self.ui.player.getMaxHP()
        currentHP = self.ui.player.getHP()
                
        playerx, playery = self.ui.player.getXY()
        depth = self.getLevel().getDepth()
        
        self.render_bar(1, 1, 18, "HP", currentHP, maxHP, colors.darkBlue, colors.darkRed)
        if (G.getDebugValue("showCoords")):
            self.showCoords(1, 3, playerx, playery, depth)
        
    def showCoords(self, x, y, playerx, playery, depth):
        
        self.putChars("Position: " + str(playerx) + ", " + str(playery), x, y, fgcolor = colors.white, bgcolor = colors.black)
        self.putChars("Depth: " + str(depth), x, y+1, fgcolor = colors.white, bgcolor = colors.black)
    
    def render_bar(self, barx, bary, totalWidth, name, value, maximum, barColor, backColor):
        #draw a bar (HP, experience, etc). first calculate the width of the bar
        barWidth = min( int(float(value) / maximum * totalWidth), totalWidth)
     
        # Draw bar
        for x in range(barx, barx + totalWidth):
#            if x < self.x + barx + barWidth:
            if x < barx + barWidth:
                bg = barColor
            else:
                bg = backColor

#            self.ui.window.putchar(' ', x, self.y + bary, fgcolor = colors.white, bgcolor = bg)
            self.putChar(' ', x, bary, fgcolor = colors.white, bgcolor = bg)
            
        # Add text
        text = name + ' ' + str(value) + '/' + str(maximum)
        textx = barx + (totalWidth - len(text)) / 2
        
        self.putChars(text, textx, bary)


class MapPanel(Panel):
    def __init__(self, *args):
        super(MapPanel, self).__init__(*args)
        self.camx = 0
        self.camy = 0
        
        self.xoffset = 0
        self.yoffset = 0

    def moveCamera(self, dx, dy):
        self.xoffset += dx
        self.yoffset += dy
        
    def resetCameraOffset(self):
        self.xoffset = 0
        self.yoffset = 0
    
    def cameraDims(self):
        return self.camx, self.camy, self.width, self.height
    
    def positionCamera(self, playerx, playery):
        
        lwidth = self.getLevel().getWidth()
        lheight = self.getLevel().getHeight()
        
        lcenterx = int(lwidth/2)
        lcentery = int(lheight/2)
        
        xmin = 0
        ymin = 0
        
        xmax = lwidth - self.width
        ymax = lheight - self.height 
                
        # If the level is smaller than the map panel, just center the whole thing
        if lwidth <= self.width:
            self.camx = lcenterx - int(self.width/2)
        
        # Otherwise center on the player's position
        else:
            self.camx = playerx - int(self.width/2)
            self.camx = min(xmax, max(xmin, self.camx))
            
            # Add offset
            self.camx += self.xoffset
            self.camx = min(xmax, max(xmin, self.camx))
        
        
        # Do it again for the y coordinate
        if lheight <= self.height:
            self.camy = lcentery - int(self.height/2)
        else:
            self.camy = playery - int(self.height/2) 
            self.camy = min(ymax, max(ymin, self.camy))
            self.camy += self.yoffset
            self.camy = min(ymax, max(ymin, self.camy))
            
    
    def drawLevel(self, playerx, playery):
        debug = G.getDebugValue("showPaths")
        
        # Set camera position
        self.positionCamera(playerx, playery)
        
        # Get tiles
        tilesToDraw = self.getLevel().getTilesToDraw(playerx, playery, self.cameraDims())
        
        # Draw monster paths
        if debug:
            creaturePathTiles = []
            for cr in self.getLevel().getLivingCreatures():
                path = cr.getPath()
                if path:
                    creaturePathTiles += path


        for (x, y, symbol, color, background) in tilesToDraw:
            if debug:
                if (x, y) in creaturePathTiles:
                    color = colors.colorDebugPath
            self.putChar(symbol, x - self.camx, y - self.camy, color, background)
            
    def getTileDescription(self, x, y):
        
        if self.containsPoint(x, y):
            mapx, mapy = x + self.camx, y + self.camy
            player = G.game.getPlayer()
            
            if mapx < 0 or mapy < 0 or mapx >= self.getLevel().getWidth() or mapy >= self.getLevel().getHeight():
                return ''
            
            tile = self.getLevel().getTile(mapx, mapy)
            if tile is None:
                return ''
            elif self.getLevel().isInFOV(player.getX(), player.getY(), mapx, mapy):
                return tile.getDescription()# + " " + str((tile.getXY()))+ " " + str(self.getLevel().astar.getMovable(*tile.getXY()))
            else:
                return ''
        else:
            return ''

class MenuWindow(Panel):
    def __init__(self, *args, **kwargs):
        super(MenuWindow, self).__init__((0, 0, kwargs['width'], 0), *args)
        
        self.selected = [0]
        
        self.title = kwargs['title']
        self.margin = kwargs.get('margin', C.MENU_MARGIN)
        
        self.defaultFGColor = kwargs.get('defaultFGColor', C.MENU_TEXT_COLOR)
        
        self.selectedBGColor = kwargs.get('selectedBGColor', C.MENU_SELECTED_COLOR)
        self.defaultBGColor = kwargs.get('defaultBGColor', C.MENU_UNSELECTED_COLOR)
        
        self.tbBorder = kwargs.get('tbBorder', '-')
        self.lrBorder = kwargs.get('lrBorder', '|')
        self.multilineIndent = kwargs.get('multilineIndent', 1)
        
        self.shadow = kwargs.get('shadow', None)
        self.shadowamount = kwargs.get('shadowamount', 51)
        self.shadowx, self.shadowy = kwargs.get('shadowx', 1), kwargs.get('shadowy', 1)
        
        if kwargs.get('options'):
            self.setupOptions(kwargs['options'])
        
        self.titleLine = self.title.center(self.width, self.tbBorder)
        
    def setupOptions(self, options):
        self.options = options
        
        # Set up word wrap
        self.linesToDisplay = {}
        optNum = 0
        self.height = 2*(self.margin + 1)
        letter_index = ord('a')
        textWidth = self.width - 2*(self.margin + 1)
        
        for line in self.options:
            # Add letters
            line = '(' + chr(letter_index) + ') ' + line
            
            self.linesToDisplay[optNum] = []
            wrappedLines = textwrap.wrap(line, textWidth)
            linesForOption = 0
            
            for wline in wrappedLines:
                
                if linesForOption > 0:
                    wline = ' ' * self.multilineIndent + wline.ljust(textWidth - self.multilineIndent)
                else:
                    wline = wline.ljust(textWidth)
                    
                self.linesToDisplay[optNum].append(wline)
                self.height += 1
                linesForOption += 1
                
            optNum += 1
            letter_index += 1
                
#        self.height = len(self.linesToDisplay) + 2*(self.margin + 1)
        
        self.x = (C.SCREEN_WIDTH - self.width)/2
        self.y = (C.SCREEN_HEIGHT - self.height)/2
        
        return self.linesToDisplay
    
    def getUserInput(self):
        key, keyStr = self.ui.waitForInput()
        
        if key is None:
            return None
     
        elif key in [K_KP2, K_DOWN, K_j]:
            return 'down'
        
        elif key in [K_KP8, K_UP, K_k]:
            return 'up'
        
        elif key in [K_KP4, K_LEFT, K_h]:
            return 'left'
        
        elif key in [K_KP6, K_RIGHT, K_l]:
            return 'right'
        
        elif key in [K_RETURN, K_KP_ENTER, K_COMMA, K_SPACE]:
            return 'select'

        elif key == K_ESCAPE:
            return 'escape'

        else:
            pygame.event.clear()
            return None

    def getSingleChoice(self):
        
        while True:
            self.draw()
            uinput = self.getUserInput()
            
            if uinput is None:
                continue
         
            elif uinput == 'down':
                self.selected[0] += 1
                if self.selected[0] >= len(self.options):
                    self.selected[0] = 0
                continue
            
            elif uinput == 'up':
                self.selected[0] -= 1
                if self.selected[0] < 0:
                    self.selected[0] = len(self.options) - 1
                continue
            
            elif uinput == 'select':
                return self.selected[0]
            
            elif uinput == 'escape':
                return None

            # TODO: Add support for selection by key letter

            else:
                continue
            
    def getMultiChoice(self):
        pass
        # TODO

    def draw(self, highlightSelected=True):
        self.setUpWindow()

        # print options
        y = self.margin + 1
        for key in sorted(self.linesToDisplay.keys()):
            if highlightSelected and key in self.selected:
                bg = self.selectedBGColor
            else:
                bg = self.defaultBGColor
            
            lines = self.linesToDisplay[key]
            for line in lines:
                self.putLine(line, y, self.defaultFGColor, bg)
                y += 1
            
        # Draw shadow
        if self.shadow is not None:
            self.ui.window.addshadow(amount=self.shadowamount, region=(self.x, self.y, self.width, self.height), offset=None, direction=self.shadow, xoffset=self.shadowx, yoffset=self.shadowy)
            self.shadow = None # Only draw once
        
        self.ui.drawWindow()
        
    def setUpWindow(self):
        # Start by filling in blank background
        for y in range(self.height):
            self.putChars(" " * self.width, 0, y, self.defaultFGColor, self.defaultBGColor)

        # print top and bottom borders and title
        self.putChars(self.titleLine, 0, 0, fgcolor = self.defaultFGColor, bgcolor = self.defaultBGColor)
        self.putChars(self.tbBorder * self.width, 0, self.height - 1, fgcolor = self.defaultFGColor, bgcolor = self.defaultBGColor)
        
        # Draw margin lines
        for i in range(self.margin):
            # Side borders
            # Top left
            self.putChars(self.lrBorder + " " * self.margin, 0, i + 1, fgcolor = self.defaultFGColor, bgcolor = self.defaultBGColor)
            # Top right
            self.putChars(" " * self.margin + self.lrBorder, self.width - self.margin - 1, i + 1, fgcolor = self.defaultFGColor, bgcolor = self.defaultBGColor)
            # Bottom left
            self.putChars(self.lrBorder + " " * self.margin, 0, self.height - 2 - i, fgcolor = self.defaultFGColor, bgcolor = self.defaultBGColor)
            # Bottom right
            self.putChars(" " * self.margin + self.lrBorder, self.width - self.margin - 1, self.height - 2 - i, fgcolor = self.defaultFGColor, bgcolor = self.defaultBGColor)

        # Draw shadow
        if self.shadow is not None:
            self.ui.window.addshadow(amount=self.shadowamount, region=(self.x, self.y, self.width, self.height), offset=None, direction=self.shadow, xoffset=self.shadowx, yoffset=self.shadowy)
            self.shadow = None # Only draw once

        
    def putLine(self, line, y, fg, bg):
        # print side borders
        self.putChars(self.lrBorder + " " * self.margin, 0, y, fgcolor = self.defaultFGColor, bgcolor = self.defaultBGColor)
        self.putChars(" " * self.margin + self.lrBorder, self.width - self.margin - 1, y, fgcolor = self.defaultFGColor, bgcolor = self.defaultBGColor)
        
        # print text
        self.putChars(line, self.margin + 1, y, fgcolor=fg, bgcolor=bg)
        
class InventoryWindow(MenuWindow):

    def __init__(self, player, *args, **kwargs):
        super(InventoryWindow, self).__init__(*args, title=C.PLAYER_INVENTORY_HEADER,
                                              shadow=pygcurse.SOUTHEAST, **kwargs)

        inv = player.getInventory()
        self.height = inv.length()

        options = []

        for item in inv.getItems():
            text = item.getDescription()
            options.append(text)

        self.setupOptions(options)

    def setupOptions(self, options):
        self.options = options
        self.height = 2*(self.margin + 1)

        # Pad an empty inventory to show something
        if not options:
            self.linesToDisplay = {0 : [""]}
            self.height += 1

        else:
            # Set up word wrap
            self.linesToDisplay = {}
            optNum = 0
            textWidth = self.width - 2*(self.margin + 1)

            for line in self.options:
                self.linesToDisplay[optNum] = []
                wrappedLines = textwrap.wrap(line, textWidth)
                linesForOption = 0

                for wline in wrappedLines:
                    if linesForOption > 0:
                        wline = ' ' * self.multilineIndent + wline.ljust(textWidth - self.multilineIndent)
                    else:
                        wline = wline.ljust(textWidth)

                    self.linesToDisplay[optNum].append(wline)
                    self.height += 1
                    linesForOption += 1

                optNum += 1

        self.x = (C.SCREEN_WIDTH - self.width)/2
        self.y = (C.SCREEN_HEIGHT - self.height)/2

        return self.linesToDisplay

    def show(self):
        self.draw(highlightSelected=False)
        self.getUserInput()

class GameMenuWindow(MenuWindow):
    
    def __init__(self, *args, **kwargs):
        super(GameMenuWindow, self).__init__(*args, **kwargs)
        
        self.enabledFGColor = kwargs.get('enabledFGColor', C.MENU_TEXT_COLOR)
        self.disabledFGColor = kwargs.get('disabledFGColor', C.MENU_DISABLED_TEXT_COLOR)
        self.shadow = None
        
        self.selected = 0
        
    def setupOptions(self, options):
        self.options = options
        
        # Set up word wrap
        self.linesToDisplay = {}
        optNum = 0
        self.height = 2*(self.margin + 1)
        textWidth = self.width - 2*(self.margin + 1)
        
        for opt in self.options:
            # Data type check
            if not isinstance(opt, dict):
                raise ValueError("GameMenuWindow options must be dictionaries")
            
            text = opt.get('text')
            enabled = opt.get('enabled')
            function = opt.get('function')
            
            if text is None or not isinstance(text, basestring):
                raise ValueError("GameMenuWindow options must have 'text' string parameter")
            
            if enabled is None or not isinstance(enabled, bool):
                raise ValueError("GameMenuWindow options must have 'enabled' boolean parameter")

            if enabled and (function is None or not hasattr(function, '__call__')): # Best method check I could come up with
                raise ValueError("GameMenuWindow options must have 'function' method parameter")
            
            self.linesToDisplay[optNum] = []
            wrappedLines = textwrap.wrap(text, textWidth)
            linesForOption = 0
            
            for wline in wrappedLines:
                
                if linesForOption > 0:
                    wline = ' ' * self.multilineIndent + wline.ljust(textWidth - self.multilineIndent)
                else:
                    wline = wline.ljust(textWidth)
                    
                self.linesToDisplay[optNum].append(wline)
                self.height += 1
                linesForOption += 1
                
            optNum += 1
                
        self.x = (C.SCREEN_WIDTH - self.width)/2
        self.y = (C.SCREEN_HEIGHT - self.height)/2
        
        
    def draw(self):
        self.setUpWindow()
        
        # print options
        y = self.margin + 1
        for key in sorted(self.linesToDisplay.keys()):
            option = self.options[key]
            fg = self.disabledFGColor
            bg = self.defaultBGColor

            if key == self.selected:
                bg = self.selectedBGColor
            
            if option['enabled']:
                fg = self.enabledFGColor

            lines = self.linesToDisplay[key]
            for line in lines:
                self.putLine(line, y, fg, bg)
                y += 1
            
        # Draw shadow
        if self.shadow is not None:
            self.ui.window.addshadow(amount=self.shadowamount, region=(self.x, self.y, self.width, self.height), offset=None, direction=self.shadow, xoffset=self.shadowx, yoffset=self.shadowy)
            self.shadow = None # Only draw once
        
        self.ui.drawWindow()
        
    def getSingleChoice(self):
        while True:
            self.draw()
            uinput = self.getUserInput()
            
            if uinput is None:
                continue
         
            elif uinput == 'down':
                while True:
                    self.selected += 1
                    if self.selected >= len(self.options):
                        self.selected = 0
                        
                    newOption = self.options[self.selected]
                    if newOption['enabled']: break
                    
                continue
            
            elif uinput == 'up':
                while True:
                    self.selected -= 1
                    if self.selected < 0:
                        self.selected = len(self.options) - 1
                    
                    newOption = self.options[self.selected]
                    if newOption['enabled']: break
                    
                continue
            
            elif uinput == 'select':
                return self.options[self.selected]['function']
            
            else:
                continue
            
class EscapeMenuWindow(GameMenuWindow):

    def __init__(self, *args, **kwargs):
        super(EscapeMenuWindow, self).__init__(*args, **kwargs)
        self.shadow = kwargs.get('shadow', pygcurse.SOUTHEAST)

    def getSingleChoice(self):
        while True:
            self.draw()
            uinput = self.getUserInput()

            if uinput is None:
                continue

            elif uinput == 'down':
                while True:
                    self.selected += 1
                    if self.selected >= len(self.options):
                        self.selected = 0

                    newOption = self.options[self.selected]
                    if newOption['enabled']: break

                continue

            elif uinput == 'up':
                while True:
                    self.selected -= 1
                    if self.selected < 0:
                        self.selected = len(self.options) - 1

                    newOption = self.options[self.selected]
                    if newOption['enabled']: break

                continue

            elif uinput == 'select':
                return self.options[self.selected]['function']

            elif uinput == 'escape':
                return None

            else:
                continue

class ConversationWindow(MenuWindow):
    
    def __init__(self, *args, **kwargs):
        super(ConversationWindow, self).__init__(*args, **kwargs)
        self.selected = 0
        self.conversationTree = kwargs['tree']
        self.shadow = kwargs.get('shadow', pygcurse.SOUTHEAST)
        
    def doConversation(self):
        # Start with the first node on the tree
        self.currentNode = None
        node = self.conversationTree.getFirstNode()
        
        while True:
            self.draw(node)
            uinput = self.getUserInput()
            
            if uinput is None:
                continue
         
            elif uinput == 'down':
                self.selected += 1
                if self.selected >= len(node.options):
                    self.selected = 0
                continue
            
            elif uinput == 'up':
                self.selected -= 1
                if self.selected < 0:
                    self.selected = len(node.options) - 1
                continue
            
            elif uinput == 'select':
                selectedOption = node.options[self.selected]
                if selectedOption.callback:
                    selectedOption.callback()

                if selectedOption.nextNode:
                    node = selectedOption.nextNode
                    self.selected = 0
                    continue
                else:
                    break
            
            else:
                continue

    def draw(self, node):
        # Word wrapping
        self.setupPanel(node)
        self.setUpWindow()
                
        # Draw conversation text for this node
        y = self.margin + 1
        for line in self.textLines:
            self.putLine(line, y, self.defaultFGColor, self.defaultBGColor)
            y += 1

        # Skip a line
        self.putLine("", y, self.defaultFGColor, self.defaultBGColor)
        y += 1

        # Draw options for this node
        for key in sorted(self.optionLines.keys()):
            if key == self.selected:
                bg = self.selectedBGColor
            else:
                bg = self.defaultBGColor
            
            lines = self.optionLines[key]
            for line in lines:
                self.putLine(line, y, self.defaultFGColor, bg)
                y += 1
        
        self.ui.drawWindow()
            
    def setupPanel(self, node):
        # Skip this if we've already set up this node
        if self.currentNode is node:
            return
        
        self.height = 2*self.margin + 2 + 1 # 2 for the border, 1 for the space between text and opts
        text, options = node.getTextAndOptions()
        
        # Set up the conversation text
        self.textLines = textwrap.wrap(text, self.width - 2*(self.margin + 1))
        self.height += len(self.textLines)

        # Set up word wrap for conversation options
        self.optionLines = {}
        optNum = 0
        
        for opt in options:
            # Add letters
            line = '(' + chr(ord('a') + optNum) + ') ' + opt
            
            self.optionLines[optNum] = []
            wrappedLines = textwrap.wrap(line, self.width - 2*(self.margin + 1))
            linesForOption = 0
            
            for wline in wrappedLines:
                
                if linesForOption > 0:
                    wline = ' ' * self.multilineIndent + wline.ljust(self.width - 2*(self.margin + 1) - self.multilineIndent)
                else:
                    wline = wline.ljust(self.width - 2*(self.margin + 1))
                    
                self.optionLines[optNum].append(wline)
                self.height += 1
                linesForOption += 1
                
            optNum += 1
                
        self.x = (C.SCREEN_WIDTH - self.width)/2
        self.y = (C.SCREEN_HEIGHT - self.height)/2
        
        self.currentNode = node

class OptionWindow(MenuWindow):
    # For toggle and integer, deal with string TODO
    maxOptionWidth = 5
    
    def __init__(self, *args, **kwargs):
        super(OptionWindow, self).__init__(*args, **kwargs)
        self.shadow = kwargs.get('shadow', pygcurse.SOUTHEAST)
        self.selected = 0
        
    def doMenuStuff(self):
        while True:
            currentOption = self.options[self.selected]
            self.draw()
            uinput = self.getUserInput()
            
            if uinput is None:
                continue
         
            elif uinput == 'down':
                self.selected += 1
                if self.selected >= len(self.options):
                    self.selected = 0
                continue

            elif uinput == 'up':
                self.selected -= 1
                if self.selected < 0:
                    self.selected = len(self.options) - 1
                continue

            elif uinput == 'select':
                # TODO
                pass

            elif uinput == 'escape':
                return self.options

            elif currentOption.optionType == OptionType.STRING:
                # TODO
                pass

            elif currentOption.optionType == OptionType.TOGGLE:
                if uinput in ('left', 'right'):
                    currentOption.setValue(not currentOption.value)
                    continue

            elif currentOption.optionType == OptionType.INTEGER:
                val = currentOption.value
                if uinput == 'left':
                    currentOption.setValue(val - 1) # Bounds checking happens in setValue()
                elif uinput == 'right':
                    currentOption.setValue(val + 1)
                continue

            else:
                continue

    def draw(self):
        self.setUpWindow()

        y = self.margin + 1
        for key in sorted(self.linesToDisplay.keys()):
            option = self.options[key]
            fg = self.defaultFGColor
            bg = self.defaultBGColor

            if key == self.selected:
                bg = self.selectedBGColor
            
            lines = self.linesToDisplay[key]
            for line in lines:
                if line is lines[0]:
                    line += self.getOptionString(option)
                self.putLine(line, y, fg, bg)
                y += 1
                
        # Draw shadow
        if self.shadow is not None:
            self.ui.window.addshadow(amount=self.shadowamount, region=(self.x, self.y, self.width, self.height), offset=None, direction=self.shadow, xoffset=self.shadowx, yoffset=self.shadowy)
            self.shadow = None # Only draw once
        
        self.ui.drawWindow()
        
    def getOptionString(self, option):
        if option.optionType == OptionType.TOGGLE:
            if option.value:
                val = option.trueText
            else:
                val = option.falseText
        
        elif option.optionType == OptionType.INTEGER:
            val = str(option.value).rjust(self.maxOptionWidth - 2)
            # Add left/right arrows if appropriate
            if option.value > option.min:
                val = leftArrow + val

            if option.value < option.max:
                val += rightArrow
            else:
                val += " "
        
        elif option.optionType == OptionType.STRING:
            # TODO
            val = option.value
        
        return val.rjust(self.maxOptionWidth)
        
    def setupOptions(self, options):
        # Options should be a list of dictionaries with keys as follows:
        #     Text: The option text
        #     Type: The option type. Toggle, integer, string
        #     Value: The starting value
        #     Min, max: for integer only
        self.options = options
        
        # Fill in current state of the options
        self.state = {}
        for opt in self.options:
            self.state[opt.name] = opt.value
            
        # Format the options text for display
        self.linesToDisplay = {}
        optNum = 0
        self.height = 2*(self.margin + 1)
        textWidth = self.width - 2*(self.margin + 1)
        
        for opt in self.options:
            self.linesToDisplay[optNum] = []
            text = opt.text
            
            wrappedLines = textwrap.wrap(text, textWidth - self.maxOptionWidth)
            
            for wline in wrappedLines:
                wline = wline.ljust(textWidth - self.maxOptionWidth)
                    
                self.linesToDisplay[optNum].append(wline)
                self.height += 1
                
            optNum += 1

        self.x = (C.SCREEN_WIDTH - self.width)/2
        self.y = (C.SCREEN_HEIGHT - self.height)/2
        
        return self.linesToDisplay

class QuestWindow(MenuWindow):
    def __init__(self, *args, **kwargs):
        super(QuestWindow, self).__init__(*args, title=C.QUEST_WINDOW_HEADER,
                                      shadow=pygcurse.SOUTHEAST, **kwargs)
        self.quests = G.getQuests()
        self.setup()

    def show(self):
        self.draw(highlightSelected=False)
        self.getUserInput()
        
    def setup(self):
        self.height = 2*(self.margin + 1)
        
        self.questsToShow = []
        
        for q in self.quests:
            status = q.getStatus()
            if status == QuestStatus.NOT_STARTED or status == QuestStatus.RETURNED:
                continue
            self.questsToShow.append(q)
        
        # Pad an empty quest list to show something
        if not self.questsToShow:
            self.linesToDisplay = {0 : ["No quests".center(self.width - 2*self.margin - 2)]}
            self.height += 1
        
        else:
            # Set up word wrap
            self.linesToDisplay = {}
            optNum = 0
            
            for q in self.questsToShow:
                textWidth = C.QUEST_WINDOW_NAME_COLUMN_WIDTH

                self.linesToDisplay[optNum] = []
                questNameLines = textwrap.wrap(q.getName(), textWidth)
                linesForOption = 0

                for wline in questNameLines:
                    if linesForOption > 0:
                        wline = ' ' * self.multilineIndent + wline.ljust(textWidth - self.multilineIndent)
                        wline += ' ' * self.margin + '|'
                    else:
                        wline = wline.ljust(textWidth)
                        # Add quest status line
                        wline += ' ' * self.margin + '|' + ' ' * self.margin + q.getStatusString()

                    self.linesToDisplay[optNum].append(wline)
                    self.height += 1
                    linesForOption += 1

                optNum += 1
        
        self.x = (C.SCREEN_WIDTH - self.width)/2
        self.y = (C.SCREEN_HEIGHT - self.height)/2
        
        return self.linesToDisplay
    
#     def draw(self):
#         pass