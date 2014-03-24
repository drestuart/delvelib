'''
Created on Feb 26, 2014

@author: dstuart
'''

from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Integer

import LevelClass as L
from MapTileClass import Forest, Field, Plain, Mountain, Town
import Util as U
from VoronoiMap import VMap
import database as db
import random
import Const as C

Base = db.saveDB.getDeclarativeBase()

class Region(Base):
    __tablename__ = "regions"
    __table_args__ = {'extend_existing': True}
    
    def __init__(self, **kwargs):
        self.mapTiles = []
        
        self.tileType = random.choice([Forest, Field, Plain, Mountain])

    id = Column(Integer, primary_key=True)

    worldMapId = Column(Integer, ForeignKey("levels.id"))
    name = Column(String)
    
    def addTile(self, tile):
        self.mapTiles.append(tile)
        
    def replaceTile(self, newtile):
        for tile in self.mapTiles:
            if tile.getXY() == newtile.getXY():
                self.mapTiles.remove(tile)

        self.addTile(newtile)

    def getTileType(self):
        # More logic goes here
        return self.tileType


class WorldMap(L.MapBase):

    def __init__(self, **kwargs):
        super(WorldMap, self).__init__(**kwargs)
        
        self.mapTiles = []
        self.regions = []
        self.num_regions = kwargs['num_regions']
        
        self.load()
    
    __mapper_args__ = {'polymorphic_identity':'world_map',
#                        'concrete':True,
                       'with_polymorphic':'*'}
    
    def addTile(self, tile):
        self.mapTiles.append(tile)
        self.hasTile[tile.getX()][tile.getY()] = True
        
    def replaceTile(self, newtile):
        if self.hasTile[newtile.getX()][newtile.getY()]:
            for tile in self.mapTiles:
                if tile.getXY() == newtile.getXY():
                    self.mapTiles.remove(tile)

        self.addTile(newtile)
    
    def load(self):
        self.creatures = []

        # Initialize self.hasTile
        self.hasTile = []
        
        for dummyx in range(self.width):
            newCol = []
            for dummyy in range(self.height):
                newCol.append(False)
            self.hasTile.append(newCol)
            

    def buildTileArray(self):
        self.tileArray = []
        
        # Initialize
        for dummyx in range(self.width):
            newCol = []
            for dummyy in range(self.height):
                newCol.append(None)
            self.tileArray.append(newCol)
            
        # Fill in
        for tile in self.mapTiles:
            self.tileArray[tile.x][tile.y] = tile
            
    def getTile(self, x, y):
        if not self.__dict__.get('tileArray'):
#             print "self.tileArray not initialized!"
            self.buildTileArray()
        
        if x >= 0 and x < self.width and y >= 0 and y < self.height:
            return self.tileArray[x][y]
    
        return None
    
    def distance(self, tilea, tileb):
        return U.ChebyshevDistance(tilea.getX(), tileb.getX(), tilea.getY(), tileb.getY())
    
    def getTilesToDraw(self, dummyx, dummyy, cameradims, visibility = True):
        retArray = []
        
        camx, camy, camwidth, camheight = cameradims
        
        for tile in self.mapTiles:
            if tile:
                x = tile.x
                y = tile.y
                
                # Is the tile in the camera's range?
                if (x < camx or x >= camx + camwidth or y < camy or y >= camy + camheight):
                    continue
                
                symbol = tile.getSymbol()
                color = tile.getColor()
                background = tile.getBackgroundColor()
                    
                # Good lord, what made me think this was a good idea?
                # symbol = symbol.encode('ascii', 'ignore')
                retArray.append((x, y, symbol, color, background))
                
        return retArray

    def getAdjacentTiles(self, fromTile):
#         return self.getTilesAtRadius(1, fromTile.getX(), fromTile.getY())
        tiles = []
        x, y = fromTile.getXY()
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                if not (i == 0 and j == 0):
                    tile = self.getTile(x + i, y + j)
                    if tile: tiles.append(tile)
        return tiles
    
    def handleRemovedCreature(self, tile, creature):
        pass
    
    def handleAddedCreature(self, tile, creature):
        pass
    
    def placeCreature(self, creature, tile):
        success = tile.placeCreature(creature)
        if success and not creature in self.creatures:
            self.creatures.append(creature)
        return success
    
    def placePlayer(self, player):
        tile = self.getTile(1, 1)
        self.placeCreature(player, tile)
        
    def buildMap(self):
        raise NotImplementedError("buildMap() not implemented, use a subclass")







        
