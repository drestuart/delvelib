import Const as C
import random
import RoomClass as R
import DungeonFeatureClass as F
from randomChoice import weightedChoice

# Some constants
room_width = 7
room_height = 7
road_width = 5
room_road_margin = 1
room_room_margin = 1
bldgs_in_row = 4

# This is just the basic dungeon tile. It holds a shape.
class dungeon_tile:
    _shape = ''
 
    def __init__(self, shape):
        self._shape = shape
 
    def get_shape(self):
        return self._shape
 
    def set_shape(self, shape):
        self._shape = shape
        
class town_cell(object):
    cell_width = C.TOWN_CELL_WIDTH
    cell_height = C.TOWN_CELL_HEIGHT
    
    def __init__(self, town, cellx, celly, celltype):
        self.town = town
        self.cellx, self.celly = cellx, celly
        self.celltype = celltype
        
        self.xoffset = self.cellx*self.cell_width
        self.yoffset = self.celly*self.cell_height
        
        self.roadx = (self.cell_width - road_width)/2 + self.xoffset   # For a N-S road
        self.roady = (self.cell_height - road_width)/2 + self.yoffset  # For an E-W road
    
    def buildSpecialBuildings(self):
        pass
        
    def buildRoads(self):
        # Lay road
        if self.celltype == 'horz_road':
            self.town.makeHorzRoad(self.roady, road_width)
        elif self.celltype == 'vert_road':
            self.town.makeVertRoad(self.roadx, road_width)
        else:
            pass
    
    def buildBuildings(self):
        if self.celltype == 'horz_road':
            bldgx = 4 + self.xoffset
            bldgy = self.roady - room_road_margin - room_height
            
            # Lay first row of buildings
            for i in range(bldgs_in_row):
                self.town.makeBldg(bldgx, bldgy, room_width, room_height, 'south')
                bldgx += room_width + room_room_margin
     
            # Lay second row of buildings
            bldgx = 4 + self.xoffset
            bldgy += room_height + road_width + room_road_margin*2
            for i in range(bldgs_in_row):
                self.town.makeBldg(bldgx, bldgy, room_width, room_height, 'north')
                bldgx += room_width + room_room_margin
    
        elif self.celltype == 'vert_road':
            bldgx = self.roadx - room_road_margin - room_width
            bldgy = 4 + self.yoffset
            
            # First column
            for i in range(bldgs_in_row):
                self.town.makeBldg(bldgx, bldgy, room_width, room_height, 'east')
                bldgy += room_height + room_room_margin
            
            # Second column
            bldgx += room_width + road_width + room_road_margin*2
            bldgy = 4 + self.yoffset
            for i in range(bldgs_in_row):
                self.town.makeBldg(bldgx, bldgy, room_width, room_height, 'west')
                bldgy += room_height + room_room_margin
        
 
# Our randomly generated dungeon
class town:
    _map_size = (0, 0)
    _tiles = []
 
    def __init__(self, cellsWide, cellsHigh, level):
        
        self.level = level
        self.rooms = []
 
        self.cellsWide = cellsWide
        self.cellsHigh = cellsHigh
        
        self._map_size = (self.cellsWide*C.TOWN_CELL_WIDTH, self.cellsHigh*C.TOWN_CELL_HEIGHT)
        
        # fill the map with blank tiles
        for x in range (0, self._map_size[0]):
            self._tiles.append([])
            for dummyy in range (0,  self._map_size[1]):
                self._tiles[x].append(dungeon_tile(''))
        
        cells = []
        cellTypeChance = {
                          'horz_road' : 1,
                          'vert_road' : 2
                          }
        
        for i in range(self.cellsWide):
            for j in range(cellsHigh):
                celltype = weightedChoice(cellTypeChance)
                cell = town_cell(self, i, j, celltype)
                cells.append(cell)
                
        random.shuffle(cells)
        
        for cell in cells:
            cell.buildSpecialBuildings()

        for cell in cells:
            cell.buildRoads()
        
        for cell in cells:
            cell.buildBuildings()
 
    def makeBldg(self, x, y, width, height, door_side):
#         rand_width = random.randint(4, width)
#         rand_height = random.randint(4, height)
        room_width = width
        room_height = height
        
        # boundary checking, thanks
        room_width = min(room_width, self._map_size[0] - x - 1 - C.DUNGEON_MARGIN)
        room_height = min(room_height, self._map_size[1] - y - 1 - C.DUNGEON_MARGIN)
        
        # Check that we're not intersecting any other rooms or existing features
        newRoom = R.Room(x=x, y=y, width=room_width, height=room_height)
        
        for room in self.rooms:
            if room.intersect(newRoom):
                del newRoom
                return False
        
        for i in range(y, y + room_height):
            if i < 0 or i > self._map_size[1]-1: return False
            for j in range(x, x + room_width):
                if j < 0 or j > self._map_size[0]-1: return False
                if self._tiles[j][i].get_shape() != '': return False
        
        
        # It's valid, so register this room object
        newRoom.setLevel(self.level)
        
        # Lay down walls and floors
        for i in range(y, y + room_height):
            for j in range(x, x + room_width):
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
                if self._tiles[j][i].get_shape() != '': continue
                self._tiles[j][i].set_shape('~')
        return True
    
    # TODO
    def makeVertRoad(self, x, roadWidth):
        
        for j in range(x, x + roadWidth):
            for i in range(self._map_size[1]):
                if self._tiles[j][i].get_shape() != '': continue
                self._tiles[j][i].set_shape('~')
        return True

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
                

