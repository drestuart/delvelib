'''
Created on Feb 25, 2014

@author: dstuart
'''

from symbols import dungeonSymbol
from AreaClass import DungeonStatus

import LevelClass as L
from TileClass import TileBase
from colors import blankBackground, colorClosedDungeon, colorOpenDungeon
from AreaClass import SingleLevelArea, MultiLevelArea

class MapTile(TileBase):
    
    backgroundColor = blankBackground
    description = "tile"
    name = '' # TODO: Get name from region?
    
    def __init__(self, x, y, **kwargs):
        super(MapTile, self).__init__(x, y, **kwargs)
        
        self.worldMap = kwargs.get('worldMap')
        self.generateArea()
        self.region = None
        self.area = None

    waterTile = False
    terrainType = L.WildernessLevel
    areaType = SingleLevelArea
    
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
    
    def setLevel(self, level):
        self.worldMap = level
        if self not in self.worldMap.getMapTiles():
            self.level.addTile(self)
    
    def getRegion(self):
        return self.region
    
    def setRegion(self, reg):
        self.region = reg
    
    def getColor(self):
        # Determine which color to use to draw this tile
        
        if self.creature and self.creature.isVisible():
            return self.creature.getColor()
        
        elif self.hasDungeon():
            if self.hasOpenDungeon():
                return colorOpenDungeon
            else:
                return colorClosedDungeon

        else:
            return super(MapTile, self).getColor()
    
    def getSymbol(self):
        # Determine which symbol to use to draw this tile
        if self.creature and self.creature.isVisible():
            toReturn = self.creature.getSymbol()
            
        elif self.hasDungeon():
            toReturn = dungeonSymbol
            
        else:
            toReturn = self.baseSymbol
        
        return toReturn
    
    def generateConnectedLevel(self):
        raise NotImplementedError("Deprecated generateConnectedLevel()")
        
    def getConnectedArea(self):
        if not self.connectedArea:
            self.generateArea()
        return self.connectedArea
    
    def setConnectedArea(self, area):
        self.connectedArea = area
        if self is not area.getMapTile():
            area.setMapTile(self)
    
    def getStartingLevel(self): # TODO: Threading flag here?
        return self.getConnectedArea().getStartingLevel()
        
    def getDescription(self):
        return self.description
    
    def getTerrainType(self):
        return self.terrainType
    
    def generateArea(self):
        self.setConnectedArea(self.areaType())
    
    def hasDungeon(self):
        return self.getConnectedArea().dungeonStatus() is not DungeonStatus.none
    
    def hasOpenDungeon(self):
        return self.getConnectedArea().dungeonStatus() is DungeonStatus.open
    
    def addDungeon(self, areaType = MultiLevelArea):
        if self.areaType is areaType:
            return
        
        self.areaType = areaType
        
        if self.getConnectedArea() and self.getConnectedArea().startingLevel:
            self.getConnectedArea().convertToMultilevelArea()
        else:
            newArea = areaType(name = self.name)
            self.setConnectedArea(newArea)
            newArea.setMapTile(self)
            
#         database.saveDB.save(self)
        
