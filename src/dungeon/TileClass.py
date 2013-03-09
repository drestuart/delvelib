###############################################################
#
# OLD STUFF
#
###############################################################


# External imports
import libtcodpy as libtcod

# Internal imports
from DungeonFeatureClass import *
from InventoryClass import *
from GetSetClass import *
from CoordinatesClass import *
from colors import *

# The Tile class

class Tile(GetSet):
    #a tile of the map and its properties
    def __init__(self, x = 0, y = 0, blockMove = False, blockSight = False, baseSymbol = '.', 
                 baseColor = colorLightGround, baseBackground = libtcod.BKGND_NONE, 
                 feature = None, baseDescription = "floor"):
        
        self.__dict__['coordinates'] = Coordinates(x = x, y = y)
        self.__dict__['blockMove'] = blockMove
        self.__dict__['blockSight'] = blockSight
        self.__dict__['baseSymbol'] = baseSymbol
        self.__dict__['baseColor'] = baseColor
        self.__dict__['baseDescription'] = baseDescription
        self.__dict__['baseBackground'] = baseBackground
        
        self.__dict__['objects'] = ItemInventory()      # The objects on this tile 
        self.__dict__['creature'] = None   #The creature on this tile.  The ONE creature, by the way.
        
        self.__dict__['feature'] = feature
        

            
    def toDraw(self):
        # Returns a tuple of the tile's symbol, color, and background for the
        # drawing functionality
        return self.symbol(), self.color(), self.background()
    
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
        return [removeObject(ind) for ind in indices]
    
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
        
        
    # Some functions that show what's in the Tile        
    def symbol(self):
        # Determine which symbol to use to draw this tile
        if self.creature and self.creature.isVisible():
            return self.creature.symbol()
        
        elif self.feature and self.feature.isVisible():
            return self.feature.symbol()
        
        elif self.objects:
            return self.objects[0].symbol()
        
        else:
            return self.baseSymbol
        
    def color(self):
        # Determine which color to use to draw this tile
        if self.creature and self.creature.isVisible():
            return self.creature.color()
        
        elif self.feature and self.feature.isVisible():
            return self.feature.color()
        
        elif self.objects:
            return self.objects[0].color()
        
        else:
            return self.baseColor        

    def background(self):
        # Determine which background to use to draw this tile
        if self.creature and self.creature.isVisible():
            return self.creature.background()
        
        elif self.feature and self.feature.isVisible():
            return self.feature.background()
                
        else:
            return self.baseBackground   

    def description(self):
        # Determine which description to use to draw this tile
        if self.creature and self.creature.isVisible():
            return self.creature.description
        
        elif self.feature and self.feature.isVisible():
            return self.feature.description
        
        elif self.objects:
            return self.objects[0].description
        
        else:
            return self.baseDescription   
        
    def coords(self):
        return self.coordinates
    
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
    tile = Tile(baseSymbol = 'x', baseDescription = 'some junk')  
    print tile.color(), tile.symbol(), tile.description()
            
if __name__ == '__main__':
    main()













