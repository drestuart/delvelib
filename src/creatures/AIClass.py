'''
Created on Mar 13, 2013

@author: dstu
'''


from Import import *
libtcod = importLibtcod()

import Util as U
import random

class AI(object):
    
    def setOwner(self, creature):
        self.owner = creature


class PlayerAI(AI):
    
    def takeTurn(self):
        print "Waiting for player"
        
        
        while True:
            key = libtcod.console_wait_for_keypress(True)
            
            if key.vk == libtcod.KEY_ESCAPE:
                exit(0)  #exit game
                
            elif key.pressed:
     
                if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8 or U.get_key(key) == 'k':
                    if self.owner.move(0, -1):
                        break
         
                elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2 or  U.get_key(key) == 'j':
                    if self.owner.move(0, 1):
                        break
         
                elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4 or  U.get_key(key) == 'h':
                    if self.owner.move(-1, 0):
                        break
         
                elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6 or  U.get_key(key) == 'l':
                    if self.owner.move(1, 0):
                        break
        
                elif key.vk == libtcod.KEY_KP1 or  U.get_key(key) == 'b':
                    if self.owner.move(-1, 1):
                        break
        
                elif key.vk == libtcod.KEY_KP3 or  U.get_key(key) == 'n':
                    if self.owner.move(1, 1):
                        break
                    
                elif key.vk == libtcod.KEY_KP7 or  U.get_key(key) == 'y':
                    if self.owner.move(-1, -1):
                        break
                
                elif key.vk == libtcod.KEY_KP9 or  U.get_key(key) == 'u':
                    if self.owner.move(1, -1):
                        break
                    
                elif U.get_key(key) == '.':
                    break


class AggressiveAI(AI):
    def takeTurn(self):
#        print self.owner.name, "moves"
        while True:
            randX = random.randint(-1, 1)
            if randX:
                randY = random.randint(-1, 1)
            else:
                randY = random.choice([-1, 1])
                
            if self.owner.move(randX, randY):
                break


class NeutralAI(AI):
    def takeTurn(self):
#        print self.name, "moves"
        while True:
            randX = random.randint(-1, 1)
            if randX:
                randY = random.randint(-1, 1)
            else:
                randY = random.choice([-1, 1])
                
            if self.owner.move(randX, randY):
                break


class SedentaryAI(AI):
    def takeTurn(self):
        pass

