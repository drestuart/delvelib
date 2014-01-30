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
import ItemClass as I
import TileClass as T
import Game as G
import Util as U
import ca_cave
import colors
import database as db
import dungeon_builder

Base = db.saveDB.getDeclarativeBase()


class Level(Base):
    '''A class that models a map, essentially an array of tiles.  Holds functionality for drawing itself in a console.  Subclassed into DungeonLevel and FOVMap.'''
    
    __tablename__ = "levels"
    __table_args__ = {'extend_existing': True}
    
    def __init__(self, **kwargs):
        
        self.name = kwargs.get('name', "")
        self.depth = kwargs.get('depth', 0)
        
        self.width = kwargs.get('width')
        self.height = kwargs.get('height')
        
        if not self.width or not self.height:
            raise ValueError("Level class constructor requires width and height values")
        
        self.tiles = []
        self.rooms = []
        self.creatures = []
        
        self.load()
        
##########################################################################
#
#        I N    M E M O R I A M
#
#    For the hours of my life that died here
#
##########################################################################        
#        self.hasTile = [[False]*C.MAP_HEIGHT]*C.MAP_WIDTH
        

    id = Column(Integer, primary_key=True)
    name = Column(String)
    depth = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    
    dungeonId = Column(Integer, ForeignKey("dungeons.id"))
    
    tiles = relationship("Tile", backref=backref("level"), primaryjoin="Level.id==Tile.levelId")
    rooms = relationship("Room", backref = "level")
    
    levelType = Column(String)
    
    __mapper_args__ = {'polymorphic_on': levelType,
                       'polymorphic_identity': 'level'}
    
    def load(self):
        
        self.FOVMap = None
        self.astar = None
        self.upStairs = []
        self.downStairs = []
        self.tileArray = []

        # Initialize self.hasTile
        self.hasTile = []
        
        for dummyx in range(self.width):
            newCol = []
            for dummyy in range(self.height):
                newCol.append(False)
            self.hasTile.append(newCol)
        
        self.findDownStairs()
        self.findUpStairs()
        
        # Event listeners
        pub.subscribe(self.handleAddedCreature, "event.addedCreature")
        pub.subscribe(self.handleRemovedCreature, "event.removedCreature")
        
        pub.subscribe(self.handleDoorOpen, "event.doorOpen")
        pub.subscribe(self.handleDoorClose, "event.doorClose")
        
        
        
        # Load child objects
        for cr in self.creatures:
            cr.load()
        
        for t in self.tiles:
            t.load()
        

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
        
    def getTile(self, x, y):
        if not self.__dict__.get('tileArray'):
#             print "self.tileArray not initialized!"
            self.buildTileArray()
        
        if x >= 0 and x < self.width and y >= 0 and y < self.height:
            return self.tileArray[x][y]
    
        return None
    
    def distance(self, tilea, tileb):
        return U.ChebyshevDistance(tilea.getX(), tileb.getX(), tilea.getY(), tileb.getY())
    
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
        return self.getRandomTileInArea(room.x1, room.x2, room.y1, room.y2)
    
    def getRandomOpenTileInRoom(self, room):
        return self.getRandomOpenTileInArea(room.x1, room.x2, room.y1, room.y2)
        
    def getTilesToDraw(self, playerx, playery, visibility = True):
        tileArray = []
        
        for tile in self.tiles:
            if tile:
                x = tile.x
                y = tile.y
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
                    
                symbol = symbol.encode('ascii', 'ignore')
                tileArray.append((x, y, symbol, color, background))
#                UI.putChar(x, y, symbol, color, background)
        return tileArray
                
    def getTilesInRadius(self, radius, centerX, centerY):
        
        assert radius >= 0 and radius == int(radius) #Do better error checking here.
        
        tiles = []
        
        for rad in range(0, radius):
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
        
        for x in range(x1, x2):
            tile1 = self.getTile(x, y1)
            tile2 = self.getTile(x, y2)
            tiles.append(tile1)
            tiles.append(tile2)
        
        for y in range(y1 + 1, y2 - 1):
            tile1 = self.getTile(x1, y)
            tile2 = self.getTile(x2, y)
            tiles.append(tile1)
            tiles.append(tile2)
        
        assert len(tiles) == 4*radius - 4
        
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
    
#     def isInFOV_old(self, fromx, fromy, tox, toy):
#         if fromx == tox and fromy == toy:
#             return True
#         
#         fromTile = self.getTile(fromx, fromy)
#         toTile = self.getTile(tox, toy)
# 
# #         if fromTile.getVisibleTiles() is None:
#         visibleTiles = self.getVisibleTilesFromTile(fromTile)
#         
# #         else:
# #             visibleTiles = fromTile.getVisibleTiles()
#         
#         return toTile in visibleTiles
    
    def isInFOV(self, fromx, fromy, tox, toy, radius = C.PLAYER_VISION_RADIUS):
        if fromx == tox and fromy == toy:
            return True
        
        fromTile = self.getTile(fromx, fromy)
        toTile = self.getTile(tox, toy)
        
        self.computeFOV(fromx, fromy)
        if (radius == 0 or self.distance(fromTile, toTile) <= radius) and self.FOVMap.isVisible(tox, toy):
            return True
        return False
        
    
