'''
Created on Mar 13, 2013

@author: dstu
'''


import random
import keys
from pygame.locals import *
import Game as G

def getAIClassByName(name):
    return AIdict.get(name)

class AI(object):
    
    def __init__(self):
        print "Initializing AI"
        self.path = None
    
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
            
    def getPath(self):
        return self.path


class PlayerAI(AI):
    
    def takeTurn(self, key):
#        print "Waiting for player"
        
        key, keyStr = G.game.waitForInput()
        
        if key == keys.K_ESCAPE:
            return "exit"
            
        else:
            direc = keys.getMovementDirection(key, keyStr)

            if direc:
                dx, dy = direc
                if self.owner.move(dx, dy):
                    return 'took-turn'
 
            elif key == K_KP_PERIOD or keyStr == '.':
                return 'took-turn'
            
            elif keyStr == ',':
                return 'took-turn'
            
            else:
                return 'didnt-take-turn'
            
    
class AggressiveAI(AI):
    
    def walkPath(self):
        path = self.getPath()
#         print "Walking path:", path
        
        if path is None or len(path) == 0:
            self.owner.setGoalTile(None)
            self.wander()
            return
        else:
#             print self.owner.getX(), self.owner.getY(), path
            x, y = path.pop(0)
            dx = x - self.owner.getX()
            dy = y - self.owner.getY()
            
            if not self.owner.move(dx, dy):
                pass
#                 print self.owner.The(), "is stuck!"
    
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
#         print "\n\n"
#         print self.owner.The(), "moves"

        if self.enemyIsVisible() and self.enemyIsInRange():
#             print self.owner.The(), "sees an enemy within range!"
            self.attackEnemy()
            return
        elif self.enemyIsVisible():
#             print self.owner.The(), "can see an enemy!"
            self.findPathToEnemy()
            self.walkPath()
            return
        elif self.owner.getGoalTile() is not None:
#             print self.owner.The(), "is following its path"
            self.findPathToGoal()
            self.walkPath()
        else:
#             print self.owner.The(), "is looking for an enemy"
            if self.findEnemy():
                if self.enemyIsInRange():
                    self.attackEnemy()
                else:
                    self.findPathToEnemy()
                    self.walkPath()
                return
            print self.owner.The(), "gives up and wanders around"
            self.wander()
            
        

    def enemyIsVisible(self):
        enemy = self.owner.getGoalEnemy()
        if enemy is None: return False
        
        canSee = self.owner.canSeeCreature(enemy)
        if not canSee:
            self.owner.setGoalEnemy(None)
        
        return canSee
                
    def enemyIsInRange(self):
        enemy = self.owner.getGoalEnemy()
        if enemy is None: return False
        
        if enemy and self.owner.distance(enemy) <= self.owner.getAttackRange():
            return True
        else:
            return False
    
    def attackEnemy(self):
        self.owner.attack(self.owner.getGoalEnemy())
        
    def findPathToGoal(self):
        goalTile = self.owner.getGoalTile()
        
        # Check if the current path is valid and leads to the current goal tile.
        # If so, do nothing
        if self.path and not len(self.path) > 0 and goalTile is not None and self.path[-1] is goalTile:
            return True
        
        
        # Calculate the new path
        if goalTile:
#             print self.owner.The(), "is finding a path from", (self.getTile().getXY()), "to", (goalTile.getXY())
        
            self.path = self.getLevel().getPathToTile(self.getTile(), goalTile)
#             print "Path:", self.path
            if self.path and len(self.path) > 0:
                return True
            else:
                return False
        else:
            return False
    
        
    def findPathToEnemy(self):
        # Set up the goal tile
        goalTile = self.owner.getGoalEnemy().getTile()
        self.owner.setGoalTile(goalTile)
        
        return self.findPathToGoal()
            
    def findEnemy(self):
        # Look around for a new enemy to attack
        visibleCreatures = self.getLevel().getVisibleCreaturesFromTile(self.getTile())
        
        enemy = self.findNewEnemy(visibleCreatures)
        if not enemy:
            return False

        return True
    
    def findNewEnemy(self, visibleCreatures):
#        print self.owner.The(), "is looking for an enemy"
        nearestEnemy = None
        nearestEnemyDistance = None
        
        for cr in visibleCreatures:
            if cr.getCreatureType() in self.owner.getHateList():
                dist = self.owner.distance(cr)
                
                if dist < nearestEnemyDistance or nearestEnemyDistance is None:
                    nearestEnemyDistance = dist
                    nearestEnemy = cr
                    self.owner.setGoalEnemy(cr)
                    
        return nearestEnemy

class NeutralAI(AI):
    def takeTurn(self):
        self.wander()
        

class SedentaryAI(AI):
    def takeTurn(self):
        pass


AIdict = {
          "SedentaryAI" : SedentaryAI,
          "NeutralAI" : NeutralAI,
          "AggressiveAI" : AggressiveAI,
          "PlayerAI" : PlayerAI
          }