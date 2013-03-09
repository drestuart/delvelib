###############################################################
#
# OLD STUFF
#
###############################################################

# External imports
import libtcodpy as libtcod

from GetSetClass import *

CONFUSE_NUM_TURNS = 10

class AI(GetSet):
    
    def setOwner(self, creature):
        self.__dict__['owner'] = creature

class ConfusedMonster(AI):
    #AI for a temporarily confused monster (reverts to previous AI
    #after a while).
    def __init__(self, old_ai, num_turns=CONFUSE_NUM_TURNS):
        self.old_ai = old_ai
        self.num_turns = num_turns
 
    def takeTurn(self):
        if self.num_turns > 0:  #still confused...
            
            #move in a random direction, and decrease the number of
            #turns confused
            self.owner.move(libtcod.random_get_int(0, -1, 1), 
                            libtcod.random_get_int(0, -1, 1))
            self.num_turns -= 1
 
        else:  

            #restore the previous AI (this one will be deleted because
            #it's not referenced anymore)
            self.owner.ai = self.old_ai
            message('The ' + self.owner.name + ' is no longer confused!', 
                    libtcod.red)


# Normal Monster class
class NormalMonsterAI(AI):
    #AI for a basic monster.
    def takeTurn(self):
        dx = libtcod.random_get_int(0, -1, 1)
        dy = libtcod.random_get_int(0, -1, 1)
        self.owner.move(dx, dy)
        print self.owner.name, "takes its turn"
    
    def _take_turn(self):
        #a basic monster takes its turn. If you can see it, it can see you
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
 
            #move towards player if far away
            if monster.distance_to(player) >= 2:
                monster.move_towards(player.x, player.y)
 
            #close enough, attack! (if the player is still alive.)
            elif player.fighter.hp > 0:
                monster.fighter.attack(player)
                
class PlayerAI(AI):
    
    def takeTurn(self):
        print "Waiting for player"
        #key = libtcod.console_check_for_keypress()  #real-time
        key = libtcod.console_wait_for_keypress(True)  #turn-based
        
        if key.vk == libtcod.KEY_ESCAPE:
            exit(0)  #exit game
 
        elif key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
            self.owner.move(0, -1)
 
        elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
            self.owner.move(0, 1)
 
        elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
             self.owner.move(-1, 0)
 
        elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
            self.owner.move(1, 0)

        elif key.vk == libtcod.KEY_KP1:
            self.owner.move(-1, 1)

        elif key.vk == libtcod.KEY_KP3:
            self.owner.move(1, 1)
            
        elif key.vk == libtcod.KEY_KP7:
            self.owner.move(-1, -1)
        
        elif key.vk == libtcod.KEY_KP9:
            self.owner.move(1, -1)

