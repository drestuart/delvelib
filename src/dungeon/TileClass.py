'''
Created on Mar 10, 2013

@author: dstu
'''

from Import import *
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.types import String, Integer, Boolean
import Util as U
import colors
import database as db
import InventoryClass as Inv

libtcod = importLibtcod()

#from DungeonFeatureClass import *

Base = db.saveDB.getDeclarativeBase()

# The Tile class

class Tile(Base):
    # a tile of the map and its properties
    
    __tablename__ = "tiles"
#    __table_args__ = (UniqueConstraint('x', 'y', 'levelId', name='_tile_location_uc'), {'extend_existing': True})
    __table_args__ = {'extend_existing': True}

    
    def __init__(self, x, y, **kwargs):
        #print "Tile.__init__"
        self.x = x
        self.y = y
        
        self.blockMove = kwargs.get('blockMove', False)
        self.blockSight = kwargs.get('blockSight', False)
       
        self.baseSymbol = kwargs.get('baseSymbol', ' ')
        self.lastSeenSymbol = kwargs.get('lastSeenSymbol', ' ')
        
        self.baseColor = kwargs.get('baseColor', None)
        
        self.baseColorR = self.baseColor.r
        self.baseColorG = self.baseColor.g
        self.baseColorB = self.baseColor.b
        
        self.baseBackgroundColor = kwargs.get('baseBackgroundColor', None)
        
        self.baseBackgroundColorR = self.baseBackgroundColor.r
        self.baseBackgroundColorG = self.baseBackgroundColor.g
        self.baseBackgroundColorB = self.baseBackgroundColor.b
        
        self.baseDescription = kwargs.get('baseDescription', '')
        
        self.level = kwargs.get('level', None)
        self.room = kwargs.get('room', None)
        
        self.feature = kwargs.get('feature', None)
        
        self.creature = kwargs.get('creature', None)
        
        self.explored = False

        self.inventory = None
                

    id = Column(Integer, primary_key=True, unique=True)
    
    x = Column(Integer)
    y = Column(Integer)
    
    blockMove = Column(Boolean)
    blockSight = Column(Boolean)
    explored = Column(Boolean)
    
    baseSymbol = Column(String(length=1, convert_unicode = False))
    
    lastSeenSymbol = Column(String(length=1, convert_unicode = False))
    
    baseColorR = Column(Integer)
    baseColorG = Column(Integer)
    baseColorB = Column(Integer)
    
    baseBackgroundColorR = Column(Integer)
    baseBackgroundColorG = Column(Integer)
    baseBackgroundColorB = Column(Integer)
    
    baseDescription = Column(String)
    
#    level = relationship("Level", primaryjoin="Level.id==Tile.levelId")
    levelId = Column(Integer, ForeignKey("levels.id"))
    
#    room = relationship("Room", primaryjoin = "Room.id==Tile.roomId")
    roomId = Column(Integer, ForeignKey("rooms.id"))
    
    creatureId = Column(Integer, ForeignKey('creatures.id'))
    creature = relationship("Creature", backref=backref("tile", uselist=False), uselist = False, primaryjoin = "Tile.creatureId == Creature.id")
    
    featureId = Column(Integer, ForeignKey('dungeon_features.id'))
    feature = relationship("DungeonFeature", backref=backref("tile", uselist=False), uselist = False, primaryjoin = "Tile.featureId == DungeonFeature.id")
    
    destinationOfId = Column(Integer, ForeignKey('dungeon_features.id'))
    destinationOf = relationship("DungeonFeature", backref=backref("destination", uselist=False), uselist = False, primaryjoin = "Tile.destinationOfId == DungeonFeature.id")
    
    goalTileOfId = Column(Integer, ForeignKey('creatures.id'))
    goalTileOf = relationship("Creature", backref=backref("goalTile", uselist=False), uselist = False, primaryjoin = "Tile.goalTileOfId == Creature.id")
    
    inventoryId = Column(Integer, ForeignKey("inventories.id"))
    inventory = relationship("Inventory", backref = backref("tile", uselist = False), uselist = False, primaryjoin = "Tile.inventoryId == Inventory.id")
    
    tileType = Column(String)
    
    __mapper_args__ = {'polymorphic_on': tileType,
                       'polymorphic_identity': 'tile'}
    
    def initializeInventory(self):
        if not self.inventory:
            self.inventory = Inv.Inventory()
            
    def toDraw(self):
        # Returns a tuple of the tile's symbol, color, and background for the
        # drawing functionality
        return self.getSymbol(), self.getColor(), self.getBackground()
    
    def blocksMove(self):
        # Determine whether creatures can see through this square.
        
        if self.creature:
            #Blocked by creature.  All creatures block movement
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
        if self.inventory:
            self.initializeInventory()
            
        # Put an obj into this tile, if possible.
        if not self.blockMove:
            self.inventory.add(obj)
    
    def addObjects(self, objects):
        if self.inventory:
            self.initializeInventory()
        
        # Put several inventory into this tile
        [self.addObject(obj) for obj in objects]
            
    def removeObject(self, index):
        # Take an object from this tile
        obj = self.inventory.pop(index)
        return obj
    
    def removeObjects(self, indices):
        # Take some inventory from this tile
        return [self.removeObject(ind) for ind in indices]
    
    def placeCreature(self, creature):
        if (not self.blocksMove()) and (not self.creature):
            if creature.getTile():
                creature.getTile().removeCreature()
            
            self.creature = creature
            self.creature.setTile(self)
            return True
        
        else:
            return False
        
    def removeCreature(self):
        if self.creature:
            self.creature.setTile(None)
            self.creature = None
            return True
        
        else:
            return False
            
    def passTime(self, turns = 1):
        '''Pass some time on the inventory and creature on this tile'''
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
        
        if self.creature and self.creature.isVisible():
            toReturn = self.creature.getSymbol()
        
        elif self.feature and self.feature.isVisible():
            toReturn = self.feature.getSymbol()
