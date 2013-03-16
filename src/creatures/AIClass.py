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
        
    def wander(self):
        while True:
            
            if random.randint(0, 1) == 1:
                break
            
            randX = random.randint(-1, 1)
            if randX:
                randY = random.randint(-1, 1)
            else:
                randY = random.choice([-1, 1])
                
            if self.owner.move(randX, randY):
                break


class PlayerAI(AI):
    
    def takeTurn(self, key):
#        print "Waiting for player"
        
        
#        while True:
#        key = libtcod.console_wait_for_keypress(True)
        
        if key.vk == libtcod.KEY_ESCAPE:
#                exit(0)  #exit game
            return "exit"
            
        elif key.pressed:
 
            if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8 or U.get_key(key) == 'k':
                if self.owner.move(0, -1):
                    return 'took-turn'
     
            elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2 or  U.get_key(key) == 'j':
                if self.owner.move(0, 1):
                    return 'took-turn'
     
            elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4 or  U.get_key(key) == 'h':
                if self.owner.move(-1, 0):
                    return 'took-turn'
     
            elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6 or  U.get_key(key) == 'l':
                if self.owner.move(1, 0):
                    return 'took-turn'
    
            elif key.vk == libtcod.KEY_KP1 or  U.get_key(key) == 'b':
                if self.owner.move(-1, 1):
                    return 'took-turn'
    
            elif key.vk == libtcod.KEY_KP3 or  U.get_key(key) == 'n':
                if self.owner.move(1, 1):
                    return 'took-turn'
                
            elif key.vk == libtcod.KEY_KP7 or  U.get_key(key) == 'y':
                if self.owner.move(-1, -1):
                    return 'took-turn'
            
            elif key.vk == libtcod.KEY_KP9 or  U.get_key(key) == 'u':
                if self.owner.move(1, -1):
                    return 'took-turn'
                
            elif key.vk == libtcod.KEY_KPDEC or U.get_key(key) == '.':
                return 'took-turn'
            
        else:
            return 'didnt-take-turn'
            
    
    def takeTurn1(self):
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
                    
                elif key.vk == libtcod.KEY_KPDEC or U.get_key(key) == '.':
                    break


class AggressiveAI(AI):
    
    def findNewEnemy(self, visibleCreatures):
        print self.owner.The(), "is looking for an enemy"
        nearestEnemy = None
        nearestEnemyDistance = None
        
        for cr in visibleCreatures:
            if cr.getCreatureType() in self.owner.getHateList():
                dist = self.owner.distance(cr)
                
                if dist < nearestEnemyDistance or nearestEnemyDistance is None:
                    nearestEnemyDistance = dist
                    nearestEnemy = cr
                    self.owner.setGoalEnemy(cr)
                    self.owner.setGoalTile(cr.getTile())
                    
        return nearestEnemy, nearestEnemyDistance
    
    def walkPath(self):
        path = self.owner.getPath()
        
        if libtcod.path_is_empty(path):
            self.wander()
            return
        else:
            x, y = libtcod.path_walk(path, recompute = True)
            dx = x - self.owner.getX()
            dy = y - self.owner.getY()
            
            if not self.owner.move(dx, dy):
                print self.owner.The(), "is stuck!"
    
    def getLevel(self):
        return self.owner.getLevel()
    
    def getTile(self):
        return self.owner.getTile()
    
    def attackAdjacent(self):
        enemy = self.owner.getGoalEnemy()
        if enemy:
            if self.owner.distance(enemy) == 1:
                self.owner.attack(enemy)
                return True
            
        return False
    
    def takeTurn(self):
#        print self.owner.name, "moves"

        if self.attackAdjacent():
            return
        else:
            if self.findEnemy():
                self.walkPath()
                return
            print self.owner.The(), "gives up and wanders around"
            self.wander()
            
    def findEnemy(self):
        
        visibleCreatures = self.getLevel().getVisibleCreaturesFromTile(self.getTile(), 0)
        
        path = self.owner.getPath()
        enemy = self.owner.getGoalEnemy()
        
        # Look around for a new enemy to attack
        if not enemy:
            enemy, distance = self.findNewEnemy(visibleCreatures)
            if distance == 1:
                self.owner.attack(enemy)
                return True
            if not enemy:
                return False
        
        # See if we need to recalculate the path
        if path and not libtcod.path_is_empty(path) and (enemy.getTile() is self.owner.getGoalTile()):
            print self.owner.The(), "follows the path"
            return True
            
        # If we need to recalculate, set up the goal tile
        if not (enemy.getTile() is self.owner.getGoalTile()):
            print self.owner.The(), "needs to recompute a path to the enemy"
            self.owner.setGoalTile(enemy.getTile())
            distance = self.owner.distance(enemy)
            if distance == 1:
                self.owner.attack(enemy)
                return True
        
        # Calculate the new path
        print self.owner.The(), "is computing a path to the enemy"
        goalTile = self.owner.getGoalTile()
        if goalTile:
            path = self.getLevel().getPathToTile(self.getTile(), goalTile)
            
#            if path and not libtcod.path_is_empty(path):
            if not libtcod.path_is_empty(path):
                self.owner.setPath(path)
                return True
            else:
                print self.owner.The(), "can't find a path to the enemy"
                return False
    
        else:
            print self.owner.The(), "has no goal tile"
            return False
                


class NeutralAI(AI):
    def takeTurn(self):
        self.wander()
        

class SedentaryAI(AI):
    def takeTurn(self):
        pass

