'''
Created on Mar 10, 2013

@author: dstu
'''

import random

from pubsub import pub
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Integer

import AStar
import Const as C
from DungeonFeatureClass import upStair, downStair
import DungeonFeatureClass as F
import FOVMap as fov
import Game as G
import ItemClass as I
from RoomClass import Room
import TileClass as T
import Util as U
import ca_cave
import colors
import database as db
from randomChoice import weightedChoice

Base = db.saveDB.getDeclarativeBase()

class MapBase(Base):
    
    __tablename__ = "levels"
    __table_args__ = {'extend_existing': True}

    def __init__(self, **kwargs):
        self.creatures = []

        self.name = kwargs.get('name', "")

        self.width = kwargs.get('width')
        self.height = kwargs.get('height')

        if self.width is None or self.height is None:
            raise ValueError("Map class constructor requires width and height values")

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    width = Column(Integer)
    height = Column(Integer)
    levelType = Column(String)
    
    __mapper_args__ = {'polymorphic_on': levelType,
                       'polymorphic_identity': 'level'}
    
    def getWidth(self):
        return self.width
    
    def getHeight(self):
        return self.height
    
    def setupEventListeners(self):
        pass
    
    def computeFOV(self, x, y):
        pass
    
    def bumpEdge(self, creature):
        return False
    
    def distance(self, tilea, tileb):
        return U.ChebyshevDistance(tilea.getX(), tileb.getX(), tilea.getY(), tileb.getY())


class Level(MapBase):
    '''A class that models a map as an array of tiles.'''
    
    def __init__(self, **kwargs):
        super(Level, self).__init__(**kwargs)
        
        self.depth = kwargs.get('depth', 0)
        self.area = kwargs['area']
                
        self.tiles = []
        self.rooms = []
        
        self.FOVMap = None
        self.astar = None
        self.upStairs = []
        self.downStairs = []
        self.tileArray = []
#         self.load()
        
##########################################################################
#
#        I N    M E M O R I A M
#
#    For the hours of my life that died here
#
##########################################################################        
#        self.hasTile = [[False]*C.MAP_HEIGHT]*C.MAP_WIDTH
        

    depth = Column(Integer)
    
    areaId = Column(Integer, ForeignKey("areas.id"))
    startingLevelOfId = Column(Integer, ForeignKey("areas.id"))
    
    tiles = relationship("Tile", backref=backref("level"), primaryjoin="Level.id==Tile.levelId")
    rooms = relationship("Room", backref = "level")
    
    entryPointX = Column(Integer)
    entryPointY = Column(Integer)
    
    __mapper_args__ = {'polymorphic_identity': 'level',
                       'concrete':True}

    
    def load(self):
        
        # Initialize self.hasTile
        self.hasTile = U.twoDArray(self.width, self.height, False)
        
        self.findDownStairs()
        self.findUpStairs()
        
        # Load child objects
        for cr in self.creatures:
            cr.load()
        
        for t in self.tiles:
            t.load()
        
        self.setupEventListeners()
        
    def setupEventListeners(self):
        
        # Event listeners
        try:
            if not pub.isSubscribed(self.handleAddedCreature, "event.addedCreature"):
                pub.subscribe(self.handleAddedCreature, "event.addedCreature")
                pub.subscribe(self.handleRemovedCreature, "event.removedCreature")
        except:
            pub.subscribe(self.handleAddedCreature, "event.addedCreature")
            pub.subscribe(self.handleRemovedCreature, "event.removedCreature")
        
        try:
            if not pub.isSubscribed(self.handleDoorOpen, "event.doorOpen"):
                pub.subscribe(self.handleDoorOpen, "event.doorOpen")
                pub.subscribe(self.handleDoorClose, "event.doorClose")
        except:
            pub.subscribe(self.handleDoorOpen, "event.doorOpen")
            pub.subscribe(self.handleDoorClose, "event.doorClose")

    
    
    def buildTileArray(self):
        self.tileArray = []
        
        # Initialize
        for dummyx in range(self.width):
            newCol = []
            for dummyy in range(self.height):
                newCol.append(None)
            self.tileArray.append(newCol)
            
        # Fill in
        for tile in self.tiles:
            self.tileArray[tile.x][tile.y] = tile
            
    def getDepth(self):
        return self.depth
        
    def getTile(self, x, y):
        if not self.__dict__.get('tileArray'):
