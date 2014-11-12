'''
Created on Jan 18, 2014

@author: dstu
'''

import Const as C
import colors
import keys
from pygame.locals import *
import re
import textwrap
from symbols import *
import Game as G

fgdefault = colors.colorMessagePanelFG
bgdefault = colors.colorMessagePanelBG

__all__ = ["MessagePanel", "CharacterPanel", "MenuPanel", "MapPanel"]

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
        # Clear tint
        self.ui.window.settint(0, 0, 0, (self.x, self.y, self.width, self.height))
        
        # Clear characters
        for y in range(self.height):
            self.putChars(" " * self.width, 0, y, colors.black, colors.black)
        
        

class MessagePanel(Panel):
    # TODO implement multi-color messages
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
        depth = self.ui.currentLevel.getDepth()
        
        self.render_bar(1, 1, 18, "HP", currentHP, maxHP, colors.darkBlue, colors.darkRed)
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
    def __init__(self, level, *args):
        super(MapPanel, self).__init__(*args)
        self.level = level
        self.camx = 0
        self.camy = 0
        
        self.xoffset = 0
        self.yoffset = 0
        
    def setLevel(self, lvl):
        self.level = lvl
        
    def getLevel(self):
        return self.level
    
    def moveCamera(self, dx, dy):
        self.xoffset += dx
        self.yoffset += dy
        
#        print self.camx + self.xoffset, self.camy + self.yoffset
        
    def resetCameraOffset(self):
        self.xoffset = 0
        self.yoffset = 0
    
    def cameraDims(self):
        return self.camx, self.camy, self.width, self.height
    
    def positionCamera(self, playerx, playery):
        
        lwidth = self.level.getWidth()
        lheight = self.level.getHeight()
        
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
        
        # Set camera position
        self.positionCamera(playerx, playery)
        
        # Get tiles
        tilesToDraw = self.level.getTilesToDraw(playerx, playery, self.cameraDims())
        
        for (x, y, symbol, color, background) in tilesToDraw:
            self.putChar(symbol, x - self.camx, y - self.camy, color, background)
            
    def getTileDescription(self, x, y):
        
        if self.containsPoint(x, y):
            mapx, mapy = x + self.camx, y + self.camy
            
            player = G.game.getPlayer()
            
            tile = self.level.getTile(mapx, mapy)
            if tile is None:
                return ''
            elif self.level.isInFOV(player.getX(), player.getY(), mapx, mapy):
                return tile.getDescription()
            else:
                return ''
        else:
            return ''
            
        
class MenuPanel(Panel):
    def __init__(self, *args, **kwargs):
        super(MenuPanel, self).__init__((0, 0, kwargs['width'], 0), *args)
        
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
        
        self.setupOptions(kwargs['options'])
        
        self.titleLine = self.title.center(self.width, self.tbBorder)
        
        
        
    def setupOptions(self, options):
        self.options = options
        
        # Set up word wrap
        self.linesToDisplay = {}
        optNum = 0
        self.height = 2*(self.margin + 1)
        letter_index = ord('a')
        
        for line in self.options:
            # Add letters
            line = '(' + chr(letter_index) + ') ' + line
            
            self.linesToDisplay[optNum] = []
            wrappedLines = textwrap.wrap(line, self.width - 2*(self.margin + 1))
            linesForOption = 0
            
            for wline in wrappedLines:
                
                if linesForOption > 0:
                    wline = ' ' * self.multilineIndent + wline.ljust(self.width - 2*(self.margin + 1) - self.multilineIndent)
                else:
                    wline = wline.ljust(self.width - 2*(self.margin + 1))
                    
                self.linesToDisplay[optNum].append(wline)
                self.height += 1
                linesForOption += 1
                
            optNum += 1
            letter_index += 1
                
#        self.height = len(self.linesToDisplay) + 2*(self.margin + 1)
        
        self.x = (C.SCREEN_WIDTH - self.width)/2
        self.y = (C.SCREEN_HEIGHT - self.height)/2
        
    def getSingleChoice(self):
        
        while True:
            self.draw()
            key, keyStr = self.ui.waitForInput()
            
            if key is None:
                return
         
            if key in (K_KP2, K_DOWN, K_j):
                self.selected[0] += 1
                if self.selected[0] >= len(self.options):
                    self.selected[0] = 0
                continue
            
            elif key in (K_KP8, K_UP, K_k):
                self.selected[0] -= 1
                if self.selected[0] < 0:
                    self.selected[0] = len(self.options) - 1
                continue
            
            elif key in (K_RETURN, K_KP_ENTER, K_COMMA):
                return self.selected[0]
            
            #convert the ASCII code to an index; if it corresponds to an option, return it
            index = key - ord('a')
            if index >= 0 and index < len(self.options): 
                return index
            
    def getMultiChoice(self):
        pass
        # TODO

    def draw(self):
        
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
        
        # print options, finally
        y = self.margin + 1
        for key in sorted(self.linesToDisplay.keys()):
            if key in self.selected:
                bg = self.selectedBGColor
            else:
                bg = self.defaultBGColor
            
            lines = self.linesToDisplay[key]
            for line in lines:

                # print side borders
                self.putChars(self.lrBorder + " " * self.margin, 0, y, fgcolor = self.defaultFGColor, bgcolor = self.defaultBGColor)
                self.putChars(" " * self.margin + self.lrBorder, self.width - self.margin - 1, y, fgcolor = self.defaultFGColor, bgcolor = self.defaultBGColor)
                
                # print text
                self.putChars(line, self.margin + 1, y, fgcolor = self.defaultFGColor, bgcolor=bg)
                y += 1
            
            
    
        # Draw shadow
        if self.shadow is not None:
            self.ui.window.addshadow(amount=self.shadowamount, region=(self.x, self.y, self.width, self.height), offset=None, direction=self.shadow, xoffset=self.shadowx, yoffset=self.shadowy)
        
        self.ui.drawWindow()
        
