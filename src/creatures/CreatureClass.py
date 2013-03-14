###############################################################
#
# OLD STUFF
#
###############################################################

from Import import *
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.types import String, Integer, Boolean
import colors
import database as db

libtcod = importLibtcod()

Base = db.saveDB.getDeclarativeBase()


class Creature(Base):
    def __init__(self, **kwargs):
        
        self.symbol = kwargs['baseSymbol']
        self.baseColor = kwargs['baseColor']
        self.baseBackground = kwargs['baseBackground']
        
        
#    def getCoords(self):
#        return self.coordinates
#        
#    def move(self, dx, dy):
#        
#        newCoords = self.coordinates + Coordinates(x = dx, y = dy)
#        newTile = self.map.getTile(newCoords)
#        
#        if newTile.addCreature(self):
#            
#            #Remove self from the old tile
#            oldTile = self.map.getTile(self.coordinates)
#            oldTile.removeCreature()
#        
#            self.setPosition(self.map, newCoords)
#            #self.energy -= self.moveCost
#                        
#            print self.name + " moves to", self.coordinates
#            return True
#        
#        else:
#            return False
#        
#    def setPosition(self, map, coords):
#        self.__dict__['coordinates'] = coords
#        self.__dict__['map'] = map
#    
#    def changeHP(self, amount):
#        self.__dict__['hp'] = min(self.hp + amount, self.max_hp)
#        if self.hp <= 0:
#            self.deathFunction(self)
#
#    def heal(self, amount):
#        #heal by the given amount
#        self.changeHP(amount)
#
#    def takeDamage(self, damage):
#        #apply damage if possible
#        if damage > 0:
#            self.changeHP(-damage)
#            
#    def passTime(self, turns = 1):
#        print "It is " + self.name + "'s turn"
#        for i in range(turns):
#            self.takeTurn() 
#
#    def takeTurn(self):
#        self.ai.takeTurn()
#    
#    def isVisible(self):
#        return self.visible
#    
#    def color(self):
#        # There will probably be some more logic here
#        return self.baseColor
#    
#    def symbol(self):
#        return self.symbol
#    
#    def background(self):
#        return self.baseBackground