#             print "self.tileArray not initialized!"
            self.buildTileArray()
        
        if x >= 0 and x < self.width and y >= 0 and y < self.height:
            return self.tileArray[x][y]
    
        print "Bad coordinates: ", (x, y)
        return None
    
    def replaceTile(self, oldtile, newtile):
        assert oldtile.getXY() == newtile.getXY()
        self.tiles.remove(oldtile)
        self.tiles.append(newtile)
        
        newtile.setLevel(self)
        
        # TODO: Move any items from the old tile to the new tile
        
    def addRoom(self, room):
        self.rooms.append(room)
    
    def getEntryPoint(self):
        return self.getTile(self.entryPointX, self.entryPointY)
    
    def getRandomTile(self):
        randX = random.randint(0, self.width)
        randY = random.randint(0, self.height)
        return self.getTile(randX, randY)
    
    def getRandomOpenTile(self):
        while True:
            randTile = self.getRandomTile()
            if randTile and not randTile.blocksMove():
                return randTile
            
    def getRandomTileInArea(self, x1, x2, y1, y2):
        
        x1 = max(0, x1)
        x1 = min(x1, self.width)
        
        x2 = max(0, x2)
        x2 = min(x2, self.width)
        
        y1 = max(0, y1)
        y1 = min(y1, self.height)
        
        y2 = max(0, y2)
        y2 = min(y2, self.height)
        
        
#        randX = random.randint(x1, x2)
        randX = random.randint(min(x1, x2), max(x1, x2))
        
#        randY = random.randint(y1, y2)

        randY = random.randint(min(y1, y2), max(y1, y2))

        return self.getTile(randX, randY)
    
    def getRandomOpenTileInArea(self, x1, x2, y1, y2):
#        print "Looking for tile in x=[", x1, x2, "], y=[", y1, y2, "]"
        
        openTiles = []
        
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                tile = self.getTile(x, y)
                if tile and not tile.blocksMove():
                    openTiles.append(tile)
                    
        if len(openTiles) == 0:
            return None
        
        else:
            return random.choice(openTiles)
                
            
    def getRandomTileInRoom(self, room):
#         return self.getRandomTileInArea(room.x1, room.x2, room.y1, room.y2)
        return random.choice(room.getTiles())
    
    def getRandomOpenTileInRoom(self, room):
#         return self.getRandomOpenTileInArea(room.x1, room.x2, room.y1, room.y2)
        openTiles = []
        for tile in room.getTiles():
            if tile and not tile.blocksMove():
                openTiles.append(tile)
                
        return random.choice(openTiles)
        
    def getTilesToDraw(self, playerx, playery, cameradims, visibility = True):
        retArray = []
        
        camx, camy, camwidth, camheight = cameradims
        
        for tile in self.tiles:
            if tile:
                x = tile.x
                y = tile.y
                
                # Is the tile in the camera's range?
                if (x < camx or x >= camx + camwidth or y < camy or y >= camy + camheight):
                    continue
                
#                print "Drawing", x, ",", y, ":", tile.toDraw()
                
                # Determine visibility
                if visibility:
                    if self.isInFOV(playerx, playery, x, y):
                        
                        tile.setExplored(True)
                        
                        symbol, color, background = tile.toDraw()
                        background = colors.colorLightWall
                        tile.setLastSeenSymbol(symbol)
                        
                    
                    else:
                        
                        if tile.getExplored():
                            symbol = tile.getLastSeenSymbol()
                            color = colors.colorNotInFOV
                            background = colors.colorWallNotInFOV
                            
                        else:
                            symbol = ' '
                            color = colors.black
                            background = colors.blankBackground
                else:
                    symbol, color, background = tile.toDraw()
                    background = colors.colorLightWall
                    
