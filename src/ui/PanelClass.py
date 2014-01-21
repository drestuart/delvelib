'''
Created on Jan 18, 2014

@author: dstu
'''

import re
import colors
import Const as C

fgdefault = colors.colorMessagePanelFG
bgdefault = colors.colorMessagePanelBG

__all__ = ["Panel", "MessagePanel", "CharacterPanel"]

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
#        return (x >= self.x) and (x <= self.x + self.width) and \
#                (y >= self.y) and (y <= self.y + self.height)
        
        return (x >= self.x) and (x < self.x + self.width) and \
                (y >= self.y) and (y < self.y + self.height)

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
        
    def draw(self):
        self.render_bar(1, 1, 18, "HP", 15, 20, colors.darkBlue, colors.darkRed)
    
    def render_bar(self, barx, bary, totalWidth, name, value, maximum, barColor, backColor):
        #draw a bar (HP, experience, etc). first calculate the width of the bar
        barWidth = min( int(float(value) / maximum * totalWidth), totalWidth)
     
        # Draw bar
        for x in range(self.x + barx, self.x + barx + totalWidth):
            if x < self.x + barx + barWidth:
                bg = barColor
            else:
                bg = backColor

            self.window.putchar(' ', x, self.y + bary, fgcolor = None, bgcolor = bg)
            
        # Add text
        text = name + ' ' + str(value) + '/' + str(maximum)
        textx = self.x + barx + (totalWidth - len(text)) / 2
        
        self.window.putchars(text, textx, self.y + bary)
        
def main():
    
    import pygcurse
    import pygame
    import sys
    
    window = pygcurse.PygcurseWindow(40, 25)
    charPanel = CharacterPanel((5, 5, 20, 15), window)
    for h in range(5, 18):
        charPanel.render_bar(1, 1, 18, "HP", h, 20, colors.darkBlue, colors.darkRed)
        pygcurse.waitforkeypress()
    
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()