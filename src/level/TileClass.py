'''
Created on Mar 10, 2013

@author: dstu
'''

from pubsub import pub
import Util as U
import colors
import InventoryClass as Inv
import random
from DungeonFeatureClass import Door

# A parent class for both level and world map tiles
class TileBase(colors.withBackgroundColor):
    
    def __init__(self, x, y, **kwargs):
        super(TileBase, self).__init__(**kwargs)
        
        self.x = x
        self.y = y
        
        self.blockMove = kwargs.get('blockMove', False)
        self.baseDescription = kwargs.get('baseDescription', u'')
        self.baseSymbol = kwargs.get('baseSymbol', u' ')
        self.creature = kwargs.get('creature', None)
        self.feature = kwargs.get('feature', None)

    def blocksMove(self):
        raise NotImplementedError("blocksMove() not implemented, use a subclass")

    def blocksPathing(self):
        return self.blocksMove() and not self.hasClosedDoor()

    def hasClosedDoor(self):
        return self.feature is not None and isinstance(self.feature, Door) and self.feature.isClosed()
    
    def getSymbol(self):
        return self.baseSymbol
    
    def getColor(self):
        return super(TileBase, self).getColor()
    
    def getBackgroundColor(self):
        return super(TileBase, self).getBackgroundColor()
    
    def getDescription(self):
        return self.__str__()
    
    def getX(self):
        return self.x
    
    def getY(self):
        return self.y
    
    def getXY(self):
        return self.x, self.y

    def getCreature(self):
        return self.creature

    def placeCreature(self, creature):
        if self.blocksMove():
            return False
        
        oldTile = creature.getTile()
        if oldTile:
            oldTile.removeCreature()
        
        self.setCreature(creature)
        return True

    def setCreature(self, creature):
        self.creature = creature
        if creature.getTile() is not self:
            creature.setTile(self)

        pub.sendMessage("event.addedCreature", tile = self, creature = creature)
        
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
        
        self.explored = False
        self.inventory = None
        
        self.destination = None
        self.destinationOf = None
        
        self.goalTileOf = None #?
        
        self.load()
    
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

    def setFeature(self, feat):
        self.feature = feat
        if feat.getTile() is not self:
            feat.setTile(self)
        
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
    
    def getRoom(self):
        return self.room
    
    def setRoom(self, room):
        self.room = room
        if self not in room.getTiles():
            room.addTile(self)
    
    def getLevel(self):  
        return self.level
    
    def setLevel(self, level):
        self.level = level
        if self not in self.level.getTiles():
            self.level.addTile(self)
            
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

    def getInventory(self):
        self.initializeInventory()
        return self.inventory
    
    def setInventory(self, inv):
        self.inventory = inv
        if inv.getTile is not self:
            inv.setTile(self)
    
    def initializeInventory(self):
        if not self.inventory:
            self.setInventory(Inv.Inventory())

# Some classes representing different kinds of tiles

class Wall(Tile):
    
    def __init__(self, x, y, **kwargs):
        super(Wall, self).__init__(x, y, blockMove = True, blockSight = True, baseSymbol = u'#', **kwargs)
    
    backgroundColor = colors.black
    
class WoodWall(Wall):
    
    def __init__(self, x, y, **kwargs):
        super(WoodWall, self).__init__(x, y, baseDescription = u"A wooden wall", **kwargs)
        
    color = colors.colorWood
    
class RockWall(Wall):
    
    def __init__(self, x, y, **kwargs):
        super(RockWall, self).__init__(x, y, baseDescription = u"A rock wall", **kwargs)
    
    color = colors.colorRock
    
class StoneWall(Wall):
    
    def __init__(self, x, y, **kwargs):
        super(StoneWall, self).__init__(x, y, baseDescription = u"A stone wall", **kwargs)
    
    color = colors.colorStone
    
class Floor(Tile):
        
    def __init__(self, x, y, **kwargs):
        super(Floor, self).__init__(x, y, blockMove = False, blockSight = False, **kwargs)
    
    backgroundColor = colors.black
    
class StoneFloor(Floor):
        
    def __init__(self, x, y, **kwargs):
        super(StoneFloor, self).__init__(x, y, baseDescription = u"A stone floor", baseSymbol = u'.', **kwargs)
        
    color =  colors.colorStone
    
class GrassFloor(Floor):
            
    def __init__(self, x, y, **kwargs):
        super(GrassFloor, self).__init__(x, y, baseDescription = u"Grass", baseSymbol = random.choice([u'.', u',']), **kwargs)
        
    color = colors.colorGrass
    
class WoodFloor(Floor):
            
    def __init__(self, x, y, **kwargs):
        super(WoodFloor, self).__init__(x, y, baseDescription = u"A wooden floor", baseSymbol = u'.', **kwargs)
    
    color = colors.colorWood
    
class RockTunnel(Floor):
    
    def __init__(self, x, y, **kwargs):
        super(RockTunnel, self).__init__(x, y, baseDescription = u"A rocky tunnel", baseSymbol = u'.', **kwargs)
        
    color = colors.colorRock
    
class RoadFloor(Floor):
    
    def __init__(self, x, y, **kwargs):
        super(RoadFloor, self).__init__(x, y, baseDescription = u"A dirt road", baseSymbol = u'~', **kwargs)
        
    color = colors.brown
