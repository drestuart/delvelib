'''
Created on Jan 18, 2014

@author: dstu
'''

import re
import colors

fgdefault = colors.colorMessagePanelFG
bgdefault = colors.colorMessagePanelBG

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
    
        
    def displayMessages(self):
        y = self.y

        # Only show the last (height) messages
        for line in self.messages[-self.height]:
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
                        
                    self.window.write(word, y=y, fgcolor=fg, bgcolor=bg)
                    charsPrinted += len(word)
                    wordsPrinted += 1
                    
            self.window.write("\n")
            y += 1
        
class CharacterPanel(Panel):
    def __init__(self, *args):
        super(CharacterPanel, self).__init__(*args)
        
    # TODO implement character panel rendering
    def render(self):
        pass
