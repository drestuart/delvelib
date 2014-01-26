'''
Created on Jan 18, 2014

@author: dstu
'''

import Const as C
import colors
import keys
import pygame
from pygame.locals import *
import re
import textwrap

fgdefault = colors.colorMessagePanelFG
bgdefault = colors.colorMessagePanelBG

__all__ = ["Panel", "MessagePanel", "CharacterPanel", "MenuPanel"]

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
        chars = chars.encode(C.ENCODING, C.ENCODING_MODE)
        self.window.putchars(chars, cellx, celly, fgcolor, bgcolor)
        
    def putChar(self, char, x, y, fgcolor = None, bgcolor = None, indent = False):
        # Add offset for this window
        cellx = x + self.x
        celly = y + self.y
        char = char.encode(C.ENCODING, C.ENCODING_MODE)
        self.window.putchar(char, cellx, celly, fgcolor, bgcolor)
        
    def containsPoint(self, x, y):
        return (x >= self.x) and (x < self.x + self.width) and \
                (y >= self.y) and (y < self.y + self.height)
    
    def clear(self):
        # Clear tint
        self.window.settint(0, 0, 0, (self.x, self.y, self.width, self.height))
        
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
#            self.singleMessageClear()
            self.singleMessage = message.ljust(self.width)
            self.messageChanged = True
        else:
            self.messageChanged = False
            
    def singleMessageClear(self):
        clearst = ' ' * self.width
        self.putChars(clearst, 0, 0, colors.blankBackground, colors.blankBackground)
        
        
    def displayMessages(self):
        # Show single-line message
        self.putChars(self.singleMessage, 0, 0)
        
        y = self.y + 1

        # Only show the last (height) messages
        for line in self.messages[-self.messageWindowHeight:]:
            charsPrinted = 0
            wordsPrinted = 0
            wordsInLine = 0
            for (text, fg, bg) in line:
                wordsInLine += len(text.split())
            
            for (text, fg, bg) in line:
                words = text.split()
                
                # TODO Maybe don't need this if the word-wrap code in addMessage() is working?
                for word in words:
                    if len(word) + charsPrinted > self.width:
                        self.window.write("\n")
                        y += 1
                        charsPrinted = 0
                    
                    if wordsPrinted < wordsInLine - 1:
                        word = word + ' '
                        
                    # TODO convert to use putChars() so we don't have to handle the x-y offset twice
                    self.window.write(word, y=y, fgcolor=fg, bgcolor=bg)
                    charsPrinted += len(word)
                    wordsPrinted += 1
                    
            self.window.write("\n")
            y += 1
        
class CharacterPanel(Panel):
    def __init__(self, *args):
        super(CharacterPanel, self).__init__(*args)
        
    def draw(self, playerx = 0, playery = 0):
        self.render_bar(1, 1, 18, "HP", 15, 20, colors.darkBlue, colors.darkRed)
        self.showCoords(1, 3, playerx, playery)
        
    def showCoords(self, x, y, playerx, playery):
        
        self.putChars("Position: " + str(playerx) + ", " + str(playery), x, y, fgcolor = colors.white, bgcolor = colors.black)
        
    
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

#            self.window.putchar(' ', x, self.y + bary, fgcolor = colors.white, bgcolor = bg)
            self.putChar(' ', x, bary, fgcolor = colors.white, bgcolor = bg)
            
        # Add text
        text = name + ' ' + str(value) + '/' + str(maximum)
        textx = barx + (totalWidth - len(text)) / 2
        
        self.putChars(text, textx, bary)
    
        
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
            key, keyStr = keys.waitForInput()
            
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
            
            elif key in (K_RETURN, K_KP_ENTER):
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
            self.putChars(self.lrBorder + " " * self.margin, 0, i + 1, fgcolor = self.defaultFGColor, bgcolor = self.defaultBGColor)
            self.putChars(" " * self.margin + self.lrBorder, self.width - self.margin - 1, i + 1, fgcolor = self.defaultFGColor, bgcolor = self.defaultBGColor)
            # Spaces
            self.putChars(" " * (self.width - self.margin - 1), self.margin + 1, i + 1, fgcolor=colors.blankBackground, bgcolor=colors.blankBackground)
            
            self.putChars(self.lrBorder + " " * self.margin, 0, self.height - 2 - i, fgcolor = self.defaultFGColor, bgcolor = self.defaultBGColor)
            self.putChars(" " * self.margin + self.lrBorder, self.width - self.margin - 1, self.height - 2 - i, fgcolor = self.defaultFGColor, bgcolor = self.defaultBGColor)
            self.putChars(" " * (self.width - self.margin - 1), self.margin + 1, self.height - 2 - i, fgcolor=colors.blankBackground, bgcolor=colors.blankBackground)
        
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
            self.window.addshadow(amount=self.shadowamount, region=(self.x, self.y, self.width, self.height), offset=None, direction=self.shadow, xoffset=self.shadowx, yoffset=self.shadowy)
        
        self.window.update()
        self.window.blittowindow()
        
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