#                 symbol = symbol.encode('ascii', 'ignore')
                retArray.append((x, y, symbol, color, background))
#                UI.putChar(x, y, symbol, color, background)
        return retArray
                
    def getTilesInRadius(self, radius, centerX, centerY):
        
        assert radius >= 0 and radius == int(radius) #Do better error checking here.
        
        tiles = []
        
        for rad in range(0, radius + 1):
            tiles += self.getTilesAtRadius(rad, centerX, centerY)
        
        return tiles
        
    
    def getTilesAtRadius(self, radius, centerX, centerY):
               
        assert radius >= 0 and radius == int(radius) #Do better error checking here.
        
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
            if tile1: tiles.append(tile1)
            if tile2: tiles.append(tile2)
        
        for y in range(y1 + 1, y2):
            tile1 = self.getTile(x1, y)
            tile2 = self.getTile(x2, y)
            if tile1: tiles.append(tile1)
            if tile2: tiles.append(tile2)
        
        return tiles
    
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
    
    def computeFOVProperties(self, force = False):
        
        fovArray = []
        self.FOVMap = None
        
        # TODO hang on to fovArray and change sight properties in-place
        
        # Initialize fovArray
        for dummyy in range(self.height):
            newCol = []
            for dummyx in range(self.width):
                newCol.append(False)
            fovArray.append(newCol)
        
        for tile in self.tiles:
            x = tile.x
            y = tile.y
            blocksSight = tile.blocksSight()
            
            fovArray[y][x] = blocksSight
            
        self.FOVMap = fov.FOVMap(fovArray)
        
        if force:
            self.FOVMap.lastx, self.FOVMap.lasty = None, None
        
    def computeFOV(self, x, y):
        '''Compute the field of view of this map with respect to a particular position'''
        if not self.__dict__.get('FOVMap'):
            self.computeFOVProperties()
            
        self.FOVMap.do_fov(x, y, C.FOV_RADIUS)
    
    def isInFOV(self, fromx, fromy, tox, toy, radius = C.PLAYER_VISION_RADIUS):
        if fromx == tox and fromy == toy:
            return True
        
        fromTile = self.getTile(fromx, fromy)
        toTile = self.getTile(tox, toy)
        
        self.computeFOV(fromx, fromy)
        if (radius == 0 or self.distance(fromTile, toTile) <= radius) and self.FOVMap.isVisible(tox, toy):
            return True
        return False
        
    def getVisibleCreaturesFromTile(self, fromTile, radius = C.PLAYER_VISION_RADIUS):
        
        fromx, fromy = fromTile.getXY()
        thisCreature = fromTile.getCreature()
        retArray = []
        
        for creature in self.creatures:
            if creature is thisCreature: continue
            
            creaturex, creaturey = creature.getTile().getXY()
            if creature and creature.isVisible() and self.isInFOV(fromx, fromy, creaturex, creaturey):
                retArray.append(creature)
            
        return retArray
    
    def setupPathing(self):
        mapdata = []
        width = self.width
        height = self.height

        for dummyx in range(width):
            for dummyy in range(height):
                mapdata.append(1)
        
        for tile in self.tiles:
            if tile.blocksMove():
                mapdata[tile.getX() + tile.getY() * width] = -1
        
        self.astar = AStar.setUpMap(mapdata, self.width, self.height)
        
    def handleRemovedCreature(self, tile, creature):
#        print "Creature removed from tile", tile.getXY()
        x, y = tile.getXY()
        if self.__dict__.get('astar'): self.astar.setMovable(x, y, True)
        
    def handleAddedCreature(self, tile, creature):
