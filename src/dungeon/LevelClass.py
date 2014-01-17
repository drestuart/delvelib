'''
Created on Mar 10, 2013

@author: dstu
'''

#from Import import *
#libtcod = importLibtcod()

from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Integer
from sqlalchemy import and_
import Const as C
import RoomClass as R
import TileClass as T
import DungeonFeatureClass as F
import ItemClass as I
import colors
import database as db
import random


#from CreatureClass import *


Base = db.saveDB.getDeclarativeBase()


class Level(Base):
    '''A class that models a map, essentially an array of tiles.  Holds functionality for drawing itself in a console.  Subclassed into DungeonLevel and FOVMap.'''
    
    __tablename__ = "levels"
    __table_args__ = {'extend_existing': True}
    
    def __init__(self, **kwargs):
        
        self.name = kwargs.get('name', " ")
        self.depth = kwargs.get('depth', 0)
        
        self.defaultFloorType = kwargs.get('defaultFloorType', None)
        self.defaultWallType = kwargs.get('defaultWallType', None)
        self.defaultTunnelFloorType = kwargs.get('defaultTunnelFloorType', None)
        self.defaultTunnelWallType = kwargs.get('defaultTunnelWallType', None)

        self.nextLevel = kwargs.get('nextLevel', None)
        self.previousLevel = kwargs.get('previousLevel', None)
        
        # TODO instantiate FOV map
#        self.FOVMap = libtcod.map_new(C.MAP_WIDTH, C.MAP_HEIGHT)
        self.needToComputeFOV = True
        
        self.tiles = []
        self.rooms = []
        
        self.creatures = []
        
##########################################################################
#
#        I N    M E M O R I A M
#
#    For the hours of my life that died here
#
##########################################################################        
#        self.hasTile = [[False]*C.MAP_HEIGHT]*C.MAP_WIDTH
        
        # Initialize self.hasTile
        self.hasTile = []
        self.tileArray = []
        
        for dummyx in range(C.MAP_WIDTH):
            newCol = []
            for dummyy in range(C.MAP_HEIGHT):
                newCol.append(False)
            self.hasTile.append(newCol)

    id = Column(Integer, primary_key=True)
    name = Column(String)
    depth = Column(Integer)
    
    nextLevel = relationship("Level", uselist=False, primaryjoin="Level.id==Level.nextLevelId")
    nextLevelId = Column(Integer, ForeignKey("levels.id"))
    
    previousLevel = relationship("Level", uselist=False, primaryjoin="Level.id==Level.previousLevelId")
    previousLevelId = Column(Integer, ForeignKey("levels.id"))
    
    tiles = relationship("Tile", backref=backref("level"), primaryjoin="Level.id==Tile.levelId")
    rooms = relationship("Room", backref = "level")
    
    levelType = Column(String)
    
    mapConsole = None
    
    __mapper_args__ = {'polymorphic_on': levelType,
                       'polymorphic_identity': 'level'}
    

    def buildTileArray(self):
        self.tileArray = []
        
        # Initialize
        for dummyx in range(C.MAP_WIDTH):
            newCol = []
            for dummyy in range(C.MAP_HEIGHT):
                newCol.append(None)
            self.tileArray.append(newCol)
            
        # Fill in
        for tile in self.tiles:
            self.tileArray[tile.x][tile.y] = tile
        
    def getTile(self, x, y):
        if not self.tileArray:
            print "self.tileArray not initialized!"
            return None
        
        return self.tileArray[x][y]
    
    
    def getTileFromDB(self, x, y, level):
        query = db.saveDB.getQueryObj(T.Tile)
        query.filter(and_(T.Tile.x == x, T.Tile.y == y, T.Tile.level == level))
        return db.saveDB.runQuery(query)
    
    def getRandomTile(self):
        randX = random.randint(0, C.MAP_WIDTH)
        randY = random.randint(0, C.MAP_HEIGHT)
        return self.getTile(randX, randY)
    
    def getRandomOpenTile(self):
        while True:
            randTile = self.getRandomTile()
            if randTile and not randTile.blocksMove():
                return randTile
            
    def getRandomTileInArea(self, x1, x2, y1, y2):
        
        x1 = max(0, x1)
        x1 = min(x1, C.MAP_WIDTH)
        
        x2 = max(0, x2)
        x2 = min(x2, C.MAP_WIDTH)
        
        y1 = max(0, y1)
        y1 = min(y1, C.MAP_HEIGHT)
        
        y2 = max(0, y2)
        y2 = min(y2, C.MAP_HEIGHT)
        
        
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
        
    def getMapConsole(self):
        return self.mapConsole

    def setMapConsole(self, con):
        self.mapConsole = con

    def isInFOV(self, x, y):
        pass
        #TODO return FOV status
