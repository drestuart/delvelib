'''
Created on Jan 16, 2014

@author: dstuart
'''

import pygcurse

win = pygcurse.PygcurseWindow(40, 25)
for k in pygcurse.colornames:
    win.write('This is the color %s\n' % (k), fgcolor=k)
    
pygcurse.waitforkeypress()