#        print "Creature added to tile", tile.getXY()
        x, y = tile.getXY()
        if self.__dict__.get('astar'): self.astar.setMovable(x, y, False)
        
    def handleDoorOpen(self, tile):
        x, y = tile.getXY()
        G.message("Door opened " + str(x) + ", " + str(y))
        if self.__dict__.get('astar'): self.astar.setMovable(x, y, True)
        self.computeFOVProperties(force = True)
    
    def handleDoorClose(self, tile):
        x, y = tile.getXY()
        G.message("Door closed " + str(x) + ", " + str(y))
        if self.__dict__.get('astar'): self.astar.setMovable(x, y, False)
        self.computeFOVProperties(force = True)
    
    
    def getPathToTile(self, fromTile, toTile):
        
        if self.__dict__.get('astar') is None:
            self.setupPathing()

        startpoint = fromTile.getXY()
        endpoint = toTile.getXY()
        
        # Hack to fix issue with starting and ending tiles being blocked
        self.astar.setMovable(fromTile.getX(), fromTile.getY(), True)
        if toTile.blocksMove() and toTile.getCreature(): self.astar.setMovable(toTile.getX(), toTile.getY(), True)
        
        pathObj = AStar.findPath(startpoint, endpoint, self.astar)
        
        # Disenhack
        self.astar.setMovable(fromTile.getX(), fromTile.getY(), False)
        if toTile.blocksMove() and toTile.getCreature(): self.astar.setMovable(toTile.getX(), toTile.getY(), False)
        
        if pathObj:
            path = [(node.location.x, node.location.y) for node in pathObj.getNodes()]
            
            if fromTile.getXY() == path[0]:
                path.pop(0)
                
            return path
        
        else:
            return None
        
    
        
    def findCreatures(self):
        self.creatures = []
        for tile in self.tiles:
            if tile.creature:
                self.creatures.append(tile.creature)
        
    def placeCreature(self, creature, tile):
        success = tile.placeCreature(creature)
        if success and not creature in self.creatures:
            self.creatures.append(creature)
        return success
    
    def placeCreatureAtRandom(self, creature):
        raise NotImplementedError("placeStairs() not implemented, use a subclass")
        
    def buildLevel(self):
        raise NotImplementedError("buildLevel() not implemented, use a subclass")
    
    def placeItems(self):
        raise NotImplementedError("placeItems() not implemented, use a subclass")
    
    def placeUpStair(self):
        raise NotImplementedError("placeUpStair() not implemented, use a subclass")
    
    def placeDownStair(self):
        raise NotImplementedError("placeDownStair() not implemented, use a subclass")
    
    def findUpStairs(self):
        self.upStairs = []
        for tile in self.tiles:
            feature = tile.getFeature()
            if feature and isinstance(feature, upStair):
                self.upStairs.append(tile)
    
    def getUpStairs(self):
#        if not self.upStairs:
        if not self.__dict__.get('upStairs', None):
            self.findUpStairs()
        
        return self.upStairs
    
    def getArea(self):
        return self.area
    
    def findDownStairs(self):
        self.downStairs = []
        for tile in self.tiles:
            feature = tile.getFeature()
            if feature and isinstance(feature, downStair):
                self.downStairs.append(tile)
    
    def getDownStairs(self):
#        if not self.downStairs:
        if not self.__dict__.get('downStairs', None):
            self.findDownStairs()
        
        return self.downStairs
    
    def placeOnUpStair(self, creature):
        stairTiles = self.getUpStairs()
        if stairTiles:
            self.placeCreature(creature, stairTiles[0])
            return True
        raise Exception("No upstair found!")
        
    def placeOnDownStair(self, creature):
        stairTiles = self.getDownStairs()
        if stairTiles:
            self.placeCreature(creature, stairTiles[0])
            return True
        raise Exception("No downstair found!")
    
    def setNextLevel(self, other):
        
        # Just get the first one, fix later
        dstair = self.getDownStairs()[0].getFeature()
        ustairTile = other.getUpStairs()[0]
        
        dstair.setDestination(ustairTile)
        
    def setPreviousLevel(self, other):

        # Just get the first one, fix later
        ustair = self.getUpStairs()[0].getFeature()
        dstairTile = other.getDownStairs()[0]
        
        ustair.setDestination(dstairTile)
        
    def bumpEdge(self, creature):
        if self.depth == 0:
            return self.getArea().getMapTile()
        return False
    
    def findEntryPoint(self):
        x, y = self.width/2, self.height - 1 # Bottom center
        if not self.getTile(x, y).blocksMove():
            self.entryPointX, self.entryPointY = x, y
            return
        
        for i in range(1, self.width/2):
            x = x + i
            if not self.getTile(x, y).blocksMove():
                self.entryPointX, self.entryPointY = x, y
                return
            
            x = x - i
            if not self.getTile(x, y).blocksMove():
                self.entryPointX, self.entryPointY = x, y
                return
        
        raise Exception("Couldn't find valid entry point")

        