#        return libtcod.map_is_in_fov(self.FOVMap, x, y)
                
    # Draw that map!
    def draw(self, visibility = True):

        for tile in self.tiles:
            if tile:
                x = tile.x
                y = tile.y
#                print "Drawing", x, ",", y, ":", tile.toDraw()
                
                # Determine visibility
                if visibility:
                    if self.isInFOV(x, y):
                        
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
                # TODO blit symbol to console
#                libtcod.console_put_char_ex(self.mapConsole, x, y, symbol, color, background)
                
    # Erase that map!
    def clear(self):
        for x in range(C.MAP_WIDTH):
            for y in range(C.MAP_HEIGHT):
                pass
                # TODO erase map
#                libtcod.console_put_char_ex(self.mapConsole, x, y, ' ', colors.black, libtcod.BKGND_NONE)
                
            
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
        
        x2 = min(centerX + radius, C.MAP_WIDTH)
        y2 = min(centerY + radius, C.MAP_HEIGHT)
        
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
    
    def getVisibleTilesFromTile(self, fromTile, radius = 0):
        
        x = fromTile.getX()
        y = fromTile.getY()
        
        self.setNeedToComputeFOV(True)
        self.computeFOV(x, y, radius)
        self.setNeedToComputeFOV(True)
        
        retArray = []
        
        for tile in self.tiles:
            #TODO get FOV status
#            if libtcod.map_is_in_fov(self.FOVMap, tile.getX(), tile.getY()):
                retArray.append(tile)
                
        return retArray
    
    def getVisibleCreaturesFromTile(self, fromTile, radius = 0):
        
        tileArr = self.getVisibleTilesFromTile(fromTile, radius)
        
        retArray = []
        
        for tile in tileArr:
            creature = tile.getCreature()
            if creature and creature.isVisible():
                retArray.append(creature)
                
        return retArray
        
    def getPathToTile(self, fromTile, toTile):
        pass
        # TODO compute path
#        path = libtcod.path_new_using_map(self.FOVMap, dcost=1)
#        libtcod.path_compute(path, fromTile.getX(), fromTile.getY(), toTile.getX(), toTile.getY())

#        return path
        
    def isWalkable(self, xFrom, yFrom, xTo, yTo, userData):
        if self.getTile(xTo, yTo).blocksMove():
            return 0
        
        return 1
    
    def computeFOVProperties(self):
        
        if not self.FOVMap:
            pass
        # TODO: Create FOV map
#            self.FOVMap = libtcod.map_new(C.MAP_WIDTH, C.MAP_HEIGHT)
        
        for tile in self.tiles:
            x = tile.x
            y = tile.y
            blocksMove = tile.blocksMove()
            blocksSight = tile.blocksSight()
            
            # TODO: Fill in FOV map
#            libtcod.map_set_properties(self.FOVMap, x, y, not blocksMove, not blocksSight)
                
    def computeFOV(self, x, y, radius = 0):
        '''Compute the field of view of this map with respect to a particular position'''
        if self.getNeedToComputeFOV() == False:
            return
        else:
            
            self.setNeedToComputeFOV(False)
            
            # TODO Compute FOV
#            libtcod.map_compute_fov(self.FOVMap, x, y, radius, C.FOV_LIGHT_WALLS, C.FOV_ALGO)

    def getNeedToComputeFOV(self):
        return self.needToComputeFOV

    def setNeedToComputeFOV(self, value):
        self.needToComputeFOV = value
        
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
    
    def placeCreatureInRandomRoom(self, creature):
        while True:
            room = random.choice(self.rooms)
            tile = self.getRandomOpenTileInRoom(room)
            if tile:
                self.placeCreature(creature, tile)
                break
        
    def placeCreatureInRandomTile(self, creature):
        tile = self.getRandomOpenTile()
        self.placeCreature(creature, tile)
        
    
    
            
