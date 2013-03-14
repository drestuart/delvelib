'''
Created on Mar 13, 2013

@author: dstu
'''


from Import import *
libtcod = importLibtcod()

import Util as U

class AI(object):
    
    def setOwner(self, creature):
        self.owner = creature


class PlayerAI(AI):
    
    def takeTurn(self):
        print "Waiting for player"
        #key = libtcod.console_check_for_keypress()  #real-time
        key = libtcod.console_wait_for_keypress(True)  #turn-based
        
        if key.vk == libtcod.KEY_ESCAPE:
            exit(0)  #exit game
 
        elif key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8 or U.get_key(key) == 'k':
            self.owner.move(0, -1)
 
        elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2 or  U.get_key(key) == 'j':
            self.owner.move(0, 1)
 
        elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4 or  U.get_key(key) == 'h':
            self.owner.move(-1, 0)
 
        elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6 or  U.get_key(key) == 'l':
            self.owner.move(1, 0)

        elif key.vk == libtcod.KEY_KP1 or  U.get_key(key) == 'b':
            self.owner.move(-1, 1)

        elif key.vk == libtcod.KEY_KP3 or  U.get_key(key) == 'n':
            self.owner.move(1, 1)
            
        elif key.vk == libtcod.KEY_KP7 or  U.get_key(key) == 'y':
            self.owner.move(-1, -1)
        
        elif key.vk == libtcod.KEY_KP9 or  U.get_key(key) == 'u':
            self.owner.move(1, -1)

