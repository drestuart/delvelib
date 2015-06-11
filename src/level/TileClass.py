'''
Created on Mar 10, 2013

@author: dstu
'''

from pubsub import pub
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Unicode, Integer, Boolean
import Util as U
import colors
import database as db
import InventoryClass as Inv
import random
from DungeonFeatureClass import Door

#from DungeonFeatureClass import *

Base = db.saveDB.getDeclarativeBase()

# A parent class for both level and world map tiles
class TileBase(colors.withBackgroundColor, Base):
    
    __tablename__ = "tiles"
    __table_args__ = {'extend_existing': True}
    
    def __init__(self, x, y, **kwargs):
        super(TileBase, self).__init__(**kwargs)
        
        self.x = x
        self.y = y
        
        self.blockMove = kwargs.get('blockMove', False)
        self.baseDescription = kwargs.get('baseDescription', u'')
        self.baseSymbol = kwargs.get('baseSymbol', u' ')
        self.creature = kwargs.get('creature', None)


    id = Column(Integer, primary_key=True, unique=True)
    
    x = Column(Integer)
    y = Column(Integer)
    
    creatureId = Column(Integer, ForeignKey('creatures.id'))
    creature = relationship("Creature", backref=backref("tile", uselist=False), uselist = False, primaryjoin = "Tile.creatureId == Creature.id")
    
    tileType = Column(Unicode)

    blockMove = Column(Boolean)

    baseSymbol = Column(Unicode(length=1))
    baseDescription = Column(Unicode)

    tileType = Column(Unicode)

    __mapper_args__ = {'polymorphic_on': tileType,
                       'polymorphic_identity': u'tileBase'}
    
    def blocksMove(self):
        raise NotImplementedError("blocksMove() not implemented, use a subclass")
    
#     def placeCreature(self, creature):
#         raise NotImplementedError("placeCreature() not implemented, use a subclass")
# 
#     def removeCreature(self):
#         raise NotImplementedError("removeCreature() not implemented, use a subclass")
    
    def getSymbol(self):
        return self.baseSymbol
    
    def getColor(self):
        return super(TileBase, self).getColor()
    
    def getBackgroundColor(self):
        return super(TileBase, self).getBackgroundColor()
    
    def getDescription(self):
        return self.__str__()
    
    def __str__(self):
        return self.baseDescription
    
    def getX(self):
        return self.x
    
    def getY(self):
        return self.y
    
    def getXY(self):
        return self.x, self.y
    
    def placeCreature(self, creature):
        if self.blocksMove():
            return False
        
        oldTile = creature.getTile()
        if oldTile:
            oldTile.removeCreature()
        
        self.creature = creature
        self.creature.setTile(self)
        pub.sendMessage("event.addedCreature", tile = self, creature = creature)
        return True
        
        
    def removeCreature(self):
        if self.creature:
            creature = self.creature
            creature.setTile(None)
            self.creature = None
            pub.sendMessage("event.removedCreature", tile = self, creature = creature)
            return True
        
        else:
            return False
        
    def getLastSeenSymbol(self):
        return self.baseSymbol
    
    def distance(self, other):
        return U.ChebyshevDistance(self.getX(), other.getX(), self.getY(), other.getY())



class Tile(TileBase):
    # A tile of the map and its properties
    
    def __init__(self, x, y, **kwargs):
        super(Tile, self).__init__(x, y, **kwargs)
        
        self.blockSight = kwargs.get('blockSight', False)

        self.lastSeenSymbol = kwargs.get('lastSeenSymbol', u' ')
        
        self.level = kwargs.get('level', None)
        self.room = kwargs.get('room', None)
        
        self.feature = kwargs.get('feature', None)
        self.explored = False
        self.inventory = None
        
        self.load()
    
    
    blockSight = Column(Boolean)
    explored = Column(Boolean)
    
    lastSeenSymbol = Column(Unicode(length=1))
    
#    level = relationship("Level", primaryjoin="Level.id==Tile.levelId")
    levelId = Column(Integer, ForeignKey("levels.id"))
    
