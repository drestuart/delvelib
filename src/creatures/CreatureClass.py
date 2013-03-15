'''
Created on Mar 13, 2013

@author: dstu
'''

from Import import *
from ctypes.wintypes import INT
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.types import String, Integer, Boolean
import Util as U
import AIClass as AI
import colors
import database as db

libtcod = importLibtcod()

Base = db.saveDB.getDeclarativeBase()


class Creature(Base):
    
    __tablename__ = "creatures"
    __table_args__ = {'extend_existing': True}
    
    
    def __init__(self, **kwargs):
        
        self.symbol = kwargs['symbol']
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
        
        self.visible = kwargs.get('visible', True)
        self.path = None
        
        self.hateList = kwargs.get('hateList', ['player'])
        
        self.AIClass = kwargs['AIClass']
        self.initializeAI()

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
    creatureType = Column(String)
    
    maxHP = Column(Integer)
    damageTaken = Column(Integer)
    
    goalEnemy = relationship("Creature", uselist=False)
    goalEnemyId = Column(Integer, ForeignKey('creatures.id'))
    
    visible = Column(Boolean)
    
    AIClassName = Column(String)
    
    __mapper_args__ = {'polymorphic_on': creatureType,
                       'polymorphic_identity': 'creature'}
    
    def move(self, dx, dy):
        
        newX = self.getX() + dx
        newY = self.getY() + dy
        level = self.getLevel()
        newTile = level.getTile(newX, newY)
        
        return self.moveToTile(newTile)
        
        
    def moveToTile(self, newTile):
        
        level = self.getLevel()
        
        if level.placeCreature(self, newTile):
                        
            print self.name + " moves to", self.getX(), self.getY()
            return True
        
        else:
            return False
        
    
    def getTile(self):
        return self.tile
    
    def setTile(self, tile):
        self.tile = tile
        
    def getX(self):
        return self.tile.getX()
    
    def getY(self):
        return self.tile.getY()
        
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
        if self.__dict__.get('baseColor', None):
            return self.baseColor
        else:
            self.baseColor = libtcod.Color(self.baseColorR, self.baseColorG, self.baseColorB)
            return self.baseColor

    
    def getColor(self):
        return self.getBaseColor()


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

    def isVisible(self):
        return self.visible

    def setVisible(self, value):
        self.visible = value

    def getSymbol(self):
        return self.symbol

    def setSymbol(self, value):
        self.symbol = value
        
    def initializeAI(self):
        if not self.AIClassName:
            # Get AI class by name
            pass
        else:
            self.AIClassName = self.AIClass.__name__
        
        self.AI = self.AIClass()
        self.AI.setOwner(self)
        
    def takeTurn(self):
        self.AI.takeTurn()
        
    def getGoalTile(self):
        return self.goalTile
    
    def setGoalTile(self, newTile):
#        oldGoal = self.getGoalTile()
#        if oldGoal:
#            oldGoal.setGoalTileOf(None)
        
#        self.goalTile = newTile
        newTile.setGoalTileOf(self)
        
    def distance(self, other):
        return self.getTile().distance(other.getTile())


    def getCreatureType(self):
        return self.creatureType

    def setCreatureType(self, value):
        self.creatureType = value

    def getGoalEnemy(self):
        return self.goalEnemy

    def getGoalEnemyId(self):
        return self.goalEnemyId

    def setGoalEnemy(self, value):
        self.goalEnemy = value

    def setGoalEnemyId(self, value):
        self.goalEnemyId = value

    def getPath(self):
        return self.path

    def setPath(self, value):
        self.path = value

    def getHateList(self):
        return self.hateList

    def setHateList(self, value):
        self.hateList = value
        
    def attack(self, enemy):
        print self.getName(), "attacks", enemy.getName()


class Orc(Creature):
    
    def __init__(self, **kwargs):
        super(Orc, self).__init__(symbol = 'o', baseColor = colors.red, baseBackground = colors.black, 
                                  name = 'orc', description = 'a hideous orc', species = 'orc',
                                  maxHP = 10, AIClass = AI.AggressiveAI, **kwargs)
    
    __mapper_args__ = {'polymorphic_identity': 'orc'}


    








