'''
Created on Jan 28, 2014

@author: dstuart
'''

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Integer
from sqlalchemy.orm import relationship, backref

import database as db
import LevelClass as L
import Const as C


Base = db.saveDB.getDeclarativeBase()

class Area(Base):
    
    __tablename__ = "areas"
    __table_args__ = {'extend_existing': True}

    def __init__(self, **kwargs):
        self.name = kwargs.get('name', "")
        self.withTown = kwargs.get("withTown", False)
        
        self.levels = []
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    levels = relationship("Level", backref=backref("area", uselist=False), 
                          primaryjoin="Area.id==Level.areaId")
    
    startingLevel = relationship("Level", uselist = False, primaryjoin="Area.id==Level.startingLevelOfId")
    startingLevelId = Column(Integer, ForeignKey("levels.id", use_alter = True, name="starting_level_fk"))
    
    mapTile = relationship("MapTile", uselist=False, backref=backref("connectedArea", uselist=False), 
                          primaryjoin="MapTile.connectedAreaId==Area.id")
    mapTileId = Column(Integer, ForeignKey("map_tiles.id", use_alter = True, name="map_tile_fk"))
    
    areaType = Column(String)
    
    __mapper_args__ = {'polymorphic_on': areaType,
                       'polymorphic_identity': 'area'}
    
    def getLevels(self):
        return self.levels
    
    def generateLevels(self, numLevels = 1):
        raise NotImplementedError("generateLevels() not implemented, use a subclass")
    
    def getStartingLevel(self):
        if not self.startingLevel:
            self.generateLevels()
        return self.startingLevel
    
    def getMapTile(self):
        return self.mapTile
    
    def getTerrainType(self):
        return self.getMapTile().getTerrainType()
        
    
    
    
