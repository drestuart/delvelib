'''
Created on Feb 26, 2014

@author: dstuart
'''

from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Integer

import LevelClass as L
import Util as U
from VoronoiMap import *
import database as db
from MapTileClass import *
from PlayerClass import Player

Base = db.saveDB.getDeclarativeBase()

class Region(Base):
    __tablename__ = "regions"
    __table_args__ = {'extend_existing': True}
    
    def __init__(self, **kwargs):
        self.mapTiles = []
        
        self.tileType = random.choice([Forest, Field, Plain, Mountain])

    id = Column(Integer, primary_key=True)

    mapTiles = relationship("MapTile", backref=backref("region", uselist=False), primaryjoin="Region.id==MapTile.regionId")
    worldMapId = Column(Integer, ForeignKey("world_map.id"))
    name = Column(String)
    
    def addTile(self, tile):
        self.mapTiles.append(tile)

    def getTileType(self):
        # More logic goes here
        return self.tileType


class WorldMap(L.MapBase):
    __tablename__ = "world_map"
    __table_args__ = {'extend_existing': True}
    __mapper_args__ = {'polymorphic_identity':'world_map',
                       'concrete':True}

    def __init__(self, **kwargs):
        super(WorldMap, self).__init__(**kwargs)
        
        self.mapTiles = []
        self.regions = []
        self.num_regions = kwargs['num_regions']
        
        self.load()
    
    id = Column(Integer, primary_key=True)
    mapTiles = relationship("MapTile", backref=backref("worldMap", uselist=False), primaryjoin="WorldMap.id==MapTile.worldMapId")
    regions = relationship("Region", backref=backref("worldMap", uselist=False), primaryjoin="WorldMap.id==Region.worldMapId")
    name = Column(String)
    width = Column(Integer)
    height = Column(Integer)
    levelType = Column(String)
    
    def addTile(self, tile):
        self.mapTiles.append(tile)
    
    def load(self):

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
        ''' Oh here we go. '''
        
        vmap = VMap(self.width, self.height, self.num_regions)

        vmap.generate_voronoi_map()
        
        regions = vmap.regions
        centerpoints = vmap.centerPoints
        adj = vmap.getAdjacency()
        
        # Overlay template, add tiles
        
        
        # Add rivers and other features
        
        
        
        # Create regions and tile objects
        for region in regions:
            newRegion = Region()
            
            tiletype = newRegion.getTileType() 
            
            for (x, y) in region.memberPoints:
                # Skip tiles we've already added
                if self.hasTile[x][y]: 
                    tile = self.getTile(x, y)
                    newRegion.addTile(tile)
                
                else:
                    newTile = tiletype(x, y)
                    newRegion.addTile(newTile)
                    self.addTile(newTile)
                    self.hasTile[x][y] = True


        # Finish up
        self.buildTileArray()
#         db.saveDB.save(self)







        
