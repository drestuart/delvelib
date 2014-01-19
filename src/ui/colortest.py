'''
Created on Jan 18, 2014

@author: dstu
'''

import pygcurse
import re
import colors

fgdefault = colors.colorMessagePanelFG
bgdefault = colors.colorMessagePanelBG
width = 40

def addMessage(message):

    colorpat = re.compile(r'(<.*?>)')
    m = re.search(colorpat, message)
        
    if not m:
        return [(message, fgdefault, bgdefault)]
#        print message
    
    else:
        chunks = re.split(colorpat, message)
        retlist = []
        fg = fgdefault
        bg = bgdefault

#        print chunks

        while len(chunks) > 0:
            chunk = chunks.pop(0)
            colorspecpat = re.compile(r'^<(.*)>$')
            cm = re.search(colorspecpat, chunk)
            
            if cm:
                text = cm.groups()
#                print text
                # Set fg and bg variables
                words = text[0].split()
                
                fgpat = re.compile(r'fg=(.*)')
                bgpat = re.compile(r'bg=(.*)')
#                tuplepat = re.compile(r'\(.(\s*,.+?\s*)*?\)')
                tuplepat = re.compile(r'^\(.+\)$')
#                commapat = re.compile(r'(\s*,.+?\s*)')
                commapat = ','
                
                for word in words:
                    
                    if word == 'default':
                        fg = fgdefault
                        bg = bgdefault
                        #print "Setting foreground: default"
                        continue
                    
                    fgm = re.match(fgpat, word)
                    if fgm:
                        fgStr = fgm.group(1)
                        
                        if re.match(tuplepat, fgStr):
                            #print "found a tuple"
                            # Convert to tuple
                            #print re.split(commapat, fgStr[1:-1])
                            fg = tuple(int(s) for s in re.split(commapat, fgStr[1:-1]))
                        else:
                            #print "no tuple"
                            fg = fgStr
                        
                        #print "Setting foreground: " + str(fg)
                        continue
                    
                    
                    bgm = re.match(bgpat, word)
                    if bgm:
                        bgStr = bgm.group(1)
                        
                        if re.match(tuplepat, bgStr):
                            #print "found a tuple"
                            # Convert to tuple
                            #print re.split(commapat, bgStr[1:-1])
                            bg = tuple(int(s) for s in re.split(commapat, bgStr[1:-1]))
                        else:
#                            print "no tuple"
                            bg = bgStr
                        
                        #print "Setting background: " + str(bg)
                        continue
                        
                
            else:
                if len(chunk) > 0:
                    retlist.append( (chunk, fg, bg) )
                
        return retlist
        
def printColorMessages(win, messages):
    
    y = 0
    
    for line in messages:
        charsPrinted = 0
        wordsPrinted = 0
        wordsInLine = 0
        for (text, fg, bg) in line:
            wordsInLine += len(text.split())
        
        for (text, fg, bg) in line:
            words = text.split()
            
            for word in words:
                if len(word) + charsPrinted > width:
                    print "Word wrap!"
                    win.write("\n")
                    y += 1
                    charsPrinted = 0
                
                if wordsPrinted < wordsInLine - 1:
                    word = word + ' '
                    
                win.write(word, y=y, fgcolor=fg, bgcolor=bg)
                charsPrinted += len(word)
                wordsPrinted += 1
                print charsPrinted
                
        win.write("\n")
        y += 1
        
    pygcurse.waitforkeypress()

def main():
    
    win = pygcurse.PygcurseWindow(width, 25)
    messages = []
    
    messages.append(addMessage("Hello!"))
    messages.append(addMessage("Hello <fg=green>green!"))
    messages.append(addMessage("<bg=red>Hello <fg=(255,255,255) bg=green>green!"))
    messages.append(addMessage("<default>Hello <fg=olive>olive <bg=red>red <default>default!<bg=(0,0,255)>"))
    messages.append(addMessage("This is a really really really really really really really really really really really really really really really long message"))
    
    printColorMessages(win, messages)
    
#    print messages



if __name__ == '__main__':
    main()