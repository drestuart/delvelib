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
from AreaClass import Area

Base = db.saveDB.getDeclarativeBase()

class MapTile(TileBase):
    
    __tablename__ = "map_tiles"
    __table_args__ = {'extend_existing': True}
    
    backgroundColor = blankBackground
    
    description = "tile"
    
    def __init__(self, x, y, **kwargs):
        super(MapTile, self).__init__(x, y, **kwargs)
        
        self.connectedArea = self.areaType()
        self.worldMap = kwargs.get('worldMap')
        
    id = Column(Integer, ForeignKey('tiles.id'), primary_key=True)
    
    connectedAreaId = Column(Integer, ForeignKey("areas.id"))
    
    regionId = Column(Integer, ForeignKey("regions.id"))
    worldMapId = Column(Integer, ForeignKey("levels.id", use_alter = True, name="world_map_fk"))
    name = Column(String)
    
    waterTile = False
    terrainType = L.WildernessLevel
    areaType = Area
    
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
        return self.getConnectedArea().getStartingLevel()
    
    def generateConnectedLevel(self):
        raise NotImplementedError("Deprecated generateConnectedLevel()")
        
    def getConnectedArea(self):
        return self.connectedArea
    
    def getStartingLevel(self):
        return self.getConnectedArea().getStartingLevel()
        
    def getDescription(self):
        return self.description
    
    def getTerrainType(self):
        return self.terrainType