class DungeonLevel(Level):
    '''A Level subclass for modeling one dungeon level.  Includes functionality for passing time and level construction.'''
    
    __mapper_args__ = {'polymorphic_identity': 'dungeon level'}

    
    def __init__(self, **kwargs):
        super(DungeonLevel, self).__init__(**kwargs)
    
    def buildLevelOld(self):
        '''Add some rooms to the level'''
        rooms = []

        # Make some rooms
        for dummy in range(C.MAX_ROOMS):
            #random width and height
            
            w = random.randint(C.ROOM_MIN_SIZE, C.ROOM_MAX_SIZE)
            h = random.randint(C.ROOM_MIN_SIZE, C.ROOM_MAX_SIZE)
    
            #random position without going out of the boundaries of the map
            
            x = random.randint(C.DUNGEON_MARGIN, C.MAP_WIDTH - w - 1 - C.DUNGEON_MARGIN)
            y = random.randint(C.DUNGEON_MARGIN, C.MAP_HEIGHT - h - 1 - C.DUNGEON_MARGIN)
    
            newRoom = R.Room(x = x, y = y, width = w, height = h,
                             defaultFloorType = self.defaultFloorType, defaultWallType = self.defaultWallType)
     
            #run through the other rooms and see if they intersect with this one
            failed = False
            for otherRoom in rooms:
                if newRoom.intersect(otherRoom):
                    failed = True
                    del newRoom
                    break
            
            if not failed:
                #print "No room intersection detected"
                #this means there are no intersections, so this room is valid
                #"paint" it to the map's tiles
                self.createRoom(newRoom)
                
                #self.placeObjects(newRoom)
                
                rooms.append(newRoom)
                self.rooms.append(newRoom)

        # Connect rooms with tunnels
        if len(self.rooms) >= 1:
            for rn in range(len(self.rooms) - 1):
                thisRoom, nextRoom = self.rooms[rn], self.rooms[rn + 1]
                
                self.createTunnel(thisRoom, nextRoom)
            
            lastRoom = self.rooms[-1]
            firstRoom = self.rooms[0]
            self.createTunnel(lastRoom, firstRoom)
        
        
        print "Placing walls"
        # Fill in empty spaces
        self.fillInSpaces()
        
        print "Building tile array"    
        self.buildTileArray()    
        
        # Place Stairs
        print "Placing stairs"
        self.placeStairs()
        
        print "Saving open tiles"
        db.saveDB.save(self)
        
        print "Setting up FOV"
        self.computeFOVProperties()
        

    def buildLevel(self):
        '''
        Adapted from the dungeon building algorithm by Zack Hovatter (http://roguebasin.roguelikedevelopment.org/index.php?title=User:Zackhovatter)
        
        Available at: http://roguebasin.roguelikedevelopment.org/index.php?title=Python_Curses_Example_of_Dungeon-Building_Algorithm
        
        '''
        
        # This is just the basic dungeon tile. It holds a shape.
        class dungeon_tile:
            _shape = ''
         
            def __init__(self, shape):
                self._shape = shape
         
            def get_shape(self):
                return self._shape
         
            def set_shape(self, shape):
                self._shape = shape
         
        # Our randomly generated dungeon
        class dungeon:
            _map_size = (0, 0)
            _tiles = []
         
            # max_features - how many rooms/corridors will be generated at the most
            # room_chance - the % chance that the generated feature will be a room
            def __init__(self, map_size_x, map_size_y, max_features, room_chance, level):
                
                self.level = level
                
                # seed the psuedo-random number generator
