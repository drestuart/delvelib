'''
Created on Mar 13, 2013

@author: dstu
'''

from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Unicode, Integer, Boolean
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
        
        self.name = kwargs.get('name', None)
        
        self.maxHP = kwargs['maxHP']
        self.hp = kwargs['maxHP']
        self.damageTaken = kwargs.get('damageTaken', 0)
        self.dead = False
        
        self.visible = kwargs.get('visible', True)
        self.AIClass = kwargs['AIClass']
        self.AIClassName = unicode(kwargs['AIClass'].__name__)
        
        self.AI = self.AIClass()
        self.AI.setOwner(self)

        self.load()
        
        self.inventory = I.Inventory()


    id = Column(Integer, primary_key=True, unique=True)
    
    symbol = Column(Unicode(length=1))
    
    name = Column(Unicode)
    creatureType = Column(Unicode)
    
    maxHP = Column(Integer)
    damageTaken = Column(Integer)
    dead = Column(Boolean)
    
    goalEnemy = relationship("Creature", uselist=False)
    goalEnemyId = Column(Integer, ForeignKey('creatures.id'))
    
    inventoryId = Column(Integer, ForeignKey("inventories.id"))
    inventory = relationship("Inventory", backref = backref("creature", uselist = False), uselist = False, primaryjoin = "Creature.inventoryId == Inventory.id")
    
    levelId = Column(Integer, ForeignKey('levels.id'))
    level = relationship("Level", backref=backref("creatures"), uselist = False, primaryjoin = "Creature.levelId == Level.id")
    
    givingQuestId = Column(Integer, ForeignKey("quests.id"))
    
    visible = Column(Boolean)
    
    AIClassName = Column(Unicode)
    
    __mapper_args__ = {'polymorphic_on': creatureType,
                       'polymorphic_identity': u'creature'}
    
    def load(self):
        self.hateList = ['player']
        
    def getInventory(self):
        return self.inventory
    
    def handleBump(self, bumper):
        # Decide whether to handle an attack, start a dialog, or whatever
        return bumper.attack(self)
    
    def move(self, dx, dy):
        
        newX = self.getX() + dx
        newY = self.getY() + dy
        level = self.getLevel()
        nextTile = level.getTile(newX, newY)
        
        if nextTile.hasClosedDoor():
            return self.openDoor(nextTile)
        else:
            return self.moveToTile(nextTile)
        
    def openDoor(self, tile):
        # Probably redundant error checking
        if not tile.hasClosedDoor():
            raise Exception("Trying to open an open or non-existent door")
        
        tile.getFeature().open_()
        message = self.The() + " opens a door " + str(tile.getXY())
        G.message(message)
        return True
        
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
        self.damageTaken = max(self.damageTaken - amount, 0)
        self.calcHP()
        if self.hp <= 0:
            self.die()
            
    def die(self):
        message = self.The() + " dies!"
        G.message(message)
        print message
        
        self.dead = True
            
    def getHP(self):
        return self.hp

    def getName(self):
        return self.name

    def getDescription(self):
        return self.name or self.description

    def getSpecies(self):
        return self.species

    def getMaxHP(self):
        return self.maxHP

    def getDamageTaken(self):
        return self.damageTaken

    def getAIClass(self):
        return self.AIClass
    
    def getAI(self):
        if self.__dict__.get("AI"):
            return self.AI
        self.AI = self.AIClass()
        return self.AI

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
    
    def isDead(self):
        return self.dead

    def setVisible(self, value):
        self.visible = value

    def getSymbol(self):
        return self.symbol

    def setSymbol(self, value):
        self.symbol = value
        
    def takeTurn(self):
        self.getAI().takeTurn()
        
    def getGoalTile(self):
        return self.goalTile
    
    def setGoalTile(self, newTile):
        self.goalTile = newTile
        if newTile is not None:
            newTile.setGoalTileOf(self)
            print "Setting goal tile to", (newTile.getXY())
        else:
            print "Setting goal tile to None"
        
    def distance(self, other):
        return self.getTile().distance(other.getTile())

    def getCreatureType(self):
        return self.creatureType

    def getGoalEnemy(self):
        return self.goalEnemy

    def setGoalEnemy(self, value):
        self.goalEnemy = value

    def getHateList(self):
        return self.hateList

    def setHateList(self, value):
        self.hateList = value
        
    def canSeeCreature(self, creature):
        return self.level.isTileInFOV(self.getTile(), creature.getTile())
        
    def attack(self, enemy):
        damage = self.getAttackDamage()
        
        message = self.The() + " attacks " + enemy.the() + " for " + str(damage)
        G.message(message)
        print message
        
        enemy.takeDamage(damage)
        
        return True
        
    def getAttackDamage(self):
        # A highly sophisticated algorithm, taking into account material properties,
        # the creature's lever arm, and the local wind speed
        return 2
    
    def getAttackRange(self):
        return 1

    def getPath(self):
        return self.getAI().path

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
    
    def dropItem(self, item):
        G.message(self.The() + " drops " + item.a_an())
#         self.getInventory().removeItem(item)
    

class Orc(Creature):
    color = colors.red
    species = 'orc'
    description = 'a hideous orc'
    
    def __init__(self, **kwargs):
        super(Orc, self).__init__(symbol = u'o', name = u'orc', maxHP = 4, AIClass = AI.AggressiveAI, **kwargs)
    
    __mapper_args__ = {'polymorphic_identity': u'orc'}


    








