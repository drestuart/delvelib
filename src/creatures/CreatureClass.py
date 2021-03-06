'''
Created on Mar 13, 2013

@author: dstu
'''

import AIClass as AI
import colors
import InventoryClass as I
from pubsub import pub

killEventPrefix = "event.creature.kill."
questKillEventPrefix = "event.quest.creature.kill."

class Creature(colors.withColor):
    
    blockSight = False
    description = "creature"
    creatureType = "creature"
    
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
        
        self.tile = None
        self.goalEnemy = None
        self.goalTile = None

        self.load()
        
        self.setInventory(I.Inventory())
        self.level = None

        self.givingQuest = None
        self.returnQuest = None
        self.questTarget = kwargs.get('questTarget', False)

    def load(self):
        self.hateList = ['player']
    
    def killEvent(self):
        pub.sendMessage(self.getKillEvent(), creature=self)
        if self.isQuestTarget():
            pub.sendMessage(self.getQuestKillEvent(), creature=self)
    
    @classmethod
    def getKillEvent(cls):
        return killEventPrefix + cls.creatureType
    
    @classmethod
    def getQuestKillEvent(cls):
        return questKillEventPrefix + cls.creatureType
        
    def getInventory(self):
        return self.inventory
    
    def setInventory(self, inv):
        self.inventory = inv
        if self.inventory.getCreature() is not self:
            self.inventory.setCreature(self)
    
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
        import Game as G
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
            return True
        
        else:
            return False
    
    def getTile(self):
        return self.tile
    
    def setTile(self, tile):
        self.tile = tile
        if tile and tile.getCreature() is not self:
            tile.setCreature(self)
        
    def getX(self):
        return self.tile.getX()
    
    def getY(self):
        return self.tile.getY()
    
    def getXY(self):
        return self.tile.getXY()
        
    def getLevel(self):
        return self.level
    
    def setLevel(self, lvl):
        oldLevel = self.level
        if oldLevel:
            oldLevel.removeCreature(self)

        self.level = lvl
        if self not in self.level.getCreatures():
            self.level.addCreature(self)
    
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
        import Game as G
        self.killEvent()
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
        if self.__dict__.get("AIClass"):
            return self.AIClass
        self.AIClass = AI.__dict__.get(self.AIClassName)
        return self.AIClass
    
    def getAI(self):
        if self.__dict__.get("AI"):
            return self.AI
        self.AI = self.getAIClass()()
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

    def isQuestTarget(self):
        return self.questTarget

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

    def getGivingQuest(self):
        return self.givingQuest

    def setGivingQuest(self, quest):
        self.givingQuest = quest
        if self is not quest.getQuestGivingNPC():
            quest.setQuestGivingNPC(self)

    def getReturnQuest(self):
        return self.returnQuest
    
    def setReturnQuest(self, quest):
        self.returnQuest = quest
        if self is not quest.getQuestReturnNPC():
            quest.setQuestReturnNPC(self)
        
    def canSeeCreature(self, creature):
        return self.level.isTileInFOV(self.getTile(), creature.getTile())
        
    def attack(self, enemy):
        import Game as G
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
        import Game as G
        G.message(self.The() + " picks up " + item.a_an())
        self.getInventory().addItem(item)
    
    def dropItem(self, item):
        import Game as G
        G.message(self.The() + " drops " + item.a_an())
#         self.getInventory().removeItem(item)
    

class Orc(Creature):
    color = colors.red
    species = 'orc'
    description = 'a hideous orc'
    creatureType = 'orc'
    
    def __init__(self, **kwargs):
        super(Orc, self).__init__(symbol = u'o', name = u'orc', maxHP = 4, AIClass = AI.AggressiveAI, **kwargs)


