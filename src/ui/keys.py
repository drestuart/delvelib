'''
Created on Mar 21, 2013

@author: dstu
'''

import libtcodpy as libtcod
import Util as U

movementKeys = {
                libtcod.KEY_UP : (0, -1),
                libtcod.KEY_KP8 : (0, -1),
                'k' : (0, -1),
                
                libtcod.KEY_DOWN : (0, 1),
                libtcod.KEY_KP2 : (0, 1),
                'j' : (0, 1),
                
                libtcod.KEY_LEFT : (-1, 0),
                libtcod.KEY_KP4 : (-1, 0),
                'h' : (-1, 0),
                
                libtcod.KEY_RIGHT : (1, 0),
                libtcod.KEY_KP6 : (1, 0),
                'l' : (1, 0),
                
                libtcod.KEY_KP1 : (-1, 1),
                'b' : (-1, 1),
                
                libtcod.KEY_KP3 : (1, 1),
                'n' : (1, 1),
                
                libtcod.KEY_KP7 : (-1, -1),
                'y' : (-1, -1),
                
                libtcod.KEY_KP9 : (1, -1),
                'u' : (1, -1)
                }

def getMovementDirection(key):
    
    if key.vk in movementKeys.keys():
        return movementKeys[key.vk]
    elif U.get_key(key) in movementKeys.keys():
        return movementKeys[U.get_key(key)]
    else:
        return None