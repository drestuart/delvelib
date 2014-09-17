'''
Created on Feb 25, 2014

@author: dstuart
'''

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Integer
from sqlalchemy.orm import relationship, backref

import LevelClass as L
from TileClass import TileBase
from colors import blankBackground
import database as db

Base = db.saveDB.getDeclarativeBase()

class MapTile(TileBase):
    
    __tablename__ = "map_tiles"
    __table_args__ = {'extend_existing': True}
    
    backgroundColor = blankBackground
    
    description = "tile"
    
    def __init__(self, x, y, **kwargs):
        super(MapTile, self).__init__(x, y, **kwargs)
        
        self.worldMap = kwargs.get('worldMap')
        self.levels = []
        self.startingLevelIndex = kwargs.get('startingLevelIndex', 0)
        
    id = Column(Integer, ForeignKey('tiles.id'), primary_key=True)
    name = Column(String)
    startingLevelIndex = Column(Integer)
    
    levels = relationship("Level", backref=backref("maptile", uselist=False), 
                          primaryjoin="MapTile.id==Level.mapTileId")
    
    regionId = Column(Integer, ForeignKey("regions.id"))
    worldMapId = Column(Integer, ForeignKey("levels.id", use_alter = True, name="world_map_fk"))
    name = Column(String)
    
    waterTile = False
    terrainType = L.WildernessLevel
    
    tileType = Column(String)
    
    __mapper_args__ = {'polymorphic_identity': 'maptile'}
    
    def remove(self):
        self.worldMap = None
        self.worldMapId = None
        del self
        self = None
    
    def blocksMove(self):
        return self.isWaterTile()
    
    def bump(self, bumper):
        return False
    
    def blocksSight(self):
        return False
    
    def isWaterTile(self):
        return self.waterTile
    
    def getLevel(self):  
        return self.worldMap
    
    def getRegion(self):
        return self.region
    
    def setRegion(self, reg):
        self.region = reg
    
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
        print "Deprecated getConnectedLevel()"
        return self.getStartingLevel()
    
    def generateConnectedLevel(self):
        raise NotImplementedError("Deprecated generateConnectedLevel()")
        
    def getLevels(self):
        return self.levels
    
    def generateLevels(self, numLevels = 1):
        raise NotImplementedError("generateLevels() not implemented, use a subclass")
    
    def getStartingLevel(self):
        if not self.levels:
            self.generateLevels()
        return self.levels[self.startingLevelIndex]
        
    def getDescription(self):
        return self.description
    
    def getTerrainType(self):
        return self.terrainType
