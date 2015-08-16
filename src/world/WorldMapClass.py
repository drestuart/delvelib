'''
Created on Feb 26, 2014

@author: dstuart
'''

import LevelClass as L
import Util as U
import random

class Region(object):
    
    def __init__(self, **kwargs):
        self.mapTiles = set()
        self.name = None
        self.worldMap = None

# TODO:
#     worldMapId = Column(Integer, ForeignKey("levels.id"))
    
    def addTile(self, tile):
        self.mapTiles.add(tile)
        tile.setRegion(self)
        
    def replaceTile(self, oldtile, newtile):
        assert oldtile.getXY() == newtile.getXY()
        self.mapTiles.remove(oldtile)
        self.addTile(newtile)

    def getTileType(self):
        return self.tileType


class WorldMap(L.MapBase):
    
    def __init__(self, **kwargs):
        super(WorldMap, self).__init__(**kwargs)
        self.name = None
        self.mapTiles = set()
        self.regions = set()
        self.num_regions = kwargs['num_regions']
        
        self.creatures = set()

        # Initialize self.hasTile
        self.hasTile = []
        
        for dummyx in range(self.width):
            newCol = []
            for dummyy in range(self.height):
                newCol.append(False)
            self.hasTile.append(newCol)

    def load(self):
        pass

    def getMapTiles(self):
        return self.mapTiles

    def addTile(self, tile):
        self.mapTiles.add(tile)
        self.hasTile[tile.getX()][tile.getY()] = True
        if tile.getLevel() is not self:
            tile.setLevel(self)
        
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

    def getRegions(self):
        return self.regions

    def addRegion(self, reg):
        self.regions.add(reg)
    
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
    
    def buildMap(self):
        raise NotImplementedError("buildMap() not implemented, use a subclass")
