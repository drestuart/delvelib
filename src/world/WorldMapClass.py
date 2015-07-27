'''
Created on Feb 26, 2014

@author: dstuart
'''

from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Unicode, Integer

import LevelClass as L
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
        

    id = Column(Integer, primary_key=True)

#     worldMapId = Column(Integer, ForeignKey("world_map.id"))
    worldMapId = Column(Integer, ForeignKey("levels.id"))
    name = Column(Unicode)
    mapTiles = relationship("MapTile", backref=backref("region", uselist=False), primaryjoin="Region.id==MapTile.regionId")
    regionType = Column(Unicode)
    
    __mapper_args__ = {'polymorphic_on': regionType,
                       'polymorphic_identity': u'region'}
    
    def addTile(self, tile):
        self.mapTiles.append(tile)
        tile.setRegion(self)
        
    def replaceTile(self, oldtile, newtile):
        assert oldtile.getXY() == newtile.getXY()
        self.mapTiles.remove(oldtile)
        self.addTile(newtile)

    def getTileType(self):
        return self.tileType


class WorldMap(L.MapBase):
    
#     __tablename__ = 'world_map'
#     __table_args__ = {'extend_existing': True}

    def __init__(self, **kwargs):
        super(WorldMap, self).__init__(**kwargs)
        
#         self.id = 1
        
        self.mapTiles = []
        self.regions = []
        self.num_regions = kwargs['num_regions']
        
        self.load()
    
#     id = Column(Integer, ForeignKey('levels.id'), primary_key=True, autoincrement=True)
#     name = Column(Unicode)
#     width = Column(Integer)
#     height = Column(Integer)
#     levelType = Column(Unicode)
    
    __mapper_args__ = {#'polymorphic_on': levelType,
                      'polymorphic_identity':u'world_map',
#                       'concrete':True,
                      'with_polymorphic':'*'}
    
    def addTile(self, tile):
        self.mapTiles.append(tile)
        self.hasTile[tile.getX()][tile.getY()] = True
        
    def replaceTile(self, newtile):
        oldtile = self.getTile(newtile.getX(), newtile.getY())
        assert oldtile.getXY() == newtile.getXY()

        reg = oldtile.getRegion()
        if reg:
            reg.replaceTile(oldtile, newtile)
        
        oldnumtiles = len(self.mapTiles)
        self.mapTiles.remove(oldtile)
        oldtile.remove()
        
        self.addTile(newtile)
        self.tileArray[newtile.getX()][newtile.getY()] = newtile
        
        newnumtiles = len(self.mapTiles)
        assert newnumtiles == oldnumtiles
    
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
            assert tile is not None
            self.tileArray[tile.x][tile.y] = tile
            
    def getTile(self, x, y):
        if not self.__dict__.get('tileArray'):
#             print "self.tileArray not initialized!"
            self.buildTileArray()
        
        if x >= 0 and x < self.width and y >= 0 and y < self.height:
            return self.tileArray[x][y]
        
        return None
    
    def distance(self, tilea, tileb):
        return self.coordinateDistance(tilea.getX(), tileb.getX(), tilea.getY(), tileb.getY())
    
    def coordinateDistance(self, xa, xb, ya, yb):
        return U.ChebyshevDistance(xa, xb, ya, yb)

    
    def getTilesInRadius(self, radius, centerX, centerY, tileClass=None):
        assert radius >= 0 and radius == int(radius)
        
        tiles = []
        for rad in range(0, radius + 1):
            tiles += self.getTilesAtRadius(rad, centerX, centerY, tileClass)
        
        return tiles
    
    def getTilesInRange(self, rmin, rmax, centerX, centerY, tileClass=None):
        assert rmin <= rmax and rmin > 0
        
        tiles = []
        for rad in range(rmin, rmax + 1):
            tiles += self.getTilesAtRadius(rad, centerX, centerY, tileClass)
        
        return tiles
    
    def getNearestTile(self, fromTile, tileClass):
        centerX, centerY = fromTile.getXY()
        radius = 1
        
        while True:
            matches = self.getTilesAtRadius(radius, centerX, centerY, tileClass)
            if not matches:
                radius += 1
                continue

            return random.choice(matches)
    
    def getTilesAtRadius(self, radius, centerX, centerY, tileClass=None):
        assert radius >= 0 and radius == int(radius)
        
        centerTile = self.getTile(centerX, centerY)
        tiles = []
        
        if radius == 0:
            return [centerTile]
        
        x1 = max(0, centerX - radius)
        y1 = max(0, centerY - radius)
        
        x2 = min(centerX + radius, self.width)
        y2 = min(centerY + radius, self.height)
        
        for x in range(x1, x2 + 1):
            tile1 = self.getTile(x, y1)
            tile2 = self.getTile(x, y2)
            if tile1 and (tileClass is None or isinstance(tile1, tileClass)): tiles.append(tile1)
            if tile2 and (tileClass is None or isinstance(tile2, tileClass)): tiles.append(tile2)
        
        for y in range(y1 + 1, y2):
            tile1 = self.getTile(x1, y)
            tile2 = self.getTile(x2, y)
            if tile1 and (tileClass is None or isinstance(tile1, tileClass)): tiles.append(tile1)
            if tile2 and (tileClass is None or isinstance(tile2, tileClass)): tiles.append(tile2)
        
        return tiles
    
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
        
    def buildMap(self):
        raise NotImplementedError("buildMap() not implemented, use a subclass")







        
