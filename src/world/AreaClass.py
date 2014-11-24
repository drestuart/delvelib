'''
Created on Jan 28, 2014

@author: dstuart
'''

from enum import Enum, unique
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Unicode, Integer

import database as db

Base = db.saveDB.getDeclarativeBase()

class Area(Base):
    
    __tablename__ = "areas"
    __table_args__ = {'extend_existing': True}
    hasDungeon = False

    def __init__(self, **kwargs):
        self.name = kwargs.get('name', "")
        
        self.levels = []
    
    id = Column(Integer, primary_key=True)
    name = Column(Unicode)
    
    levels = relationship("Level", backref=backref("area", uselist=False), 
                          primaryjoin="Area.id==Level.areaId")
    
    startingLevel = relationship("Level", uselist = False, primaryjoin="Area.id==Level.startingLevelOfId")
    startingLevelId = Column(Integer, ForeignKey("levels.id", use_alter = True, name="starting_level_fk"))
    
    mapTile = relationship("MapTile", uselist=False, backref=backref("connectedArea", uselist=False), 
                          primaryjoin="MapTile.connectedAreaId==Area.id")
    mapTileId = Column(Integer, ForeignKey("map_tiles.id", use_alter = True, name="map_tile_fk"))
    
    areaType = Column(Unicode)
    
    __mapper_args__ = {'polymorphic_on': areaType,
                       'polymorphic_identity': u'area'}
    
    def getLevels(self):
        return self.levels
    
    def buildStartingLevel(self):
        raise NotImplementedError("buildStartingLevel() not implemented, use a subclass")
    
    def buildLowerLevels(self, numLevels):
        raise NotImplementedError("buildLowerLevels() not implemented, use a subclass")
    
    def getStartingLevel(self):
        if not self.startingLevel:
            self.buildStartingLevel()
        return self.startingLevel
    
    def getMapTile(self):
        return self.mapTile
    
    def setMapTile(self, mt):
        self.mapTile = mt
    
    def getTerrainType(self):
        return self.getMapTile().getTerrainType()
    
    def dungeonStatus(self):
        if not self.hasDungeon:
            return DungeonStatus.none
        elif len(self.levels) > 1:  # We've added some levels other than the first
            return DungeonStatus.open
        else:
            return DungeonStatus.closed
    
@unique
class DungeonStatus(Enum):
    none = 1
    closed = 2
    open = 3
    
    
