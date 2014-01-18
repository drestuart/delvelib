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
            msglist = []
            fg = fgdefault
            bg = bgdefault
    
    
            while len(chunks) > 0:
                chunk = chunks.pop(0)
                colorspecpat = re.compile(r'^<(.*)>$')
                cm = re.search(colorspecpat, chunk)
                
                if cm:
                    text = cm.groups()
                    # Set fg and bg variables
                    words = text[0].split()
                    
                    fgpat = re.compile(r'fg=(.*)')
                    bgpat = re.compile(r'bg=(.*)')
                    tuplepat = re.compile(r'^\(.+\)$')
                    commapat = ','
                    
                    for word in words:
                        
                        if word == 'default':
                            fg = fgdefault
                            bg = bgdefault
                            print "Setting foreground: default"
                            continue
                        
                        fgm = re.match(fgpat, word)
                        if fgm:
                            fgStr = fgm.group(1)
                            
                            if re.match(tuplepat, fgStr):
                                print "found a tuple"
                                # Convert to tuple
                                print re.split(commapat, fgStr[1:-1])
                                fg = tuple(int(s) for s in re.split(commapat, fgStr[1:-1]))
                            else:
                                print "no tuple"
                                fg = fgStr
                            
                            print "Setting foreground: " + str(fg)
                            continue
                        
                        
                        bgm = re.match(bgpat, word)
                        if bgm:
                            bgStr = bgm.group(1)
                            
                            if re.match(tuplepat, bgStr):
                                print "found a tuple"
                                # Convert to tuple
                                print re.split(commapat, bgStr[1:-1])
                                bg = tuple(int(s) for s in re.split(commapat, bgStr[1:-1]))
                            else:
                                print "no tuple"
                                bg = bgStr
                            
                            print "Setting background: " + str(bg)
                            continue
                            
                    
                else:
                    if len(chunk) > 0:
                        msglist.append( (chunk, fg, bg) )
                    
            self.messages.append(msglist)
    
        
    def displayMessages(self):
        y = self.y
        
        # Only show the last (height) messages
        for line in self.messages[-self.height]:
            for (text, fg, bg) in line:
                self.window.write(text, y=y, fgcolor=fg, bgcolor=bg)
            self.window.write("\n")
            y += 1
        
class CharacterPanel(Panel):
    def __init__(self, *args):
        super(CharacterPanel, self).__init__(*args)
        
    # TODO implement character panel rendering
    def render(self):
        pass
