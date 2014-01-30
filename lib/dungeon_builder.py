'''
Adapted from the dungeon building algorithm by Zack Hovatter (http://roguebasin.roguelikedevelopment.org/index.php?title=User:Zackhovatter)

Available at: http://roguebasin.roguelikedevelopment.org/index.php?title=Python_Curses_Example_of_Dungeon-Building_Algorithm

'''

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
        rand_width = min(rand_width, self._map_size[0] - x - 1 - C.DUNGEON_MARGIN)
        rand_height = min(rand_height, self._map_size[1] - y - 1 - C.DUNGEON_MARGIN)
        
 
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
                    door = F.Door(tile = newTile)
                    newTile.setFeature(door)
                    
                    
                else:
                    print "Bad tile type:'", shape, "'"
        
                self.level.tiles.append(newTile)
                self.level.hasTile[x][y] = True