#                random.seed()
         
                # set the map size
                self._map_size = (map_size_x, map_size_y)
         
                # fill the map with blank tiles
                for x in range (0, self._map_size[0]):
                    self._tiles.append([])
                    for dummyy in range (0,  self._map_size[1]):
                        self._tiles[x].append(dungeon_tile(''))
         
                current_features = 1
                self._make_room(self._map_size[0]/2, self._map_size[1]/2, 5, 5, random.randint(0, 3))
         
                for dummyi in range (0, 1000):
                    if current_features == max_features: break
         
                    newx = 0
                    xmod = 0
                    newy = 0
                    ymod = 0
                    direction = -1
         
                    for dummyj in range (0, 1000):
                        newx = random.randint(1, self._map_size[0]-2)
                        newy = random.randint(1, self._map_size[1]-2)
                        direction = -1
         
                        shape = self._tiles[newx][newy].get_shape()
         
                        if shape == '#' or shape == 'c':
                            if self._tiles[newx][newy+1].get_shape() == '.' or self._tiles[newx][newy+1].get_shape() == 'c':
                                xmod = 0
                                ymod = -1
                                direction = 0
                            elif self._tiles[newx-1][newy].get_shape() == '.' or self._tiles[newx-1][newy].get_shape() == 'c':
                                xmod = 1
                                ymod = 0
                                direction = 1
                            elif self._tiles[newx][newy-1].get_shape() == '.' or self._tiles[newx][newy-1].get_shape() == 'c':
                                xmod = 0
                                ymod = 1
                                direction = 2
                            elif self._tiles[newx+1][newy].get_shape() == '.' or self._tiles[newx+1][newy].get_shape() == 'c':
                                xmod = -1
                                ymod = 0
                                direction = 3
         
                            if direction > -1: break
         
                    if direction > -1:
                        feature = random.randint(0, 100)
         
                        if feature <= room_chance:
                            if self._make_room(newx+xmod, newy+ymod, 10, 10, direction):
                                current_features += 1
                                self._tiles[newx][newy].set_shape('+')
                                self._tiles[newx+xmod][newy+ymod].set_shape('.')
                        elif feature > room_chance:
                            if self._make_corridor(newx+xmod, newy+ymod, 6, direction):
                                current_features += 1
                                self._tiles[newx][newy].set_shape('+')
         
            # this makes a corridor at x,y in a direction
            def _make_corridor(self, x, y, length, direction):
                leng = random.randint(2, length)
         
                direc = 0
                if direction > 0 and direction < 4: direc = direction
         
                if direc == 0:
                    if x < 0 or x > self._map_size[0]-1: return False
         
                    for i in range (y, y-leng, -1):
                        if i < 0 or i > self._map_size[1]-1: return False
                        if self._tiles[x][i].get_shape() != '':return False
         
                    for i in range (y, y-leng, -1):
                        self._tiles[x][i].set_shape('c')
                elif direc == 1:
                    if y < 0 or y > self._map_size[1]-1: return False
         
                    for i in range (x, x+leng):
                        if i < 0 or i > self._map_size[1]-1: return False
                        if self._tiles[i][y].get_shape() != '': return False
         
                    for i in range (x, x+leng):
                        self._tiles[i][y].set_shape('c')
                elif direc == 2:
                    if x < 0 or x > self._map_size[0]-1: return False
         
                    for i in range (y, y+leng):
                        if i < 0 or i > self._map_size[1]-1: return False
                        if self._tiles[x][i].get_shape() != '': return False
         
                    for i in range (y, y+leng):
                        self._tiles[x][i].set_shape('c')
                elif direc == 3:
                    if y < 0 or y > self._map_size[1]-1: return False
         
                    for i in range (x, x-leng, -1):
                        if i < 0 or i > self._map_size[1]-1: return False
                        if self._tiles[i][y].get_shape() != '': return False
         
                    for i in range (x, x-leng, -1):
                        self._tiles[i][y].set_shape('c')
         
                return True
         
            # this makes a room at x,y with the width,height and in a direction
            def _make_room(self, x, y, width, height, direction):
                rand_width = random.randint(4, width)
                rand_height = random.randint(4, height)
                
                # boundary checking, thanks
                rand_width = min(rand_width, C.MAP_WIDTH - x - 1 - C.DUNGEON_MARGIN)
                rand_height = min(rand_height, C.MAP_HEIGHT - y - 1 - C.DUNGEON_MARGIN)
                
         
                direc = 0
                if direction > 0 and direction < 4: direc = direction
         
                if direc == 0:
                    for i in range (y, y-rand_height, -1):
                        if i < 0 or i > self._map_size[1]-1: return False
                        for j in range (x-rand_width/2, (x+(rand_width+1)/2)):
                            if j < 0 or j > self._map_size[0]-1: return False
                            if self._tiles[j][i].get_shape() != '': return False
         
                    for i in range (y, y-rand_height, -1):
                        for j in range (x-rand_width/2, (x+(rand_width+1)/2)):
                            if j == x-rand_width/2: self._tiles[j][i].set_shape('#')
                            elif j == x+(rand_width-1)/2: self._tiles[j][i].set_shape('#')
                            elif i == y: self._tiles[j][i].set_shape('#')
                            elif i == y-rand_height+1: self._tiles[j][i].set_shape('#')
                            else: self._tiles[j][i].set_shape('.')
                elif direc == 1:
                    for i in range (y-rand_height/2, y+(rand_height+1)/2):
                        if i < 0 or i > self._map_size[1]-1: return False
                        for j in range (x, x+rand_width):
                            if j < 0 or j > self._map_size[0]-1: return False
                            if self._tiles[j][i].get_shape() != '': return False
         
                    for i in range (y-rand_height/2, y+(rand_height+1)/2):
                        for j in range (x, x+rand_width):
                            if j == x: self._tiles[j][i].set_shape('#')
                            elif j == x+(rand_width-1): self._tiles[j][i].set_shape('#')
                            elif i == y-rand_height/2: self._tiles[j][i].set_shape('#')
                            elif i == y+(rand_height-1)/2: self._tiles[j][i].set_shape('#')
                            else: self._tiles[j][i].set_shape('.')
                elif direc == 2:
                    for i in range (y, y+rand_height):
                        if i < 0 or i > self._map_size[1]-1: return False
                        for j in range (x-rand_width/2, x+(rand_width+1)/2):
                            if j < 0 or j > self._map_size[0]-1: return False
                            if self._tiles[j][i].get_shape() != '': return False
         
                    for i in range (y, y+rand_height):
                        for j in range (x-rand_width/2, x+(rand_width+1)/2):
                            if j == x-rand_width/2: self._tiles[j][i].set_shape('#')
                            elif j == x+(rand_width-1)/2: self._tiles[j][i].set_shape('#')
                            elif i == y: self._tiles[j][i].set_shape('#')
                            elif i == y+(rand_height-1): self._tiles[j][i].set_shape('#')
                            else: self._tiles[j][i].set_shape('.')
                elif direc == 3:
                    for i in range (y-rand_height/2, y+(rand_height+1)/2):
                        if i < 0 or i > self._map_size[1]-1: return False
                        for j in range (x, x-rand_width, -1):
                            if j < 0 or j > self._map_size[0]-1: return False
                            if self._tiles[j][i].get_shape() != '': return False
         
                    for i in range (y-rand_height/2, y+(rand_height+1)/2):
                        for j in range (x, x-rand_width-1, -1):
                            if j == x: self._tiles[j][i].set_shape('#')
                            elif j == x-rand_width: self._tiles[j][i].set_shape('#')
                            elif i == y-rand_height/2: self._tiles[j][i].set_shape('#')
                            elif i == y+(rand_height-1)/2: self._tiles[j][i].set_shape('#')
                            else: self._tiles[j][i].set_shape('.')
                            
                # Register this room object
                
                newRoom = R.Room(x=x, y=y, width=rand_width, height=rand_height)
                newRoom.setLevel(self.level)
         
                return True
        
            def addTiles(self, level):
                
                for x in range (0, self._map_size[0]):
                    for y in range (0, self._map_size[1]):
                        dtile = self._tiles[x][y]
                        shape = dtile.get_shape()
                        
                        if shape == '.':
                            newTile = self.level.defaultFloorType(x, y)
                            
                        elif shape == '#':
                            newTile = self.level.defaultWallType(x, y)
                            
                        elif shape == 'c':
                            newTile = self.level.defaultTunnelFloorType(x, y)
                            
                        elif shape == '':
                            newTile = self.level.defaultTunnelWallType(x, y)
                            
                        elif shape == '+':
                            newTile = self.level.defaultFloorType(x, y)