#    room = relationship("Room", primaryjoin = "Room.id==Tile.roomId")
    roomId = Column(Integer, ForeignKey("rooms.id"))
    
    featureId = Column(Integer, ForeignKey('dungeon_features.id'))
    feature = relationship("DungeonFeature", backref=backref("tile", uselist=False), uselist = False, primaryjoin = "Tile.featureId == DungeonFeature.id")
    
    destinationOfId = Column(Integer, ForeignKey('dungeon_features.id'))
    destinationOf = relationship("DungeonFeature", backref=backref("destination", uselist=False), uselist = False, primaryjoin = "Tile.destinationOfId == DungeonFeature.id")
    
    goalTileOfId = Column(Integer, ForeignKey('creatures.id'))
    goalTileOf = relationship("Creature", backref=backref("goalTile", uselist=False), uselist = False, primaryjoin = "Tile.goalTileOfId == Creature.id")
    
    inventoryId = Column(Integer, ForeignKey("inventories.id"))
    inventory = relationship("Inventory", backref = backref("tile", uselist = False), uselist = False, primaryjoin = "Tile.inventoryId == Inventory.id")
    
    __mapper_args__ = {'polymorphic_identity': u'tile'}
    
    def load(self):
        self.visibleTiles = None
        
    def bump(self, bumper):    
        if self.creature:
            return self.creature.handleBump(bumper)
        
        if self.feature:
            return self.feature.handleBump(bumper)
        
        return self.handleBump(bumper)
        
    def handleBump(self, bumper):
        return False
    
    def initializeInventory(self):
        if not self.inventory:
            self.inventory = Inv.Inventory()
            
    def toDraw(self):
        # Returns a tuple of the tile's symbol, color, and background for the
        # drawing functionality
        return self.getSymbol(), self.getColor(), self.getBackgroundColor()
    
    def blocksMove(self):
        # Determine whether creatures can see through this square.
        
        if self.creature:
            # Blocked by creature.  All creatures block movement
            return True 
        
        blocks = self.blockMove
                
        if self.feature:
            # If there's a dungeon feature, determine if it blocks movement
            # before returning. This also accounts for the case of a non-
            # blocking feature in a blocking square, which seems unlikely.
            blocks = blocks or self.feature.getBlockMove()
                
        return blocks
    
    def blocksSight(self):
        # Determine whether creatures can see through this square.  Similar to
        # the above blocksMove()
        
        blocks = self.blockSight
        if self.creature:
            # Blocked by creature.  Not all creatures block sight
            blocks = blocks or self.creature.blockSight 
        
        elif self.feature:
            # If there's a dungeon feature, determine if it blocks sight. This
            # also accounts for the case of a non-blocking feature in a blocking
            # square, which seems unlikely.
            blocks = blocks or self.feature.getBlockSight()
                
        return blocks
    
    def blocksPathing(self):
        return self.blocksMove() and not self.hasClosedDoor()
    
    def hasClosedDoor(self):
        return self.feature is not None and isinstance(self.feature, Door) and self.feature.isClosed()
    
    def addObject(self, obj):
        if not self.inventory:
            self.initializeInventory()
            
        # Put an obj into this tile, if possible.
        if not self.blockMove:
            self.inventory.addItem(obj)
    
    def addObjects(self, objects):
        if not self.inventory:
            self.initializeInventory()
        
        # Put several inventory into this tile
        [self.addObject(obj) for obj in objects]
            
    def removeObject(self, index):
        if self.inventory:
            # Take an object from this tile
            obj = self.inventory.pop(index)
            return obj
    
    def removeObjects(self, indices):
        # Take some inventory from this tile
        return [self.removeObject(ind) for ind in indices]
    
    def passTime(self, turns = 1):
        '''Pass some time on the inventory and creature on this tile'''
        
        if self.inventory:
            for obj in self.inventory.getItems():
                obj.passTime(turns)
            
#        if self.creature is not None:
#            self.creature.passTime(turns)
            
        if self.feature is not None:
            self.feature.passTime(turns)
        
        
    def getFeature(self):
        return self.feature

    def setFeature(self, value):
        self.feature = value    
        
    def getSymbol(self):
        # Determine which symbol to use to draw this tile
        
#         if self.creature and self.creature.isVisible():
        if self.creature and self.creature.isVisible():

            toReturn = self.creature.getSymbol()
            
        elif self.inventory and self.inventory.length() > 0:
            return self.inventory.getItem(0).getSymbol()
        
        elif self.feature and self.feature.isVisible():
            toReturn = self.feature.getSymbol()

        else:
            toReturn = self.baseSymbol
        
#        self.setLastSeenSymbol(toReturn)
        return toReturn
        
    def getColor(self):
        # Determine which color to use to draw this tile
        
        if self.creature and self.creature.isVisible():
            return self.creature.getColor()
        
        elif self.inventory and self.inventory.length() > 0:
            return self.inventory.getItem(0).getColor()
        
        elif self.feature and self.feature.isVisible():
            return self.feature.getColor()
       
        else:
            return super(Tile, self).getColor()

    def getBackgroundColor(self):
        # Determine which background to use to draw this tile
