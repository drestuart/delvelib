'''
Created on Mar 13, 2013

@author: dstu
'''

from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.types import String, Integer, Boolean
import AIClass as AI
import colors
import database as db
import Game as G
import InventoryClass as I

Base = db.saveDB.getDeclarativeBase()


class Creature(colors.withColor, Base):
    
    __tablename__ = "creatures"
    __table_args__ = {'extend_existing': True}
    
    blockSight = False
    description = "creature"
    
    def __init__(self, **kwargs):
        super(Creature, self).__init__(**kwargs)
        
        self.symbol = kwargs['symbol']
        
        self.name = kwargs['name']
        self.species = kwargs['species']
        
        self.maxHP = kwargs['maxHP']
        self.damageTaken = kwargs.get('damageTaken', 0)
        
        self.visible = kwargs.get('visible', True)
        self.AIClass = kwargs['AIClass']
        self.AIClassName = kwargs['AIClass'].__name__
        self.AI = None

        self.load()
        
        self.inventory = I.Inventory()


    id = Column(Integer, primary_key=True, unique=True)
    
    symbol = Column(String(length=1, convert_unicode = True))
    
    name = Column(String)
    species = Column(String)
    creatureType = Column(String)
    
    maxHP = Column(Integer)
    damageTaken = Column(Integer)
    
    goalEnemy = relationship("Creature", uselist=False)
    goalEnemyId = Column(Integer, ForeignKey('creatures.id'))
    
    inventoryId = Column(Integer, ForeignKey("inventories.id"))
    inventory = relationship("Inventory", backref = backref("creature", uselist = False), uselist = False, primaryjoin = "Creature.inventoryId == Inventory.id")
    
    levelId = Column(Integer, ForeignKey('levels.id'))
    level = relationship("Level", backref=backref("creatures"), uselist = False, primaryjoin = "Creature.levelId == Level.id")
    
    visible = Column(Boolean)
    
    AIClassName = Column(String)
    
    __mapper_args__ = {'polymorphic_on': creatureType,
                       'polymorphic_identity': 'creature'}
    
    def load(self):
        self.AIClass = None
        self.AI = None
        self.path = None
        self.hateList = ['player']
        
        self.initializeAI()
    
    def getInventory(self):
        return self.inventory
    
    def handleBump(self, bumper):
        return False
    
    def move(self, dx, dy):
        
        newX = self.getX() + dx
        newY = self.getY() + dy
        level = self.getLevel()
        newTile = level.getTile(newX, newY)
        
        return self.moveToTile(newTile)
        
        
    def moveToTile(self, newTile):
        
        level = self.getLevel()
        
        if newTile is not None and level.placeCreature(self, newTile):
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
    
    def getXY(self):
        return self.tile.getXY()
        
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

    def setName(self, value):
        self.name = value

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
        if self.AIClassName and not self.__dict__.get('AIClass'):
            self.AIClass = AI.getAIClassByName(self.AIClassName)
        else:
            self.AIClassName = self.AIClass.__name__
        
        self.AI = self.AIClass()
        self.AI.setOwner(self)
        
    def takeTurn(self):
        if not self.__dict__.get('AI'):
            self.initializeAI()
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

    def getGoalEnemy(self):
        return self.goalEnemy

    def getGoalEnemyId(self):
        return self.goalEnemyId

    def setGoalEnemy(self, value):
        self.goalEnemy = value

    def setGoalEnemyId(self, value):
        self.goalEnemyId = value

    def getPath(self):
        if not self.__dict__.get('path'):
            self.path = None
        return self.path

    def setPath(self, value):
        self.path = value

    def getHateList(self):
        return self.hateList

    def setHateList(self, value):
        self.hateList = value
        
    def attack(self, enemy):
        G.message(self.The() + " attacks " + enemy.the())
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
        
        G.message(self.The() + " picks up " + item.a_an())
        self.getInventory().addItem(item)
    
    

class Orc(Creature):
    color = colors.red
    species = 'orc'
    description = 'a hideous orc'
    
    def __init__(self, **kwargs):
        super(Orc, self).__init__(symbol = 'o', name = 'orc', maxHP = 10, AIClass = AI.AggressiveAI, **kwargs)
    
    __mapper_args__ = {'polymorphic_identity': 'orc'}


    