def connectLevels(upper, lower):
    
    # Place a downstair in the upper level
    downTile = upper.placeDownStair()
    dStair = downTile.getFeature()
    
    # Place an upstair in the lower level
    upTile = lower.placeUpStair()
    uStair = upTile.getFeature()
    
    # Set the stair tiles as destinations for their respective stairs
    uStair.setDestination(downTile)
    dStair.setDestination(upTile)
    
    return True
        
class DungeonLevel(Level):
    '''A Level subclass for modeling one dungeon level.  Includes functionality for passing time and level construction.'''
    
    __mapper_args__ = {'polymorphic_identity': 'dungeon level'}

    defaultFloorType = T.StoneFloor
    defaultWallType = T.StoneWall
    defaultTunnelType = T.StoneFloor
    
    def __init__(self, **kwargs):
        self.tilesWide = kwargs['tilesWide']
        self.tilesHigh = kwargs['tilesHigh']
        
        # Fill in default width values if necessary
        self.width = kwargs.get('width', self.tilesWide * self.MapBuilderType.tileset.tileWidth + 2)
        self.height = kwargs.get('height', self.tilesHigh * self.MapBuilderType.tileset.tileHeight + 2)
        
        kwargs['width'] = self.width
        kwargs['height'] = self.height
        
        super(DungeonLevel, self).__init__(**kwargs)
    
    def buildLevel(self):

        # Initialize self.hasTile
        self.hasTile = U.twoDArray(self.width, self.height, False)
        
        # Generate level using wang tiles
        dmap = self.MapBuilderType(self.tilesWide, self.tilesHigh, margin = 1)
        self.addTiles(dmap)
        
        # Place items
        print "Placing items"
        self.placeItems()
        
        print "Saving open tiles"
        db.saveDB.save(self)
        
        print "Setting up FOV"
        self.computeFOVProperties()
        
        print "Setting up pathing"
        self.setupPathing()
        
        print "Finding the stairs"
        self.findUpStairs()
        self.findDownStairs()
        
    def getTileType(self, glyph):
        tileDict = {'.' : (self.defaultFloorType, None),
                    ',' : (self.defaultTunnelType, None),
                    '#' : (self.defaultWallType, None),
                    '_' : (self.defaultFloorType, F.Altar),
                    '+' : {(self.defaultTunnelType, F.Door) : 0.75, 
                           (self.defaultTunnelType, None) : 0.25},
                    '?' : {(self.defaultFloorType, None) : 0.5,
                           (self.defaultWallType, None) : 0.5},
                    '&' : (self.defaultFloorType, F.Statue),}
        
        types = tileDict[glyph]
        if isinstance(types, tuple):
            return types
        
        return weightedChoice(types)
    
    def addTiles(self, dmap):
        
        tiles = dmap.getMapGlyphs()
        height = len(tiles)
        width = len(tiles[0])
        
        # Construct tiles
        for y in range(height):
            for x in range(width):
                glyph = tiles[y][x]
                newTileType, featureType = self.getTileType(glyph)
                
                newTile = newTileType(x, y)
                
                if featureType:
                    feature = featureType()
                    newTile.setFeature(feature)
                
                self.tiles.append(newTile)
                self.hasTile[x][y] = True
                
        print "Building tile array"    
        self.buildTileArray() 
                
        # Add rooms
        rooms = dmap.getRooms()
        
        for room in rooms:
            newRoom = Room()
            
            for x, y in room:
                tile = self.getTile(x, y)
                newRoom.addTile(tile)
            
            self.addRoom(newRoom)
            
    def placeItems(self):
        
        for room in self.rooms:
            # Just place one random item for now
            tile = self.getRandomOpenTileInRoom(room)
            if tile:
                item = I.getRandomItem()
                tile.addObject(item)

    def placeUpStair(self):
        if not self.__dict__.get('upStairs'):
            self.upStairs = []
        
        while True:
            upRoom = random.choice(self.rooms)
            upTile = self.getRandomOpenTileInRoom(upRoom)
            
            if upTile and not upTile.getFeature():
                
                upStair = F.upStair()
                upTile.setFeature(upStair)
                self.upStairs.append(upTile)
                
                break
            
        return upTile
        
    def placeDownStair(self):
        if not self.__dict__.get('downStairs'):
            self.downStairs = []
        
        while True:
            downRoom = random.choice(self.rooms)
            downTile = self.getRandomOpenTileInRoom(downRoom)
            
            if downTile and not downTile.getFeature():
                
                downStair = F.downStair()
                downTile.setFeature(downStair)
                self.downStairs.append(downTile)
                
                break
            
        return downTile
    
    def placeCreatureAtRandom(self, creature, inRoom = True):
        # Place in a room
        while True:
            if inRoom: 
                room = random.choice(self.rooms)
                tile = self.getRandomOpenTileInRoom(room)
            else: tile = self.getRandomOpenTile()
            if tile:
                self.placeCreature(creature, tile)
                break
            
    def placeCreatureAtEntrance(self, creature):
        self.placeOnUpStair(creature)


