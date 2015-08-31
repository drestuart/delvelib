'''
Created on Jan 28, 2014

@author: dstuart
'''

from enum import Enum, unique
import threading

@unique
class DungeonStatus(Enum):
    none = 1
    closed = 2
    open = 3

@unique
class BuildStatus(Enum):
    NOT_BUILT = 1
    BUILDING = 2
    BUILT = 3
    
class Area(object):
    
    __tablename__ = "areas"
    __table_args__ = {'extend_existing': True}
    hasDungeon = False

    def __init__(self, **kwargs):
        self.name = kwargs.get('name', u"")
        
        self.levels = []
        self.startingLevel = None
        self.startingLevelStatus = BuildStatus.NOT_BUILT
        self.lowerLevelStatus = BuildStatus.NOT_BUILT
        
        self.thread = None
        
        self.mapTile = None
    
    def getLevels(self):
        return self.levels

    def addLevel(self, lvl):
        self.levels.append(lvl)
        if self is not lvl.getArea():
            lvl.setArea(self)

    def buildStartingLevel(self):
        raise NotImplementedError("buildStartingLevel() not implemented, use a subclass")
    
    def buildLowerLevels(self, numLevels):
        raise NotImplementedError("buildLowerLevels() not implemented, use a subclass")
    
    def getStartingLevel(self): # TODO: Threading flag here?
        if not self.startingLevel:
            self.buildStartingLevel() # TODO: Threading flag here?
        return self.startingLevel

    def setStartingLevel(self, lvl):
        self.startingLevel = lvl
    
    def getMapTile(self):
        return self.mapTile
    
    def setMapTile(self, mt):
        self.mapTile = mt
        if self is not mt.getConnectedArea():
            mt.setConnectedArea(self)
    
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
    def __init__(self, area, items=[], creatures = []):
        threading.Thread.__init__(self)
        self.area = area
        self.area.setThread(self)
        self.items = items
        self.creatures = creatures
    def run(self):
        if self.area.startingLevelStatus != BuildStatus.NOT_BUILT:
            self.area.clearThread()
            raise BuildingThreadError("Area starting level building already started", self.area)

        print "Level building thread started!"
        self.area.startingLevelStatus = BuildStatus.BUILDING
        self.area.buildStartingLevel()

        for item in self.items:
            self.area.getStartingLevel().placeItemAtRandom(item)

        for creature in self.creatures:
            self.area.getStartingLevel().placeCreatureAtRandom(creature)

        self.area.startingLevelStatus = BuildStatus.BUILT
        self.area.clearThread()
        print "Level building thread finished!"

class LowerLevelsBuildingThread(threading.Thread):
    def __init__(self, area, items=[], creatures = []):
        threading.Thread.__init__(self)
        self.area = area
        self.area.setThread(self)
        self.items = items
        self.creatures = creatures
    def run(self):
        if self.area.startingLevelStatus != BuildStatus.NOT_BUILT:
            self.area.clearThread()
            raise BuildingThreadError("Area lower level building already started", self.area)

        self.area.lowerLevelStatus = BuildStatus.BUILDING
        self.area.buildLowerLevels()
        for item in self.items:
            # TODO: Put all the items in the bottom level, or do we need a way to specify where they go?
            self.area.getLevels()[-1].placeItemAtRandom(item)
        
        for creature in self.creatures:
            self.area.getLevels()[-1].placeCreatureAtRandom(creature)
        
        self.area.lowerLevelStatus = BuildStatus.BUILT
        self.area.clearThread()
        
class BuildingThreadError(Exception):
    def __init__(self, message, area):
        self.message = message
        self.area = area
    def __str__(self):
        return repr(self.message) + " " + repr(self.area)

class SingleLevelArea(Area):
    defaultWidth = 100
    defaultHeight = 80
    
    def buildStartingLevel(self):
        terrainType = self.getTerrainType()
        newLevel = terrainType(area = self, depth = 0, width = self.defaultWidth, height = self.defaultHeight)
        self.startingLevel = newLevel
        newLevel.buildLevel()
#         db.saveDB.save(self)

    def convertToMultilevelArea(self):
        newArea = MultiLevelArea(name=self.name)
        mt = self.getMapTile()
        
        self.levels[0].placeDungeonEntrance()
        newArea.levels = self.levels
        self.levels = []
        
        mt.setConnectedArea(newArea)
        del self
        
        return newArea
    
class MultiLevelArea(Area):
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
    
    
