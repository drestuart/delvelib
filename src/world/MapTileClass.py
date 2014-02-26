'''
Created on Feb 25, 2014

@author: dstuart
'''

from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Integer, Boolean

from TileClass import TileBase
import database as db
# import WorldMapClass

Base = db.saveDB.getDeclarativeBase()

class MapTile(TileBase):
    
    __tablename__ = "tiles"
    __table_args__ = {'extend_existing': True}
    
    def __init__(self, x, y, **kwargs):
        super(MapTile, self).__init__(**kwargs)
        
        self.x = x
        self.y = y
        
        self.blockMove = kwargs.get('blockMove', False)
        self.connectedLevel = kwargs.get('connectedLevel', None)
        self.worldMap = kwargs.get('worldMap')

    connectedLevelId = Column(Integer, ForeignKey("levels.id"))
    regionId = Column(Integer, ForeignKey("regions.id"))
    worldMapId = Column(Integer, ForeignKey("world_map.id"))
    
    isWaterTile = False
    
    def isWaterTile(self):
        return self.isWaterTile


class Forest(MapTile):
    pass

class Plain(MapTile):
    pass

class Mountain(MapTile):
    pass

class Ocean(MapTile):
    isWaterTile = True

class River(MapTile):
    isWaterTile = True
    
class Bridge(MapTile):
    pass

class Town(MapTile):
    pass