class CaveLevel(Level):
    
    __mapper_args__ = {'polymorphic_identity': 'cave level'}
    
    defaultFloorType = T.RockTunnel
    defaultWallType = T.RockWall
    
    def __init__(self, **kwargs):
        super(CaveLevel, self).__init__(**kwargs)

    def buildLevel(self):
        
        # Initialize self.hasTile
        self.hasTile = U.twoDArray(self.width, self.height, False)
        
        levelGrid = ca_cave.generateMap(self.width, self.height)
        rows = levelGrid.split("\n")

        for y in range(self.height):
            for x in range(self.width):
                shape = rows[y][x]
                
                if shape == '.':
                    newTile = self.defaultFloorType(x, y)
                    
                elif shape == '#':
                    newTile = self.defaultWallType(x, y)
                
                else:
                    print "Bad tile type:'", shape, "'"
                
                self.tiles.append(newTile)
                self.hasTile[x][y] = True
        
        
        print "Building tile array"    
        self.buildTileArray()    
        
        # Place items
        print "Placing items"
        self.placeItems()
        
        print "Saving open tiles"
        db.saveDB.save(self)
        
        print "Setting up FOV"
        self.computeFOVProperties()
        
        print "Finding the stairs"
        self.findUpStairs()
        self.findDownStairs()
    
    def placeItems(self):
        # Just place 20 random items for now
        placedItems = 0
        while placedItems < 20:
            tile = self.getRandomOpenTile()
            if tile:
                item = I.getRandomItem()
                tile.addObject(item)
                placedItems += 1
        
    def placeUpStair(self):
        if not self.__dict__.get('upStairs'):
            self.upStairs = []
            
        while True:
            upTile = self.getRandomOpenTile()
            
            if upTile and not upTile.getFeature():
                
                upStair = F.upStair()
                upTile.setFeature(upStair)
                self.upStairs.append(upTile)
                
                break
            
        return upTile
        
    def placeDownStair(self):
        if not self.__dict__.get('downStairs'):
            self.downStairs = []
            
        while True:
            downTile = self.getRandomOpenTile()
            
            if downTile and not downTile.getFeature():
                
                downStair = F.downStair()
                downTile.setFeature(downStair)
                self.downStairs.append(downTile)
                
                break
            
        return downTile

    def placeCreatureAtRandom(self, creature):
        tile = self.getRandomOpenTile()
        self.placeCreature(creature, tile)
        
    def placeCreatureAtEntrance(self, creature):
        self.placeOnUpStair(creature)

