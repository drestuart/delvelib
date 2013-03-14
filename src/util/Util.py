'''
Created on Mar 14, 2013

@author: dstu
'''

import libtcodpy as libtcod

def get_key(key):
    '''
    A convenience method for libtcod's draconian keyboard support
    '''
    
    if key.vk == libtcod.KEY_CHAR:
        return chr(key.c)
    else:
        return key.vk
