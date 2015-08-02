'''
Created on Jan 28, 2014

@author: dstuart
'''

from enum import Enum, unique
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Unicode, Integer
import threading
import database as db

Base = db.saveDB.getDeclarativeBase()

@unique
class DungeonStatus(Enum):
    none = 1
    closed = 2
    open = 3
    
# TODO: Convert to Enum
NOT_BUILT = "not_built"
BUILDING = "building"
BUILT = "built"

class Area(Base):
    
    __tablename__ = "areas"
    __table_args__ = {'extend_existing': True}
    hasDungeon = False

    def __init__(self, **kwargs):
        self.name = kwargs.get('name', u"")
        
        self.levels = []
        
        self.startingLevelStatus = NOT_BUILT
        self.lowerLevelStatus = NOT_BUILT
        
        self.thread = None
    
    id = Column(Integer, primary_key=True)
    name = Column(Unicode)
    
    levels = relationship("Level", backref=backref("area", uselist=False), 
                          primaryjoin="Area.id==Level.areaId")
    
    startingLevel = relationship("Level", uselist = False, primaryjoin="Area.id==Level.startingLevelOfId")
    startingLevelId = Column(Integer, ForeignKey("levels.id", use_alter = True, name="starting_level_fk"))
    startingLevelStatus = Column(Unicode)
    lowerLevelStatus = Column(Unicode)
    
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
    
    def getStartingLevel(self): # TODO: Threading flag here?
        if not self.startingLevel:
            self.buildStartingLevel() # TODO: Threading flag here?
        return self.startingLevel
    
    def getMapTile(self):
        return self.mapTile
    
    def setMapTile(self, mt):
        self.mapTile = mt
    
    def getTerrainType(self):
        return self.getMapTile().getTerrainType()
    
    def getThread(self):
        return self.thread
    
    def setThread(self, t):
        self.thread = t
        
    def clearThread(self):
        self.setThread(None)
    
    def dungeonStatus(self):
        if not self.hasDungeon:
            return DungeonStatus.none
        elif len(self.levels) > 1:  # We've added some levels other than the first
            return DungeonStatus.open
        else:
            return DungeonStatus.closed
        
class StartingLevelBuildingThread(threading.Thread):
    def __init__(self, area, items=[]):
        threading.Thread.__init__(self)
        self.area = area
        self.area.setThread(self)
        self.items = items
    def run(self):
        self.area.startingLevelStatus = BUILDING
        self.area.buildStartingLevel()
        for item in self.items:
            self.area.getStartingLevel().placeItemAtRandom(item)
        
        self.area.startingLevelStatus = BUILT
        self.area.clearThread()

class LowerLevelsBuildingThread(threading.Thread):
    def __init__(self, area, items=[]):
        threading.Thread.__init__(self)
        self.area = area
        self.area.setThread(self)
        self.items = items
    def run(self):
        self.area.lowerLevelStatus = BUILDING
        self.area.buildLowerLevels()
        for item in self.items:
            # TODO: Put all the items in the bottom level, or do we need a way to specify where they go?
            self.area.getLevels()[-1].placeItemAtRandom(item)
        
        self.area.lowerLevelStatus = BUILT
        self.area.clearThread()

class SingleLevelArea(Area):
    __mapper_args__ = {'polymorphic_identity': u'single_level_area'}
    defaultWidth = 100
    defaultHeight = 80
    
    def buildStartingLevel(self):
        terrainType = self.getTerrainType()
        newLevel = terrainType(area = self, depth = 0, width = self.defaultWidth, height = self.defaultHeight)
        self.startingLevel = newLevel
        newLevel.buildLevel()
        db.saveDB.save(self)

    def convertToMultilevelArea(self):
        newArea = MultiLevelArea(name=self.name)
        mt = self.getMapTile()
        
        self.levels[0].placeDungeonEntrance()
        newArea.levels = self.levels
        self.levels = []
        
        mt.setConnectedArea(newArea)
        del self
        db.saveDB.save(newArea)
        
        return newArea
    
class MultiLevelArea(Area):
    __mapper_args__ = {'polymorphic_identity': u'multi_level_area'}
    defaultWidth = 100
    defaultHeight = 80
    hasDungeon = True
    
    def buildStartingLevel(self):
        newDepth = 0
        
        terrainType = self.getTerrainType()
        newLevel = terrainType(area = self, depth = newDepth, width = self.defaultWidth, height = self.defaultHeight)
        self.startingLevel = newLevel
        
        newLevel.buildLevel()
        newLevel.placeDungeonEntrance()
    
    