#                            door = F.Door(tile = newTile)
#                            newTile.setFeature(door)
                            
                            
                        else:
                            print "Bad tile type:'", shape, "'"
                
                        self.level.tiles.append(newTile)
                        self.level.hasTile[x][y] = True
                
        
        d = dungeon(C.MAP_WIDTH, C.MAP_HEIGHT, C.MAX_ROOMS_AND_CORRIDORS, C.ROOM_CHANCE, self)
        d.addTiles(self)
        
        print "Building tile array"    
        self.buildTileArray()    
        
        # Place Stairs
        print "Placing stairs"
        self.placeStairs()
        
        # Place items
        print "Placing items"
        self.placeItems()
        
        print "Saving open tiles"
        db.saveDB.save(self)
        
        print "Setting up FOV"
        self.computeFOVProperties()
        
        
        
        
        

    def fillInSpaces(self):
        # Fill in empty spaces with wall tiles
        for x in range(C.MAP_WIDTH):
            for y in range(C.MAP_HEIGHT):

                hasTile = self.hasTile[x][y]
#                tiles = self.getTileFromDB(x, y, self)
                
                if not hasTile:
#                if (len(tiles) == 0):
                    newTile = self.defaultTunnelWallType(x, y, room = None)
                    self.tiles.append(newTile)
                    self.hasTile[x][y] = True
                    

    def placeItems(self):
        
        for room in self.rooms:
            # Just place one random item for now
            tile = self.getRandomOpenTileInRoom(room)
            if tile:
                item = I.getRandomItem()
                tile.addObject(item)

                                               
    # Create a room
    def createRoom(self, room):
        
        for x in range(room.getX1(), room.getX2()):
            for y in range(room.getY1(), room.getY2()):
