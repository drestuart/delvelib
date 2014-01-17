'''
Created on Jan 16, 2014

@author: dstuart
'''

import pygcurse
import pygame
from pygame.locals import *
import sys

win = pygcurse.PygcurseWindow(40, 25)

print K_ESCAPE

while True:
    for event in pygame.event.get([KEYDOWN, KEYUP, QUIT]):
        if event.type == KEYDOWN:
            continue
        elif event.type == QUIT:
            print "Got a QUIT event"
            pygame.quit()
            sys.exit()
        elif event.type == KEYUP:
            key = event.key
            keyStr = pygame.key.name(key)
            print key, "=>", keyStr
    
