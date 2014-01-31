'''
Created on Mar 21, 2013

@author: dstu
'''

from pygame.locals import *
import pygame
import Const as C

def waitForInput():
    clock = pygame.time.Clock()
    while True:
        clock.tick(C.MENU_FPS)
        for event in pygame.event.get([KEYDOWN, QUIT]):  # TODO what do the event types do here?
            if event.type == QUIT:
                return None, None
            elif event.type == KEYDOWN:
                key = event.key
                keyStr = pygame.key.name(key)
                # key is the integer key code, keyStr is the string representation
                return key, keyStr

movementKeys = {
                K_UP : (0, -1),
                K_KP8 : (0, -1),
                'k' : (0, -1),
                
                K_DOWN : (0, 1),
                K_KP2 : (0, 1),
                'j' : (0, 1),
                
                K_LEFT : (-1, 0),
                K_KP4 : (-1, 0),
                'h' : (-1, 0),
                
                K_RIGHT : (1, 0),
                K_KP6 : (1, 0),
                'l' : (1, 0),
                
                K_KP1 : (-1, 1),
                'b' : (-1, 1),
                
                K_KP3 : (1, 1),
                'n' : (1, 1),
                
                K_KP7 : (-1, -1),
                'y' : (-1, -1),
                
                K_KP9 : (1, -1),
                'u' : (1, -1)
                }

def getMovementDirection(key, keyStr):
    
    if keyStr in movementKeys.keys():
        return movementKeys[keyStr]
    elif key in movementKeys.keys():
        return movementKeys[key]
    else:
        return None