#                print "Creating tile at", x, ",", y
                newTile = self.defaultFloorType(x=x, y=y, room = room)
                self.tiles.append(newTile)
                self.hasTile[x][y] = True
                self.hasTile[x][y]
        
#        for x in range(room.getX1(), room.getX2()):
#            for y in range(room.getY1(), room.getY2()):
#                newTile = self.defaultFloorType(x = x, y = y)
#                self.hasTile[x][y] = newTile
#                room.tiles.append(newTile)
        
#        room.fillWithTiles()
#        
#        for tile in room.getTiles():
#            x = tile.x
#            y = tile.y
#            self.addTile(tile)
#            self.hasTile[x][y] = tile
#        print "Room created with", len(room.getTiles()), "tiles"

    def addTile(self, tile):
        print "add (", tile.x, ",", tile.y, ")"
        
#        try:
#            oldTileCol = self.hasTile[tile.x]
#            oldTile = oldTileCol[tile.y]
#            if oldTile:
#                self.tiles.remove(oldTile)
##                print "removed a tile"
#        except IndexError:
#            pass
        
        self.tiles.append(tile)
        self.hasTile[tile.x][tile.y] = True

    def createHTunnel(self, prevRoom, newRoom, x1, x2, y, placeDoorAtStart = False, placeDoorAtEnd = False):
        
        for x in range(min(x1, x2), max(x1, x2)):
            skip = False
            tilesHere = self.hasTile[x][y]
            if tilesHere:
                skip = True
            
            if not skip:
#                newTunnelTile = self.defaultTunnelFloorType(x = x, y = y, level = self, room = None)
                newTunnelTile = self.defaultTunnelFloorType(x = x, y = y, room = None)
                
                if placeDoorAtStart and x == min(x1, x2):
                    door = F.Door(tile = newTunnelTile)
                    newTunnelTile.setFeature(door)
                    
                if placeDoorAtEnd and x == max(x1, x2):
                    door = F.Door(tile = newTunnelTile)
                    newTunnelTile.setFeature(door)
                    
                self.tiles.append(newTunnelTile)
                self.hasTile[x][y] = True
#                self.hasTile[x][y] = newTunnelTile
#                self.addTile(newTunnelTile)

    def createVTunnel(self, prevRoom, newRoom, x, y1, y2, placeDoorAtStart = False, placeDoorAtEnd = False):
        
        for y in range(min(y1, y2), max(y1, y2)):
            skip = False
            tilesHere = self.hasTile[x][y]
            if tilesHere:
                skip = True

            if not skip:
#                newTunnelTile = self.defaultTunnelFloorType(x = x, y = y, level = self, room = None)
                newTunnelTile = self.defaultTunnelFloorType(x = x, y = y, room = None)
                
                if placeDoorAtStart and y == min(y1, y2):
                    door = F.Door(tile = newTunnelTile)
                    newTunnelTile.setFeature(door)
                    
                if placeDoorAtEnd and y == max(y1, y2):
                    door = F.Door(tile = newTunnelTile)
                    newTunnelTile.setFeature(door)
                    
                self.tiles.append(newTunnelTile)
                self.hasTile[x][y] = True
                self.hasTile[x][y]
