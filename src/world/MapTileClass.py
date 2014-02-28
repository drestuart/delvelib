'''
Created on Feb 25, 2014

@author: dstuart
'''

from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Integer, Boolean

from TileClass import TileBase
import database as db
from colors import *
from symbols import *
import Const as C

Base = db.saveDB.getDeclarativeBase()

class MapTile(TileBase):
    
    __tablename__ = "tiles"
    __table_args__ = {'extend_existing': True}
    
    def __init__(self, x, y, **kwargs):
        super(MapTile, self).__init__(x, y, backgroundColor = blankBackground, **kwargs)
        
        self.connectedLevel = kwargs.get('connectedLevel', None)
        self.worldMap = kwargs.get('worldMap')

    connectedLevelId = Column(Integer, ForeignKey("levels.id"))
    regionId = Column(Integer, ForeignKey("regions.id"))
    worldMapId = Column(Integer, ForeignKey("world_map.id"))
    
    isWaterTile = False
    
    def blocksMove(self):
        return False
    
    def blocksSight(self):
        return False
    
    def isWaterTile(self):
        return self.isWaterTile
    
    def getLevel(self):  
        return self.worldMap
    
    def getRegion(self):
        return self.region
    
    def getColor(self):
        # Determine which color to use to draw this tile
        
        if self.creature and self.creature.isVisible():
            return self.creature.getColor()

        else:
            return super(MapTile, self).getColor()
    
    def getSymbol(self):
        # Determine which symbol to use to draw this tile
        
        if self.creature and self.creature.isVisible():
            toReturn = self.creature.getSymbol()
            
        else:
            toReturn = self.baseSymbol
        
#        self.setLastSeenSymbol(toReturn)
        return toReturn

class Forest(MapTile):
#     symb = unichr(120533)
    symb = lowerTau
    def __init__(self, *args, **kwargs):
        super(Forest, self).__init__(*args, baseSymbol = self.symb, color = colorForest, **kwargs)

class Plain(MapTile):
    def __init__(self, *args, **kwargs):
        super(Plain, self).__init__(*args, baseSymbol = '.', color = colorPlain, **kwargs)
        
class Field(MapTile):
    def __init__(self, *args, **kwargs):
        super(Field, self).__init__(*args, baseSymbol = '.', color = colorField, **kwargs)

class Mountain(MapTile):
    def __init__(self, *args, **kwargs):
        super(Mountain, self).__init__(*args, baseSymbol = '^', color = colorMountain, **kwargs)

class Ocean(MapTile):
    isWaterTile = True
    def __init__(self, *args, **kwargs):
        super(Ocean, self).__init__(*args, baseSymbol = '~', color = colorOcean, **kwargs)

class River(MapTile):
    isWaterTile = True
    def __init__(self, *args, **kwargs):
        super(Ocean, self).__init__(*args, baseSymbol = '~', color = colorRiver, **kwargs)

class Bridge(MapTile):
    def __init__(self, *args, **kwargs):
        super(Bridge, self).__init__(*args, baseSymbol = '=', color = colorWood, **kwargs)

class Town(MapTile):
    def __init__(self, *args, **kwargs):
        super(Town, self).__init__(*args, baseSymbol = '*', color = colorWood, **kwargs)




