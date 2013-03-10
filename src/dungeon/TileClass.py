from Import import *
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Integer, Boolean
import database as db

libtcod = importLibtcod()

#from DungeonFeatureClass import *
#from InventoryClass import *

Base = db.saveDB.getDeclarativeBase()

# The Tile class

class Tile(Base):
    # a tile of the map and its properties
    
    __tablename__ = "tiles"
    __table_args__ = {'extend_existing': True}
    
    def __init__(self, **kwargs):
        
        self.x = kwargs['x']
        self.y = kwargs['y']
        
        self.blockMove = kwargs['blockMove']
        self.blockSight = kwargs['blockSight']
       
        self.baseSymbol = kwargs['baseSymbol']
        self.baseColor = kwargs.get('baseColor', 
                                    libtcod.Color(kwargs['baseColorR'], kwargs['baseColorG'], kwargs['baseColorB']) )

        self.baseColorR = kwargs.get('baseColor', self.baseColor.r)
        self.baseColorG = kwargs.get('baseColor', self.baseColor.g)
        self.baseColorB = kwargs.get('baseColor', self.baseColor.b)
        
        self.baseBackgroundColor = kwargs.get('baseBackgroundColor', 
                                              libtcod.Color(kwargs['baseBackgroundColorR'], kwargs['baseBackgroundColorG'], kwargs['baseBackgroundColorB']) )
       
        self.baseDescription = kwargs['baseDescription']
        
        self.level = kwargs['level']
        
#        libtcod.Color(0,0,0)

        
#        self.objects = ItemInventory()      # The objects on this tile 
#        self.creature = None   
#        self.feature = kwargs['feature']
        

    id = Column(Integer, primary_key=True)
    
    x = Column(Integer)
    y = Column(Integer)
    
    blockMove = Column(Boolean)
    blockSight = Column(Boolean)
    
    baseSymbol = Column(String(length=1))
    
    baseColorR = Column(Integer)
    baseColorG = Column(Integer)
    baseColorB = Column(Integer)
    
    baseBackgroundColorR = Column(Integer)
    baseBackgroundColorG = Column(Integer)
    baseBackgroundColorB = Column(Integer)
    
    level = relationship("Level", primaryjoin="Level.id==Tile.levelId")
    levelId = Column(Integer, ForeignKey("levels.id"))
    
    
            
    def toDraw(self):
        # Returns a tuple of the tile's symbol, color, and background for the
        # drawing functionality
        return self.getSymbol(), self.getColor(), self.getBackground()
    
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
            blocks = blocks and self.feature.blockSight
                
        return blocks
    
    def blocksSight(self):
        # Determine whether creatures can see through this square.  Similar to
        # the above blocksMove()
        
        blocks = self.blockSight
        if self.creature:
            # Blocked by creature.  Not all creatures block sight
            blocks = blocks and self.creature.blockSight 
        
        elif self.feature:
            # If there's a dungeon feature, determine if it blocks sight. This
            # also accounts for the case of a non-blocking feature in a blocking
            # square, which seems unlikely.
            blocks = blocks and self.feature.blockSight
                
        return blocks
    
    def addObject(self, object):
        # Put an object into this tile, if possible.
        if not self.blockMove:
            self.objects.add(object)
    
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
        
        
    def getSymbol(self):
        # Determine which symbol to use to draw this tile
        
        if self.creature and self.creature.isVisible():
            return self.creature.symbol()
        
        elif self.feature and self.feature.isVisible():
            return self.feature.symbol()
        
        elif self.objects:
            return self.objects[0].symbol()
        
        else:
            return self.baseSymbol
        
    def getColor(self):
        # Determine which color to use to draw this tile
        
        if self.creature and self.creature.isVisible():
            return self.creature.color()
        
        elif self.feature and self.feature.isVisible():
            return self.feature.color()
        
        elif self.objects:
            return self.objects[0].color()
        
        else:
            return self.baseColor        

    def getBackground(self):
        # Determine which background to use to draw this tile
#        if self.creature and self.creature.isVisible():
#            return self.creature.background()
        
        if self.feature and self.feature.isVisible():
            return self.feature.background()
                
        else:
            return self.baseBackground   

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
        
        
        
            
def main():
    pass

if __name__ == '__main__':
    main()