#                self.hasTile[x][y] = newTunnelTile
#                self.addTile(newTunnelTile)

    # Carve out a tunnel
    def createTunnel(self, prevRoom, newRoom):
        
        x1, y1 = prevRoom.getCenter()
        x2, y2 = newRoom.getCenter()
        
        if random.randint(0, 1) == 1:
            # Horizontal first
            
            # Place doors?
            placeDoorAtStart = False
            if random.randint(0, 1) == 1:
                placeDoorAtStart = True
            
            placeDoorAtEnd = False
            if random.randint(0, 1) == 1:
                placeDoorAtEnd = True
            
            self.createHTunnel(prevRoom, newRoom, x1, x2, min(y1, y2), placeDoorAtStart = placeDoorAtStart)
            self.createVTunnel(prevRoom, newRoom, max(x1, x2), y1, y2, placeDoorAtEnd = placeDoorAtEnd)
            
                
        else:
            #Vertical first
            
            # Place doors?
            placeDoorAtStart = False
            if random.randint(0, 1) == 1:
                placeDoorAtStart = True
            
            placeDoorAtEnd = False
            if random.randint(0, 1) == 1:
                placeDoorAtEnd = True
                
            self.createVTunnel(prevRoom, newRoom, min(x1, x2), y1, y2, placeDoorAtStart = placeDoorAtStart)
            self.createHTunnel(prevRoom, newRoom, x1, x2, max(y1, y2), placeDoorAtEnd = placeDoorAtEnd)
            

    def placeStairs(self):
        
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
                
                # Set destination
            
                downStair = F.downStair()
                downTile.setFeature(downStair)
                
                # Set destination
                
                break

    
#    def passTime(self, turns = 1):
#        print "tick"
#        
#        for i in range(turns):
#            creatures = []
#            
#            for x in range(self.WIDTH):
#                for y in range(self.HEIGHT):
#                    coords = Coordinates(x = x, y = y)
#                    
#                    tile = self.getTile(coords)
#                    tile.passTime()
#                    cr = tile.creature
#                    
#                    if cr is not None:
#                        creatures.append(cr)
#                        
#            for cr in creatures:
#                cr.passTime()
    
    
#    def placeCreature(self, creature):
#        while True:
#            coords = self.getRandOpenSpace() 
#            tile = self.getTile(coords)
#            
#            if not tile.creature:
#                tile.addCreature(creature)
#                creature.setPosition(self, coords)
#                break
#            
#    def placeCreatures(self, num_creatures):
#        for i in range(num_creatures):
#            self.placeCreature(randomCreature(self))
#
#    def getRandOpenSpace(self):
#        '''Get a random open square on the map'''
#        while True:
#            randx = libtcod.random_get_int(0, 0, self.WIDTH - 1)
#            randy = libtcod.random_get_int(0, 0, self.HEIGHT - 1)
#        
#            if not self.isWalkable(randx, randy):
#                return Coordinates(x = randx, y = randy)
#                
#    def getRandOpenSpace_NEW(self):
#        '''Get the coordinates of a random open square on the map'''
#        if self.openSpaces:
#            randOpenTile = random.choice(self.openSpaces)
#            return Coordinates(x = randOpenTile.x, y = randOpenTile.y)
#        
#        else:
#            return None, None


                

                
#####################################################
#
# Old functions!
#
#####################################################

#def target_tile(max_range=None):
#    #return the position of a tile left-clicked in player's FOV (optionally in a range), or (None,None) if right-clicked.
#    while True:
#        #render the screen. this erases the inventory and shows the names of objects under the mouse.
#        render_all()
#        libtcod.console_flush()
# 
#        key = libtcod.console_check_for_keypress()
#        mouse = libtcod.mouse_get_status()  #get mouse position and click status
#        (x, y) = (mouse.cx, mouse.cy)
# 
#        #accept the target if the player clicked in FOV, and in case a range is specified, if it's in that range
#        if (mouse.lbutton_pressed and libtcod.map_is_in_fov(FOVMap, x, y) and
#            (max_range is None or player.distance(x, y) <= max_range)):
#            return (x, y)
#                    
#        if mouse.rbutton_pressed or key.vk == libtcod.KEY_ESCAPE:
#            return (None, None)  #cancel if the player right-clicked or pressed Escape
#        
#def target_monster(max_range=None):
#    #returns a clicked monster inside FOV up to a range, or None if right-clicked
#    while True:
#        (x, y) = target_tile(max_range)
#        if x is None:  #player cancelled
#            return None
# 
#        #return the first clicked monster, otherwise continue looping
#        for obj in objects:
#            if obj.x == x and obj.y == y and obj.fighter and obj != player:
#                return obj        
#        
#
