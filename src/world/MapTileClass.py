'''
Created on Feb 25, 2014

@author: dstuart
'''

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Integer

from TileClass import TileBase
from colors import blankBackground
import delvelib.src.database.database as db

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
    name = Column(String)
    
    waterTile = False
    
    tileType = Column(String)
    
    __mapper_args__ = {'polymorphic_on': tileType,
                       'polymorphic_identity': 'maptile'}
    
    def blocksMove(self):
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
        if not self.connectedLevel:
            self.generateConnectedLevel()
        return self.connectedLevel
    
    def generateConnectedLevel(self):
        self.connectedLevel = self.connectedLevelType(width = self.connectedLevelWidth, height = self.connectedLevelHeight)
        self.connectedLevel.buildLevel()
        
        