#     def getVisibleTilesFromTile(self, fromTile, radius = C.PLAYER_VISION_RADIUS):
#         
#         retArray = []
#          
#         x = fromTile.getX()
#         y = fromTile.getY()
#          
#         self.computeFOV(x, y)
#          
#         for tile in self.tiles:
#             if (radius == 0 or self.distance(fromTile, tile) <= radius) and self.FOVMap.isVisible(tile.getX(), tile.getY()):
#                 retArray.append(tile)
#          
#         return retArray
    
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
#         tileArr = self.getVisibleTilesFromTile(fromTile, radius)
#         
#         retArray = []
#         
#         for tile in tileArr:
#             creature = tile.getCreature()
#             if creature and creature.isVisible():
#                 retArray.append(creature)
#                 
#         return retArray
    
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
        if self.astar: self.astar.setMovable(x, y, True)
        
    def handleAddedCreature(self, tile, creature):
#        print "Creature added to tile", tile.getXY()
        x, y = tile.getXY()
        if self.astar: self.astar.setMovable(x, y, False)
        
    def handleDoorOpen(self, tile):
        x, y = tile.getXY()
        G.message("Door opened " + str(x) + ", " + str(y))
        if self.astar: self.astar.setMovable(x, y, True)
        self.computeFOVProperties(force = True)
    
    def handleDoorClose(self, tile):
        x, y = tile.getXY()
        G.message("Door closed " + str(x) + ", " + str(y))
        if self.astar: self.astar.setMovable(x, y, False)
        self.computeFOVProperties(force = True)
    
    
    def getPathToTile(self, fromTile, toTile):
        
        if self.astar is None:
            self.setupPathing()

        startpoint = fromTile.getXY()
        endpoint = toTile.getXY()
        
#        print "Computing path from", startpoint, "to", endpoint
#        print "Blocking:", fromTile.blocksMove(), toTile.blocksMove()
        
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
                
#            print path
            
            return path
        
        else:
#            print "No path found!"
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
    
    def placeStairs(self):
        raise NotImplementedError("placeStairs() not implemented, use a subclass")
    
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
    defaultWallType = T.RockWall
    defaultTunnelFloorType = T.RockTunnel
    defaultTunnelWallType = T.RockWall
    
    def __init__(self, **kwargs):
        super(DungeonLevel, self).__init__(**kwargs)
    
    def buildLevel(self):
        
        
        d = dungeon_builder.dungeon(self.width, self.height, C.MAX_ROOMS_AND_CORRIDORS, C.ROOM_CHANCE, self)
        d.addTiles(self)
        
        print "Building tile array"    
        self.buildTileArray()    
        
        # Place Stairs
#         print "Placing stairs"
#         self.placeStairs()
        
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
    
    def placeStairs(self):
        raise Exception("Level.placeStairs is deprecated")
        while True:
            # Choose rooms
            upRoom = random.choice(self.rooms)
            
            while True:
                downRoom = random.choice(self.rooms)
                if len(self.rooms) == 1 or downRoom is not upRoom:
                    break
            
            # Place stairs
            
            upTile = self.getRandomOpenTileInRoom(upRoom)
            downTile = self.getRandomOpenTileInRoom(downRoom)
            
            if upTile and downTile and not (upTile.getFeature() or downTile.getFeature()):
            
                upStair = F.upStair()
                upTile.setFeature(upStair)
                self.upStairs.append(upTile)
                
                # Set destination
            
                downStair = F.downStair()
                downTile.setFeature(downStair)
                self.downStairs.append(downTile)
                
                # Set destination
                
                break
            
    def placeCreatureAtRandom(self, creature):
        # Place in a room
        while True:
            room = random.choice(self.rooms)
            tile = self.getRandomOpenTileInRoom(room)
            if tile:
                self.placeCreature(creature, tile)
                break


class CaveLevel(Level):
    
    __mapper_args__ = {'polymorphic_identity': 'cave level'}
    
    defaultFloorType = T.RockTunnel
    defaultWallType = T.RockWall
    
    def __init__(self, **kwargs):
        super(CaveLevel, self).__init__(**kwargs)

    def buildLevel(self):
        
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
        
#         # Place Stairs
#         print "Placing stairs"
#         self.placeStairs()
        
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

    def placeStairs(self):
        raise Exception("Level.placeStairs is deprecated")
        while True:
            upTile = self.getRandomOpenTile()
            downTile = self.getRandomOpenTile()
            
            if upTile and downTile and not (upTile.getFeature() or downTile.getFeature()):
            
                upStair = F.upStair()
                upTile.setFeature(upStair)
                self.upStairs.append(upTile)
                
                downStair = F.downStair()
                downTile.setFeature(downStair)
                self.downStairs.append(downTile)
                
                # TODO Set destinations
                
                break

    def placeCreatureAtRandom(self, creature):
        tile = self.getRandomOpenTile()
        self.placeCreature(creature, tile)
