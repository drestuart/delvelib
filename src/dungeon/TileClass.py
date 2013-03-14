'''
Created on Mar 10, 2013

@author: dstu
'''

from Import import *
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.types import String, Integer, Boolean
import colors
import database as db

libtcod = importLibtcod()

#from DungeonFeatureClass import *
#from InventoryClass import *

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

#        libtcod.Color(0,0,0)

        
#        self.objects = ItemInventory()      # The objects on this tile 
#        self.creature = None   
#        self.feature = kwargs['feature']
        

    id = Column(Integer, primary_key=True, unique=True)
    
    x = Column(Integer)
    y = Column(Integer)
    
    blockMove = Column(Boolean)
    blockSight = Column(Boolean)
    
    baseSymbol = Column(String(length=1, convert_unicode = False))
    
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
    
    feature_id = Column(Integer, ForeignKey('dungeon_features.id'))
    feature = relationship("DungeonFeature", backref=backref("tile", uselist=False), uselist = False, primaryjoin = "Tile.feature_id == DungeonFeature.id") #
    
    destinationOfId = Column(Integer, ForeignKey('dungeon_features.id'))
    destinationOf = relationship("DungeonFeature", backref=backref("destination", uselist=False), uselist = False, primaryjoin = "Tile.destinationOfId == DungeonFeature.id")
    
    
    tileType = Column(String)
    
    __mapper_args__ = {'polymorphic_on': tileType,
                       'polymorphic_identity': 'tile'}
            
    def toDraw(self):
        # Returns a tuple of the tile's symbol, color, and background for the
        # drawing functionality
        return self.getSymbol(), self.getColor(), self.getBackground()
    
    def blocksMove(self):
        # Determine whether creatures can see through this square.
        
#        if self.creature:
            # Blocked by creature.  All creatures block movement
#            return True 
        
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
        # Put an obj into this tile, if possible.
        if not self.blockMove:
            self.objects.add(obj)
    
    def addObjects(self, objects):
        # Put several objects into this tile
        [self.addObject(obj) for obj in objects]
            
    def removeObject(self, index):
        # Take an object from this tile
        obj = self.objects.pop(index)
        return obj
    
    def removeObjects(self, indices):
        # Take some objects from this tile
        return [self.removeObject(ind) for ind in indices]
    
    def addCreature(self, creature):
        if (not self.blocksMove()) and (not self.creature):
            self.__dict__['creature'] = creature
            return True
        
        else:
            return False
        
    def removeCreature(self):
        if self.creature:
            self.__dict__['creature'] = None
            return True
        
        else:
            return False
            
    def passTime(self, turns = 1):
        '''Pass some time on the objects and creature on this tile'''
        for obj in self.objects:
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
        
#        if self.creature and self.creature.isVisible():
#            return self.creature.symbol()
#        
        if self.feature and self.feature.isVisible():
            return self.feature.getSymbol()
#        
#        elif self.objects:
#            return self.objects[0].symbol()
#        
        else:
            return self.baseSymbol
        
    def getColor(self):
        # Determine which color to use to draw this tile
        
#        if self.creature and self.creature.isVisible():
#            return self.creature.color()
#        
        if self.feature and self.feature.isVisible():
            return self.feature.getColor()
#        
#        elif self.objects:
#            return self.objects[0].color()
#        
        else:
            return self.getBaseColor()
        
    def getBaseColor(self):        
        if self.__dict__.get('baseColor', None):
            return self.baseColor
        else:
            self.baseColor = libtcod.Color(self.baseColorR, self.baseColorG, self.baseColorB)
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
        
        elif self.objects:
            return self.objects[0].description
        
        else:
            return self.baseDescription   
        
    def __str__(self):
        return self.baseDescription
    
    def __eq__(self, other):
        
        if self is None and other is None:
            return True
        
        elif (self is None or other is None):
            return False

        else:
            return self.x == other.x and self.y == other.y and self.levelId == other.levelId
    
    def setLevel(self, level):
        self.level = level
        if level:
            self.levelId = level.id
        else:
            self.levelId = None
        
    
#    # drawing management stuff. will be moved to the console class?    
#    def draw(self, con):
#        #set the color and then draw the character that represents this object
#        #at its position
#        libtcod.console_set_foreground_color(con, self.color())
#        libtcod.console_put_char(con, self.x, self.y, self.symbol(), self.background)
# 
#    def clear(self, con):
#        #erase the character that represents this object
#        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)
        

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

