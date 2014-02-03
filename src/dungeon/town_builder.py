import Const as C
import random
import RoomClass as R
import DungeonFeatureClass as F

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
class town:
    _map_size = (0, 0)
    _tiles = []
 
    def __init__(self, map_size_x, map_size_y, level):
        
        self.level = level
        self.rooms = []
        
        # Some constants
        room_width = 7
        room_height = 5
        road_width = 3
        room_road_margin = 1
        room_room_margin = 1
 
        # set the map size
        self._map_size = (map_size_x, map_size_y)
 
        # fill the map with blank tiles
        for x in range (0, self._map_size[0]):
            self._tiles.append([])
            for dummyy in range (0,  self._map_size[1]):
                self._tiles[x].append(dungeon_tile(''))
                
        bldgx = 2
        bldgy = 2
        
        # Lay first row of buildings
        for i in range(5):
            self.makeRoom(bldgx, bldgy, room_width, room_height, 'south')
            bldgx += room_width + room_room_margin
 
        # Lay road
        bldgy += room_height + room_road_margin
        self.makeHorzRoad(bldgy, road_width)
        
        # Lay second row of buildings
        bldgx = 2
        bldgy += road_width + room_road_margin
        for i in range(5):
            self.makeRoom(bldgx, bldgy, room_width, room_height, 'north')
            bldgx += room_width + room_room_margin

 
 
    def makeRoom(self, x, y, width, height, door_side):
#         rand_width = random.randint(4, width)
#         rand_height = random.randint(4, height)
        room_width = width
        room_height = height
        
        # boundary checking, thanks
        room_width = min(room_width, self._map_size[0] - x - 1 - C.DUNGEON_MARGIN)
        room_height = min(room_height, self._map_size[1] - y - 1 - C.DUNGEON_MARGIN)
        
        # Register this room object
        newRoom = R.Room(x=x, y=y, width=room_width, height=room_height)
        newRoom.setLevel(self.level)
        
        for room in self.rooms:
            if room.intersect(newRoom):
                return False
        
        # Lay down walls and floors
        for i in range(y, y + room_height):
            if i < 0 or i > self._map_size[1]-1: return False
            for j in range(x, x + room_width):
                if j < 0 or j > self._map_size[0]-1: return False
                if self._tiles[j][i].get_shape() != '': return False
                if (j == x or j == x + room_width - 1 or i == y or i == y + room_height - 1):
                    self._tiles[j][i].set_shape('#')
                else:
                    self._tiles[j][i].set_shape(',')
                    
        # Add door
        doorx = 0
        doory = 0
        
        if door_side == 'north':
            doorx = (room_width - 1)/2
            doory = 0
        elif door_side == 'south':
            doorx = (room_width - 1)/2
            doory = room_height - 1
        elif door_side == 'east':
            doorx = room_width - 1
            doory = (room_height - 1)/2
        elif door_side == 'west':
            doorx = 0
            doory = (room_height - 1)/2
        
        if not doorx and not doory: return False
        
        self._tiles[x + doorx][y + doory].set_shape('+')
                
        return True
    
    def makeHorzRoad (self, y, roadWidth):
        
        for i in range(y, y + roadWidth):
            for j in range(self._map_size[0]):
                if self._tiles[j][i].get_shape() != '': return False
                self._tiles[j][i].set_shape('~')
        return True
    
    # TODO
    def makeVertRoad(self, x, roadWidth):
        return False

    def addTiles(self, level):
        
        for x in range (0, self._map_size[0]):
            for y in range (0, self._map_size[1]):
                dtile = self._tiles[x][y]
                shape = dtile.get_shape()
                
                if shape in ('.', ''):
                    newTile = self.level.outsideFloorTile(x, y)
                    
                elif shape == '#':
                    newTile = self.level.buildingWallTile(x, y)
                    
                elif shape == ',':
                    newTile = self.level.buildingFloorTile(x, y)
                    
                elif shape == '~':
                    newTile = self.level.roadTile(x, y)
                    
                elif shape in ('+', '_'):
                    newTile = self.level.buildingFloorTile(x, y)
                    door = F.Door(tile = newTile)
                    newTile.setFeature(door)
                    
                else:
                    print "Bad tile type:'", shape, "'"
        
                self.level.tiles.append(newTile)
                self.level.hasTile[x][y] = True
                

