'''
Created on Mar 14, 2013

@author: dstu
'''

def get_key(key):
    '''
    A convenience method for libtcod's draconian keyboard support
    '''
    
    if key.vk == libtcod.KEY_CHAR:
        return chr(key.c)
    else:
        return key.vk

def ManhattanDistance(x1, x2, y1, y2):
    return abs(x1-x2) + abs(y1-y2)

def ChebyshevDistance(x1, x2, y1, y2):
    return max(abs(x1-x2), abs(y1-y2))