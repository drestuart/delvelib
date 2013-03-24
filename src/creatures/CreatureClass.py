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
import Game as G
import InventoryClass as I

libtcod = importLibtcod()

Base = db.saveDB.getDeclarativeBase()


class Creature(Base):
    
    __tablename__ = "creatures"
    __table_args__ = {'extend_existing': True}
    
    
    def __init__(self, **kwargs):
        
        self.symbol = kwargs['symbol']
        self.color = kwargs['color']
        self.backgroundColor = kwargs['background']
        
        self.colorR = self.color.r
        self.colorG = self.color.g
        self.colorB = self.color.b
        
        self.backgroundColorR = self.backgroundColor.r
        self.backgroundColorG = self.backgroundColor.g
        self.backgroundColorB = self.backgroundColor.b
        
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
        
        self.inventory = I.Inventory()


    id = Column(Integer, primary_key=True, unique=True)
    
    symbol = Column(String(length=1, convert_unicode = False))
    
    colorR = Column(Integer)
    colorG = Column(Integer)
    colorB = Column(Integer)
    
    backgroundColorR = Column(Integer)
    backgroundColorG = Column(Integer)
    backgroundColorB = Column(Integer)
    
    description = Column(String)
    name = Column(String)
    species = Column(String)
    creatureType = Column(String)
    
    maxHP = Column(Integer)
    damageTaken = Column(Integer)
    
    goalEnemy = relationship("Creature", uselist=False)
    goalEnemyId = Column(Integer, ForeignKey('creatures.id'))
    
    inventoryId = Column(Integer, ForeignKey("inventories.id"))
    inventory = relationship("Inventory", backref = backref("creature", uselist = False), uselist = False, primaryjoin = "Creature.inventoryId == Inventory.id")
    
    visible = Column(Boolean)
    
    AIClassName = Column(String)
    
    __mapper_args__ = {'polymorphic_on': creatureType,
                       'polymorphic_identity': 'creature'}
    
    def getInventory(self):
        return self.inventory
    
    def move(self, dx, dy):
        
        newX = self.getX() + dx
        newY = self.getY() + dy
        level = self.getLevel()
        newTile = level.getTile(newX, newY)
        
        return self.moveToTile(newTile)
        
        
    def moveToTile(self, newTile):
        
        level = self.getLevel()
        
        if level.placeCreature(self, newTile):
                        
#            print self.name + " moves to", self.getX(), self.getY()
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

    def getColor(self):        
        if self.__dict__.get('color', None):
            return self.color
        else:
            self.color = libtcod.Color(self.colorR, self.colorG, self.colorB)
            return self.color

    
    def getBackgroundColor(self):
        return self.backgroundColor


    def getColorR(self):
        return self.colorR


    def getColorG(self):
        return self.colorG


    def getColorB(self):
        return self.colorB


    def getBackgroundColorR(self):
        return self.backgroundColorR


    def getBackgroundColorG(self):
        return self.backgroundColorG


    def getBackgroundColorB(self):
        return self.backgroundColorB


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


    def setColor(self, value):
        self.color = value
        self.setColorB(value.b)
        self.setColorG(value.g)
        self.setColorR(value.r)


    def setBackgroundColor(self, value):
        self.backgroundColor = value
        self.setBackgroundColorB(value.b)
        self.setBackgroundColorG(value.g)
        self.setBackgroundColorR(value.r)


    def setColorR(self, value):
        self.colorR = value


    def setColorG(self, value):
        self.colorG = value


    def setColorB(self, value):
        self.colorB = value


    def setBackgroundColorR(self, value):
        self.backgroundColorR = value


    def setBackgroundColorG(self, value):
        self.backgroundColorG = value


    def setBackgroundColorB(self, value):
        self.backgroundColorB = value


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
        if self.AIClassName and not self.AIClass:
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
        G.game.message(self.The() + " attacks " + enemy.the())
        print self.The() + " attacks " + enemy.the()
        
    def the(self):
        return "the " + self.getName()
    
    def The(self):
        return "The " + self.getName()
    
    def a_an(self):
        if self.getName().startswith(('a', 'e', 'i', 'o', 'u')):
            return "an " + self.getName()
        else:
            return "a " + self.getName()
    
    def A_An(self):
        if self.getName().startswith(('a', 'e', 'i', 'o', 'u')):
            return "An " + self.getName()
        else:
            return "A " + self.getName()
        
    def pickUpItem(self, item):
        
        G.game.message(self.The() + " picks up " + item.a_an())
        self.getInventory().addItem(item)
    
    

class Orc(Creature):
    
    def __init__(self, **kwargs):
        super(Orc, self).__init__(symbol = 'o', color = colors.red, background = colors.black, 
                                  name = 'orc', description = 'a hideous orc', species = 'orc',
                                  maxHP = 10, AIClass = AI.AggressiveAI, **kwargs)
    
    __mapper_args__ = {'polymorphic_identity': 'orc'}


    








