'''
Created on Feb 26, 2014

@author: dstuart
'''

from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Integer

import LevelClass as L

import database as db

Base = db.saveDB.getDeclarativeBase()

class Region(Base):
    __tablename__ = "regions"
    __table_args__ = {'extend_existing': True}
    
    def __init__(self, **kwargs):
        self.mapTiles = []

    id = Column(Integer, primary_key=True)

    mapTiles = relationship("MapTile", backref=backref("region", uselist=False), primaryjoin="Region.id==MapTile.regionId")
    worldMapId = Column(Integer, ForeignKey("world_map.id"))



class WorldMap(L.MapBase):
    __tablename__ = "world_map"
    __table_args__ = {'extend_existing': True}
    __mapper_args__ = {
                    'polymorphic_identity':'world_map',
                    'concrete':True}

    def __init__(self, **kwargs):
        super(WorldMap, self).__init__(**kwargs)
        
        self.mapTiles = []
        self.regions = []
    
    id = Column(Integer, primary_key=True)
    mapTiles = relationship("MapTile", backref=backref("worldMap", uselist=False), primaryjoin="WorldMap.id==MapTile.worldMapId")
    regions = relationship("Region", backref=backref("worldMap", uselist=False), primaryjoin="WorldMap.id==Region.worldMapId")
    
    def buildMap(self):
        ''' Oh here we go. '''
        
        pass
        
