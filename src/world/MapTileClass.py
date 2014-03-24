'''
Created on Feb 25, 2014

@author: dstuart
'''

from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import String

import LevelClass as L
from TileClass import TileBase
from colors import *
import database as db
import symbols
import random

Base = db.saveDB.getDeclarativeBase()

class MapTile(TileBase):
    
    __tablename__ = "tiles"
    __table_args__ = {'extend_existing': True}
    
    connectedLevelWidth = 60
    connectedLevelHeight = 40
    
    def __init__(self, x, y, **kwargs):
        super(MapTile, self).__init__(x, y, backgroundColor = blankBackground, **kwargs)
        
        self.connectedLevel = kwargs.get('connectedLevel', None)
        self.worldMap = kwargs.get('worldMap')
        
    connectedLevelId = Column(Integer, ForeignKey("levels.id"))
    regionId = Column(Integer, ForeignKey("regions.id"))
    worldMapId = Column(Integer, ForeignKey("levels.id"))
    
    isWaterTile = False
    connectedLevelType = L.WildernessLevel
    
    tileType = Column(String)
    
    __mapper_args__ = {'polymorphic_on': tileType,
                       'polymorphic_identity': 'maptile'}
    
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
    
    def getConnectedLevel(self):
        if not self.connectedLevel:
            self.generateConnectedLevel()
        return self.connectedLevel
    
    def generateConnectedLevel(self):
        self.connectedLevel = self.connectedLevelType(width = self.connectedLevelWidth, height = self.connectedLevelHeight)
        self.connectedLevel.buildLevel()
        
        

class Forest(MapTile):
    symb = symbols.lowerTau
    connectedLevelType = L.ForestLevel
    __mapper_args__ = {'polymorphic_identity': 'forest'}
    def __init__(self, *args, **kwargs):
        super(Forest, self).__init__(*args, baseSymbol = self.symb, color = colorForest, **kwargs)

class Plain(MapTile):
    __mapper_args__ = {'polymorphic_identity': 'plain'}
    def __init__(self, *args, **kwargs):
        super(Plain, self).__init__(*args, baseSymbol = '.', color = colorPlain, **kwargs)
        
class Field(MapTile):
    __mapper_args__ = {'polymorphic_identity': 'field'}
    def __init__(self, *args, **kwargs):
        super(Field, self).__init__(*args, baseSymbol = '.', color = colorField, **kwargs)

class Mountain(MapTile):
    __mapper_args__ = {'polymorphic_identity': 'mountain'}
    def __init__(self, *args, **kwargs):
        super(Mountain, self).__init__(*args, baseSymbol = '^', color = colorMountain, **kwargs)

class Ocean(MapTile):
    __mapper_args__ = {'polymorphic_identity': 'ocean'}
    isWaterTile = True
    def __init__(self, *args, **kwargs):
        super(Ocean, self).__init__(*args, baseSymbol = symbols.doubleWavy, color = colorOcean, **kwargs)

class River(MapTile):
    __mapper_args__ = {'polymorphic_identity': 'river'}
    isWaterTile = True
    def __init__(self, *args, **kwargs):
        super(Ocean, self).__init__(*args, baseSymbol = '~', color = colorRiver, **kwargs)

class Bridge(MapTile):
    __mapper_args__ = {'polymorphic_identity': 'bridge'}
    def __init__(self, *args, **kwargs):
        super(Bridge, self).__init__(*args, baseSymbol = '=', color = colorWood, **kwargs)

class Town(MapTile):
    symb = symbols.townShape
    connectedLevelType = L.TownLevel
    
    __mapper_args__ = {'polymorphic_identity': 'town'}
    
    def __init__(self, *args, **kwargs):
        super(Town, self).__init__(*args, baseSymbol = self.symb, color = colorWood, **kwargs)
        
    def generateConnectedLevel(self):
        self.connectedLevel = self.connectedLevelType(cellsWide = random.randint(2, 4), cellsHigh = random.randint(2, 4))
        self.connectedLevel.buildLevel()