#        
#        elif self.inventory:
#            toReturn = self.inventory[0].symbol()
#        
        else:
            toReturn = self.baseSymbol
        
        self.setLastSeenSymbol(toReturn)
        return toReturn
        
    def getColor(self):
        # Determine which color to use to draw this tile
        
        if self.creature and self.creature.isVisible():
            return self.creature.getColor()
        
        elif self.feature and self.feature.isVisible():
            return self.feature.getColor()
#        
#        elif self.inventory:
#            return self.inventory[0].color()
#        
        else:
            return self.getBaseColor()
        
    def getBaseColor(self):        
        if self.__dict__.get('color', None):
            return self.baseColor
        else:
            self.color = libtcod.Color(self.baseColorR, self.baseColorG, self.baseColorB)
            return self.baseColor

    def getBackground(self):
        # Determine which background to use to draw this tile
#        if self.creature and self.creature.isVisible():
#            return self.creature.background()
        
        if self.feature and self.feature.isVisible():
            return self.feature.getBackgroundColor()
                
        else:
            return self.getBaseBackgroundColor()
        
    def getBaseBackgroundColor(self):
        if self.__dict__.get('baseBackgroundColor', None):
            return self.baseBackgroundColor
        else:
            self.baseBackgroundColor = libtcod.Color(self.baseBackgroundColorR, self.baseBackgroundColorG, self.baseBackgroundColorB)
            return self.baseBackgroundColor

    def getDescription(self):
        # Determine which description to use to draw this tile
        if self.creature and self.creature.isVisible():
            return self.creature.description
        
        elif self.feature and self.feature.isVisible():
            return self.feature.description
        
        elif self.inventory and self.inventory.length() > 0:
            return self.inventory.getItem(0).getDescription()
        
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
            
    def getX(self):
        return self.x
    
    def getY(self):
        return self.y
    
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
        
    def distance(self, other):
        return U.ChebyshevDistance(self.getX(), other.getX(), self.getY(), other.getY())


# Some classes representing different kinds of tiles

class Wall(Tile):
    
    def __init__(self, x, y, **kwargs):
        super(Wall, self).__init__(x, y, blockMove = True, blockSight = True, baseBackgroundColor = colors.black, baseSymbol = '#', **kwargs)
    
    __mapper_args__ = {'polymorphic_identity': 'wall'}
    
class WoodWall(Wall):
    
    def __init__(self, x, y, **kwargs):
        super(WoodWall, self).__init__(x, y, baseDescription = "A wooden wall", baseColor = colors.colorWood, **kwargs)
    
    __mapper_args__ = {'polymorphic_identity': 'woodwall'}

class RockWall(Wall):
    
    def __init__(self, x, y, **kwargs):
        super(RockWall, self).__init__(x, y, baseDescription = "A rock wall", baseColor = colors.colorRock, **kwargs)
    
    __mapper_args__ = {'polymorphic_identity': 'rockwall'}


class Floor(Tile):
        
    def __init__(self, x, y, **kwargs):
        #print "Floor.__init__"
        super(Floor, self).__init__(x, y, blockMove = False, blockSight = False, baseBackgroundColor = colors.black, baseSymbol = '.', **kwargs)
    
    __mapper_args__ = {'polymorphic_identity': 'floor'}

class StoneFloor(Floor):
        
    def __init__(self, x, y, **kwargs):
        #print "StoneFloor.__init__"
        super(StoneFloor, self).__init__(x, y, baseDescription = "A stone floor", baseColor =  colors.colorStone, **kwargs)
    
    __mapper_args__ = {'polymorphic_identity': 'stonefloor'}

class GrassFloor(Floor):
            
    def __init__(self, x, y, **kwargs):
        super(GrassFloor, self).__init__(x, y, baseDescription = "Grass", baseColor = colors.colorGrass, **kwargs)
    
    __mapper_args__ = {'polymorphic_identity': 'grassfloor'}

class WoodFloor(Floor):
            
    def __init__(self, x, y, **kwargs):
        super(WoodFloor, self).__init__(x, y, baseDescription = "A wooden floor", baseColor = colors.colorWood, **kwargs)
    
    __mapper_args__ = {'polymorphic_identity': 'woodfloor'}

class RockTunnel(Floor):
    
    def __init__(self, x, y, **kwargs):
        super(RockTunnel, self).__init__(x, y, baseDescription = "A rocky tunnel", baseColor = colors.colorRock, **kwargs)
    
    __mapper_args__ = {'polymorphic_identity': 'rocktunnel'}
        

            
def main():
    
    import LevelClass
    import RoomClass
    
    db.saveDB.start(True)
#    db.saveDB.start()

    
    t2 = StoneFloor(x=3, y=4)
    print t2.getColor()
    
    

if __name__ == '__main__':
    main()