class GameMenuPanel(MenuPanel):
    
    def __init__(self, *args, **kwargs):
        super(GameMenuPanel, self).__init__(*args, **kwargs)
        
        self.enabledFGColor = kwargs.get('enabledFGColor', C.MENU_TEXT_COLOR)
        self.disabledFGColor = kwargs.get('disabledFGColor', C.MENU_DISABLED_TEXT_COLOR)
        
        self.selected = 0
        
    def setupOptions(self, options):
        self.options = options
        
        # Set up word wrap
        self.linesToDisplay = {}
        optNum = 0
        self.height = 2*(self.margin + 1)
        
        for opt in self.options:
            # Data type check
            if not isinstance(opt, dict):
                raise ValueError("GameMenuPanel options must be dictionaries")
            
            text = opt.get('text')
            enabled = opt.get('enabled')
            function = opt.get('function')
            
            if text is None or not isinstance(text, basestring):
                raise ValueError("GameMenuPanel options must have 'text' string parameter")
            
            if enabled is None or not isinstance(enabled, bool):
                raise ValueError("GameMenuPanel options must have 'enabled' boolean parameter")

            if enabled and (function is None or not hasattr(function, '__call__')): # Best method check I could come up with
                raise ValueError("GameMenuPanel options must have 'function' method parameter")
            
            self.linesToDisplay[optNum] = []
            wrappedLines = textwrap.wrap(text, self.width - 2*(self.margin + 1))
            linesForOption = 0
            
            for wline in wrappedLines:
                
                if linesForOption > 0:
                    wline = ' ' * self.multilineIndent + wline.ljust(self.width - 2*(self.margin + 1) - self.multilineIndent)
                else:
                    wline = wline.ljust(self.width - 2*(self.margin + 1))
                    
                self.linesToDisplay[optNum].append(wline)
                self.height += 1
                linesForOption += 1
                
            optNum += 1
                
        self.x = (C.SCREEN_WIDTH - self.width)/2
        self.y = (C.SCREEN_HEIGHT - self.height)/2
        
        
    def draw(self):
    
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
        
        # print options, finally
        y = self.margin + 1
        for key in sorted(self.linesToDisplay.keys()):
            option = self.options[key]
            
            if key == self.selected:
                bg = self.selectedBGColor
            else:
                bg = self.defaultBGColor
            
            if option['enabled']:
                fg = self.enabledFGColor
            else:
                fg = self.disabledFGColor
            
            
            lines = self.linesToDisplay[key]
            for line in lines:

                # print side borders
                self.putChars(self.lrBorder + " " * self.margin, 0, y, fgcolor = self.defaultFGColor, bgcolor = self.defaultBGColor)
                self.putChars(" " * self.margin + self.lrBorder, self.width - self.margin - 1, y, fgcolor = self.defaultFGColor, bgcolor = self.defaultBGColor)
                
                # print text
                self.putChars(line, self.margin + 1, y, fgcolor = fg, bgcolor = bg)
                y += 1
            
        # Draw shadow
        if self.shadow is not None:
            self.ui.window.addshadow(amount=self.shadowamount, region=(self.x, self.y, self.width, self.height), offset=None, direction=self.shadow, xoffset=self.shadowx, yoffset=self.shadowy)
        
        self.ui.drawWindow()
        
    def getSingleChoice(self):
            
        while True:
            self.draw()
            key, keyStr = self.ui.waitForInput()
            
            if key is None:
                return
         
            if key in (K_KP2, K_DOWN, K_j):
                while True:
                    self.selected += 1
                    if self.selected >= len(self.options):
                        self.selected = 0
                        
                    newOption = self.options[self.selected]
                    if newOption['enabled']: break
                    
                continue
            
            elif key in (K_KP8, K_UP, K_k):
                while True:
                    self.selected -= 1
                    if self.selected < 0:
                        self.selected = len(self.options) - 1
                    
                    newOption = self.options[self.selected]
                    if newOption['enabled']: break
                    
                continue
            
            elif key in (K_RETURN, K_KP_ENTER, K_COMMA, K_SPACE):
                return self.options[self.selected]['function']

        
def main():
    
    import pygcurse
    import pygame
    import sys
    
    options = ['bread', 'butter', 'eggs', 'an option which is significantly longer and will test my wordwrapping code to its very uttermost', 'milk', 'pickles']
    
    window = pygcurse.PygcurseWindow(C.SCREEN_WIDTH, C.SCREEN_HEIGHT)
    panel = MenuPanel(window, options = options, width = 25, title = "Groceries")
    print panel.getSingleChoice()
        
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()