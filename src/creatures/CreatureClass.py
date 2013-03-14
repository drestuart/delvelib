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
from ctypes.wintypes import INT

libtcod = importLibtcod()

Base = db.saveDB.getDeclarativeBase()


class Creature(Base):
    
    __tablename__ = "creatures"
    __table_args__ = {'extend_existing': True}
    
    
    def __init__(self, **kwargs):
        
        self.symbol = kwargs['baseSymbol']
        self.baseColor = kwargs['baseColor']
        self.baseBackgroundColor = kwargs['baseBackground']
        
        self.baseColorR = self.baseColor.r
        self.baseColorG = self.baseColor.g
        self.baseColorB = self.baseColor.b
        
        self.baseBackgroundColorR = self.baseBackgroundColor.r
        self.baseBackgroundColorG = self.baseBackgroundColor.g
        self.baseBackgroundColorB = self.baseBackgroundColor.b
        
        self.name = kwargs['name']
        self.description = kwargs['description']
        self.species = kwargs['species']
        
        self.maxHP = kwargs['maxHP']
        self.damageTaken = kwargs.get('damageTaken', 0)
        
        self.AIClass = kwargs['AIClass']
#        self.AI = AIClass()
        
        
        
    id = Column(Integer, primary_key=True, unique=True)
    
    symbol = Column(String(length=1, convert_unicode = False))
    
    baseColorR = Column(Integer)
    baseColorG = Column(Integer)
    baseColorB = Column(Integer)
    
    baseBackgroundColorR = Column(Integer)
    baseBackgroundColorG = Column(Integer)
    baseBackgroundColorB = Column(Integer)
    
    description = Column(String)
    name = Column(String)
    species = Column(String)
    
    maxHP = Column(Integer)
    damageTaken = Column(Integer)
    
    AIClass = Column(String)
    
    __mapper_args__ = {'polymorphic_on': species,
                       'polymorphic_identity': 'creature'}
    
    def getTile(self):
        return self.tile
    
    def setTile(self, tile):
        self.tile = tile
        
    def getLevel(self):
        return self.getTile().getLevel()
    
    def calcHP(self):
        self.hp = self.maxHP - self.damageTaken
    
    def heal(self, amount):
        self.changeHP(amount)
        
    def takeDamage(self, dam):
        self.changeHP(-dam)
        
    def changeHP(self, amount):
        self.damageTaken = min(self.damageTaken - amount, 0)
        self.calcHP()
        if self.hp <= 0:
            self.deathFunction(self)

    def getBaseColor(self):
        return self.baseColor


    def getBaseBackgroundColor(self):
        return self.baseBackgroundColor


    def getBaseColorR(self):
        return self.baseColorR


    def getBaseColorG(self):
        return self.baseColorG


    def getBaseColorB(self):
        return self.baseColorB


    def getBaseBackgroundColorR(self):
        return self.baseBackgroundColorR


    def getBaseBackgroundColorG(self):
        return self.baseBackgroundColorG


    def getBaseBackgroundColorB(self):
        return self.baseBackgroundColorB


    def getName(self):
        return self.name


    def getDescription(self):
        return self.description


    def getSpecies(self):
        return self.species


    def getMaxHP(self):
        return self.maxHP


    def getDamageTaken(self):
        return self.damageTaken


    def getAIClass(self):
        return self.AIClass


    def setBaseColor(self, value):
        self.baseColor = value


    def setBaseBackgroundColor(self, value):
        self.baseBackgroundColor = value


    def setBaseColorR(self, value):
        self.baseColorR = value


    def setBaseColorG(self, value):
        self.baseColorG = value


    def setBaseColorB(self, value):
        self.baseColorB = value


    def setBaseBackgroundColorR(self, value):
        self.baseBackgroundColorR = value


    def setBaseBackgroundColorG(self, value):
        self.baseBackgroundColorG = value


    def setBaseBackgroundColorB(self, value):
        self.baseBackgroundColorB = value


    def setName(self, value):
        self.name = value


    def setDescription(self, value):
        self.description = value


    def setSpecies(self, value):
        self.species = value


    def setMaxHP(self, value):
        self.maxHP = value


    def setDamageTaken(self, value):
        self.damageTaken = value


    def setAIClass(self, value):
        self.AIClass = value


    
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