#        if self.creature and self.creature.isVisible():
#            return self.creature.background()
        
        if self.feature and self.feature.isVisible():
            return self.feature.getBackgroundColor()
                
        else:
            return super(Tile, self).getBackgroundColor()
        
    def getDescription(self):
        # Determine which description to use to draw this tile
        if self.creature and self.creature.isVisible():
            return self.creature.getDescription()
        
        elif self.inventory and self.inventory.length() > 0:
            return self.inventory.getItem(0).getDescription()
        
        elif self.feature and self.feature.isVisible():
            return self.feature.getDescription()
        
        else:
            return self.baseDescription 
        
    def getLevel(self):  
        return self.level
        
    def __str__(self):
        return self.baseDescription
    
    def setLevel(self, level):
        self.level = level
        if level:
            self.levelId = level.id
        else:
            self.levelId = None
            
    def getExplored(self):
        return self.explored

    def setExplored(self, value):
        self.explored = value

    def getLastSeenSymbol(self):
        return self.lastSeenSymbol

    def setLastSeenSymbol(self, value):
        self.lastSeenSymbol = value

    def getGoalTileOf(self):
        return self.goalTileOf

    def setGoalTileOf(self, value):
        self.goalTileOf = value

    def getCreature(self):
        return self.creature

    def setCreature(self, value):
        self.creature = value
        
    def getInventory(self):
        return self.inventory

# Some classes representing different kinds of tiles

class Wall(Tile):
    
    def __init__(self, x, y, **kwargs):
        super(Wall, self).__init__(x, y, blockMove = True, blockSight = True, baseSymbol = u'#', **kwargs)
    
    backgroundColor = colors.black
    
    __mapper_args__ = {'polymorphic_identity': u'wall'}
    
class WoodWall(Wall):
    
    def __init__(self, x, y, **kwargs):
        super(WoodWall, self).__init__(x, y, baseDescription = u"A wooden wall", **kwargs)
        
    color = colors.colorWood
    
    __mapper_args__ = {'polymorphic_identity': u'woodwall'}

class RockWall(Wall):
    
    def __init__(self, x, y, **kwargs):
        super(RockWall, self).__init__(x, y, baseDescription = u"A rock wall", **kwargs)
    
    color = colors.colorRock
    
    __mapper_args__ = {'polymorphic_identity': u'rockwall'}
    
class StoneWall(Wall):
    
    def __init__(self, x, y, **kwargs):
        super(StoneWall, self).__init__(x, y, baseDescription = u"A stone wall", **kwargs)
    
    color = colors.colorStone
    
    __mapper_args__ = {'polymorphic_identity': u'stonewall'}


class Floor(Tile):
        
    def __init__(self, x, y, **kwargs):
        #print "Floor.__init__"
        super(Floor, self).__init__(x, y, blockMove = False, blockSight = False, **kwargs)
    
    backgroundColor = colors.black
    
    __mapper_args__ = {'polymorphic_identity': u'floor'}

class StoneFloor(Floor):
        
    def __init__(self, x, y, **kwargs):
        #print "StoneFloor.__init__"
        super(StoneFloor, self).__init__(x, y, baseDescription = u"A stone floor", baseSymbol = u'.', **kwargs)
        
    color =  colors.colorStone
    
    __mapper_args__ = {'polymorphic_identity': u'stonefloor'}

class GrassFloor(Floor):
            
    def __init__(self, x, y, **kwargs):
        super(GrassFloor, self).__init__(x, y, baseDescription = u"Grass", baseSymbol = random.choice([u'.', u',']), **kwargs)
        
    color = colors.colorGrass
    
    __mapper_args__ = {'polymorphic_identity': u'grassfloor'}

class WoodFloor(Floor):
            
    def __init__(self, x, y, **kwargs):
        super(WoodFloor, self).__init__(x, y, baseDescription = u"A wooden floor", baseSymbol = u'.', **kwargs)
    
    color = colors.colorWood
    
    __mapper_args__ = {'polymorphic_identity': u'woodfloor'}

class RockTunnel(Floor):
    
    def __init__(self, x, y, **kwargs):
        super(RockTunnel, self).__init__(x, y, baseDescription = u"A rocky tunnel", baseSymbol = u'.', **kwargs)
        
    color = colors.colorRock
    
    __mapper_args__ = {'polymorphic_identity': u'rocktunnel'}
    
class RoadFloor(Floor):
    
    def __init__(self, x, y, **kwargs):
        super(RoadFloor, self).__init__(x, y, baseDescription = u"A dirt road", baseSymbol = u'~', **kwargs)
        
    color = colors.brown
        
    __mapper_args__ = {'polymorphic_identity': u'roadfloor'}