class TownLevel(DungeonLevel):
    
    __mapper_args__ = {'polymorphic_identity': 'town level'}
    
    def __init__(self, **kwargs):
        self.tilesWide = kwargs['tilesWide']
        self.tilesHigh = kwargs['tilesHigh']
        self.width = self.tilesWide * self.MapBuilderType.tileset.tileWidth
        self.height = self.tilesHigh * self.MapBuilderType.tileset.tileHeight
        super(TownLevel, self).__init__(width = self.width, height = self.height, **kwargs)
        
    buildingWallTile = T.WoodWall
    buildingFloorTile = T.WoodFloor
    outsideFloorTile = T.GrassFloor
    roadTile = T.RoadFloor
    
    def getTileType(self, glyph):
        tileDict = {'.' : (self.outsideFloorTile, None),
                    ',' : (self.buildingFloorTile, None),
                    '#' : (self.buildingWallTile, None),
                    '+' : (self.buildingFloorTile, F.Door),
                    '~' : (self.roadTile, None)}
        
        types = tileDict[glyph]
        if isinstance(types, tuple):
            return types
        
        return weightedChoice(types)
    
    def buildLevel(self):

        # Initialize self.hasTile
        self.hasTile = U.twoDArray(self.width, self.height, False)

        tmap = self.MapBuilderType(self.tilesWide, self.tilesHigh)
        self.addTiles(tmap)

        # Place items
        print "Placing items"
        self.placeItems()
        
        print "Finding entry point"
        self.findEntryPoint()
        
        print "Saving open tiles"
        db.saveDB.save(self)
        
        print "Setting up FOV"
        self.computeFOVProperties()
        
        print "Setting up pathing"
        self.setupPathing()
        
        print "Finding the stairs"
        self.findUpStairs()
        self.findDownStairs()

    def placeCreatureAtRandom(self, creature):
        # Very random
        # TODO: make more random
        tile = self.getTile(1, 1)
        self.placeCreature(creature, tile)
        
    def placeCreatureAtEntrance(self, creature):
        tile = self.getTile(self.entryPointX, self.entryPointY)
        self.placeCreature(creature, tile)


class WildernessLevel(Level):
    __mapper_args__ = {'polymorphic_identity': 'wilderness level'}
    
    defaultFloorType = T.GrassFloor
    buildingWallType = T.StoneWall
    buildingFloorType = T.StoneFloor
    
    def __init__(self, **kwargs):
        super(WildernessLevel, self).__init__(**kwargs)

    def buildLevel(self):
        # Initialize self.hasTile
        self.hasTile = U.twoDArray(self.width, self.height, False)
        
        for y in range(self.height):
            for x in range(self.width):
                newTile = self.defaultFloorType(x, y)
                    
                self.tiles.append(newTile)
                self.hasTile[x][y] = True
        
        print "Building tile array"    
        self.buildTileArray()    
        
        print "Finding entry point"
        self.findEntryPoint()
        
        print "Saving open tiles"
        db.saveDB.save(self)
        
        print "Setting up FOV"
        self.computeFOVProperties()
        
    def placeCreatureAtRandom(self, creature):
        tile = self.getRandomOpenTile()
        self.placeCreature(creature, tile)
        
    def placeCreatureAtEntrance(self, creature):
        tile = self.getTile(self.entryPointX, self.entryPointY)
        self.placeCreature(creature, tile)
        
    def placeDownStair(self):
        if not self.__dict__.get('downStairs'):
            self.downStairs = []
        
        while True:
            downRoom = random.choice(self.rooms)
            downTile = self.getRandomOpenTileInRoom(downRoom)
            
            if downTile and not downTile.getFeature():
                
                downStair = F.downStair()
                downTile.setFeature(downStair)
                self.downStairs.append(downTile)
                
                break
            
        return downTile
    
    def placeDungeonEntrance(self):
        raise NotImplementedError("placeDungeonEntrance() not implemented, use a subclass")
        
