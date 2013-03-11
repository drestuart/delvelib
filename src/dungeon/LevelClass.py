###############################################################
#
# OLD STUFF
#
###############################################################

# The map class.  This will contain the code for creating and displaying maps.
# The plan is to have two maps: the *actual* level map, and the player's map
# showing what they know/remember about the level.

from Import import *
import RoomClass as R
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Integer, Boolean
import Const as C
import TileClass as T
import colors
import copy
import database as db
import os
import random


#from CreatureClass import *

libtcod = importLibtcod()

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
        
        self.tiles = []
        self.rooms = []
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    depth = Column(Integer)
    
    nextLevel = relationship("Level", uselist=False, primaryjoin="Level.id==Level.nextLevelId")
    nextLevelId = Column(Integer, ForeignKey("levels.id"))
    
    previousLevel = relationship("Level", uselist=False, primaryjoin="Level.id==Level.previousLevelId")
    previousLevelId = Column(Integer, ForeignKey("levels.id"))
    
    tiles = relationship("Tile", backref=backref("level", uselist=False), primaryjoin="Level.id==Tile.levelId")
    rooms = relationship("Room", backref=backref("level", uselist=False), primaryjoin="Level.id==Room.levelId")
    
    levelType = Column(String)
    
    __mapper_args__ = {'polymorphic_on': levelType,
                       'polymorphic_identity': 'level'}
    

    def recomputeFOV(self):
        self.__dict__['toRecomputeFOV'] = True
    
    def recomputedFOV(self):
        self.__dict__['toRecomputeFOV'] = False
        
        
#    def getTile(self, coords):
#        # Return a tile by coordinates, with a Coordinates object.
#        x, y = coords['x'], coords['y']
#        return self.tiles[x][y]
    
#    def setTile(self, coords, tile):
#        x, y = coords['x'], coords['y']
#        self.__dict__['tiles'][x][y] = tile
#        if not tile.blocksMove():
#            self.__dict__['openSpaces'].append(tile)
#        



    # Test if a square is blocked
#    def isBlocked(self, x, y):
#        coords = Coordinates(x = x, y = y)
#        return self.getTile(coords).blocksMove()
#    
#    def blocksMove(self, x, y):
#        return self.isBlocked(x, y)
#    
#    def blocksSight(self, x, y):
#        coords = Coordinates(x = x, y = y)
#        return self.getTile(coords).blocksSight()



                
    # Draw that map!
    def draw(self, con):
#        libtcod.console_set_foreground_color(con, self.color())
#        libtcod.console_put_char(con, self.x, self.y, self.symbol(), self.background())

        for x in range(self.WIDTH):
            for y in range(self.HEIGHT):
                #try:
                    coords = Coordinates(x = x, y = y)
                    symbol, color, background = self.getTile(coords).toDraw()
                    libtcod.console_set_foreground_color(con, color)
                    libtcod.console_put_char(con, x, y, symbol, background)
                #except:
                #    print symbol, color, background
                    
                    
    # Erase that map!
    def clear(self, con):
        for x in range(self.WIDTH):
            for y in range(self.HEIGHT):
                libtcod.console_put_char(con, x, y, ' ', libtcod.BKGND_NONE)
                
            
    def getSpacesInRadius(self, radius, centerCoords):
        '''Returns a list of all the coordinates at a distance <= *radius* from the given getCenter space.  Simply calls getSpacesAtRadius for 1 to *radius*.'''
        
        assert radius >= 0 and radius == int(radius) #Do better error checking here.
        
        coordList = [centerCoords]
        
        for i in range(radius):
            coordList += self.getSpacesAtRadius(i + 1, centerCoords)
    
    def getSpacesAtRadius(self, radius, centerCoords):
        '''Returns a list of all the coordinates at a distance of exactly *radius* from the given getCenter space.  There is probably a much better way to do this algorithm.'''
               
        assert radius > 0 and radius == int(radius) #Do better error checking here.
        
        # The plan here is to encode the directions to each square as a string
        # with u, l, r, and d for up, left, etc.  Fortunately each set of
        # directions can only have one of u/d and one of l/r.  So, to exhaust
        # all possible strings, I will start with a string of radius*u.
        baseDirString = 'u'*radius
        
        # I will store all of the direction strings in the directions list, and
        # then convert them into resulting coordinates in the coordsList.  The
        # baseDirections list will hold only the u/l directions, and I will use
        # it to generate the rest of the strings by replacing u->d, l->r, and
        # both.  So, e.g., 'ul' -> ['dl', 'ur', 'dr'], and those all go in the
        # directions list.
        directions = [baseDirString]
        baseDirections = [baseDirString]
        coordList = []
        
        for i in range(radius):
            newString = baseDirString.replace('u', 'l', 1)
            baseDirections.append(newString)
            
            if newString not in directions:
                directions.append(newString)
            
            
        # baseDirections now holds all possible direction strings of length
        # radius composed of u's and l's, up to reordering, which does nothing.
        # We will now set about converting those to the other directions as
        # well.
        
        # u->d
        for direction in baseDirections:
            newString = direction.replace('u', 'd')
            if newString not in directions:
                directions.append(newString)
        
        # l->r
        for direction in baseDirections:
            newString = direction.replace('l', 'r')
            if newString not in directions:
                directions.append(newString)
        
        
        # u->d, l->r
        for direction in baseDirections:
            newString = direction.replace('u', 'd')
            newString = direction.replace('l', 'r')
            if newString not in directions:
                directions.append(newString)
        
        #Now, convert these directions into coordinates from the getCenter coordinates provided.

        # The coordinates to add based on the direction
        dif = {'u':Coordinates(x = 0, y = 1), 'd':Coordinates(x = 0, y = -1),
               'l':Coordinates(x = -1, y = 0), 'r':Coordinates(x = 1, y = 0)}
        
        for dirString in directions:
            
            newCoords = centerCoords
            
            # Read out the direction instructions one at a time
            for letter in dirString:
                #Move the coordinates by a given amount 
                newCoords += dif[letter]
                
            # Add to the list of new coords.  They should be unique, but it's good to check.
            if newCoords not in coordList:
                coordList.append(newCoords)
                
        return coordList
            
            
            
class DungeonLevel(Level):
    '''A Level subclass for modeling one dungeon level.  Includes functionality for passing time and level construction.'''
    
    __mapper_args__ = {'polymorphic_identity': 'dungeon level'}

    
    def __init__(self, **kwargs):
        super(DungeonLevel, self).__init__(**kwargs)
    
    def createRooms(self):
        '''Add some rooms to the level'''
        rooms = []
        num_rooms = 0
     
        # Make some rooms
        for dummy in range(C.MAX_ROOMS):
            #random width and height
#            w = libtcod.random_get_int(0, C.ROOM_MIN_SIZE, C.ROOM_MAX_SIZE)
#            h = libtcod.random_get_int(0, C.ROOM_MIN_SIZE, C.ROOM_MAX_SIZE)
            
            w = random.randint(C.ROOM_MIN_SIZE, C.ROOM_MAX_SIZE)
            h = random.randint(C.ROOM_MIN_SIZE, C.ROOM_MAX_SIZE)
    
            #random position without going out of the boundaries of the map
#            x = libtcod.random_get_int(0, 0, self.WIDTH - w - 1)
#            y = libtcod.random_get_int(0, 0, self.HEIGHT - h - 1)
            
            x = random.randint(0, C.MAP_WIDTH - w - 1)
            y = random.randint(0, C.MAP_HEIGHT - h - 1)
    
            newRoom = R.Room(x = x, y = y, width = w, height = h, level = self,
                             defaultFloorType = self.defaultFloorType, defaultWallType = self.defaultWallType)
     
            #run through the other rooms and see if they intersect with this one
            failed = False
            for otherRoom in rooms:
                if newRoom.intersect(otherRoom):
#                    print "Room intersection detected"
                    failed = True
                    break
    
            if not failed:
#                print "No room intersection detected"
                #this means there are no intersections, so this room is valid
                #"paint" it to the map's tiles
                self.createRoom(newRoom)
    
                #add some contents to this room, such as monsters
#                self.placeObjects(newRoom)
     
                if num_rooms >= 1:
                    #all rooms after the first:
                    #connect it to the previous room with a tunnel
                    prevRoom = self.rooms[-1]
                    
                    self.createTunnel(prevRoom, newRoom)
    
     
                # Append the new room to the list
                rooms.append(newRoom)
                self.rooms.append(newRoom)
                num_rooms += 1

            # Place upstair and downstair
            self.placeStairs()
            
        # Save tiles
#        print "saving", len(self.tiles), "tiles"
        db.saveDB.saveAll(self.tiles)
        db.saveDB.saveAll(self.rooms)

                                               
    # Create a room
    def createRoom(self, room):
        
        room.fillWithTiles()
        self.tiles += room.getTiles()
#        print "Room created with", len(room.getTiles()), "tiles"

    # Carve out a tunnel
    def createTunnel(self, prevRoom, newRoom):
        
        x1, y1 = prevRoom.getCenter()
        x2, y2 = newRoom.getCenter()
        
        if random.randint(0, 1) == 1:
            # Horizontal first
            
            for x in range(min(x1, x2), max(x1, x2) + 1):
                
                if newRoom.contains(x, y1) or prevRoom.contains(x, y1):
                    continue
                
                newTunnelTile = self.defaultTunnelFloorType(x = x, y = y1, level = self, room = None)
                self.tiles.append(newTunnelTile)
                
                topWallTile = self.defaultTunnelWallType(x = x, y = y1 + 1, level = self, room = None)
                bottomWallTile = self.defaultTunnelWallType(x = x, y = y1 - 1, level = self, room = None)
                self.tiles.append(topWallTile)
                self.tiles.append(bottomWallTile)
            
            for y in range(min(y1, y2), max(y1, y2) + 1):
                
                if newRoom.contains(x2, y) or prevRoom.contains(x2, y):
                    continue
            
                newTunnelTile = self.defaultTunnelFloorType(x = x2, y = y, level = self, room = None)
                self.tiles.append(newTunnelTile)
                
                leftWallTile = self.defaultTunnelWallType(x = x2 - 1, y = y, level = self, room = None)
                rightWallTile = self.defaultTunnelWallType(x = x2 + 1, y = y, level = self, room = None)
                self.tiles.append(leftWallTile)
                self.tiles.append(rightWallTile)
                
        else:
            #Vertical first
            
            for y in range(min(y1, y2), max(y1, y2) + 1):
                
                if newRoom.contains(x1, y) or prevRoom.contains(x1, y):
                    continue
            
                newTunnelTile = self.defaultTunnelFloorType(x = x1, y = y, level = self, room = None)
                self.tiles.append(newTunnelTile)
                
                leftWallTile = self.defaultTunnelWallType(x = x1 - 1, y = y, level = self, room = None)
                rightWallTile = self.defaultTunnelWallType(x = x1 + 1, y = y, level = self, room = None)
                self.tiles.append(leftWallTile)
                self.tiles.append(rightWallTile)
                
            for x in range(min(x1, x2), max(x1, x2) + 1):
                
                if newRoom.contains(x, y2) or prevRoom.contains(x, y2):
                    continue
                
                newTunnelTile = self.defaultTunnelFloorType(x = x, y = y2, level = self, room = None)
                self.tiles.append(newTunnelTile)
                
                topWallTile = self.defaultTunnelWallType(x = x, y = y2 + 1, level = self, room = None)
                bottomWallTile = self.defaultTunnelWallType(x = x, y = y2 - 1, level = self, room = None)
                self.tiles.append(topWallTile)
                self.tiles.append(bottomWallTile)

    def placeStairs(self):
        pass

    # Carve out a horizontal tunnel
    def createHTunnelOld(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            
            newTunnelTile = self.defaultTunnelFloorType(x = x, y = y, level = self, room = None)
            self.tiles.append(newTunnelTile)
            
            topWallTile = self.defaultTunnelWallType(x = x, y = y + 1, level = self, room = None)
            bottomWallTile = self.defaultTunnelWallType(x = x, y = y - 1, level = self, room = None)
            self.tiles.append(topWallTile)
            self.tiles.append(bottomWallTile)
            

    # Carve out a vertical tunnel
    def createVTunnelOld(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            
            newTunnelTile = self.defaultTunnelFloorType(x = x, y = y, level = self, room = None)
            self.tiles.append(newTunnelTile)
            
            leftWallTile = self.defaultTunnelWallType(x = x - 1, y = y, level = self, room = None)
            rightWallTile = self.defaultTunnelWallType(x = x + 1, y = y, level = self, room = None)
            self.tiles.append(leftWallTile)
            self.tiles.append(rightWallTile)
    
    
    def passTime(self, turns = 1):
        print "tick"
        
        for i in range(turns):
            creatures = []
            
            for x in range(self.WIDTH):
                for y in range(self.HEIGHT):
                    coords = Coordinates(x = x, y = y)
                    
                    tile = self.getTile(coords)
                    tile.passTime()
                    cr = tile.creature
                    
                    if cr is not None:
                        creatures.append(cr)
                        
            for cr in creatures:
                cr.passTime()
    
    
    def placeCreature(self, creature):
        while True:
            coords = self.getRandOpenSpace() 
            tile = self.getTile(coords)
            
            if not tile.creature:
                tile.addCreature(creature)
                creature.setPosition(self, coords)
                break
            
    def placeCreatures(self, num_creatures):
        for i in range(num_creatures):
            self.placeCreature(randomCreature(self))

    def getRandOpenSpace(self):
        '''Get a random open square on the map'''
        while True:
            randx = libtcod.random_get_int(0, 0, self.WIDTH - 1)
            randy = libtcod.random_get_int(0, 0, self.HEIGHT - 1)
        
            if not self.isBlocked(randx, randy):
                return Coordinates(x = randx, y = randy)
                
    def getRandOpenSpace_NEW(self):
        '''Get the coordinates of a random open square on the map'''
        if self.openSpaces:
            randOpenTile = random.choice(self.openSpaces)
            return Coordinates(x = randOpenTile.x, y = randOpenTile.y)
        
        else:
            return None, None

class FOVMap():
    '''A map subclass for a creature's Field of View.  Keeps track of what the creature can see, and only updates squares that can be seen.  Reads from its corresponding DungeonLevel object.'''


    def __init__(self, baseMap):
        #super(FOVMap, self).__init__(width, height, name, depth)
        self.__dict__['baseMap'] = baseMap
        self.__dict__['toRecompute'] = True
        
        # Initialize the fov_map object for libtcod
        self.__dict__['fov_map'] = libtcod.map_new(C.MAP_WIDTH, C.MAP_HEIGHT)
        
        self.__dict__['tiles'] = [[ None 
                                    for y in range(self.baseMap.HEIGHT) ]
                                    for x in range(self.baseMap.WIDTH) ]
        
        self.computeFOVProperties()
        
    def getTile(self, coords):
        # Return a tile by coordinates, with a Coordinates object.
        x, y = coords['x'], coords['y']
        return self.tiles[x][y]
    
    def setTile(self, coords, tileIn):
        self.__dict__['tiles'][coords['x']][coords['y']] = copy.deepcopy(tileIn)
        
    def computeFOVProperties(self):
        for y in range(self.baseMap.HEIGHT):
            for x in range(self.baseMap.WIDTH):
                libtcod.map_set_properties(self.fov_map, x, y, 
                                           not self.baseMap.blocksMove(x, y), 
                                           not self.baseMap.blocksSight(x, y))
        
        
    def recompute(self):
        self.__dict__['toRecompute'] = True
        
    def recomputed(self):
        self.__dict__['toRecompute'] = False
                
    def computeFOV(self, position, radius):
        '''Compute the field of view of this map with respect to a particular position'''
        if self.toRecompute == False and self.baseMap.toRecomputeFOV == False:
            return
        else:
            
            self.__dict__['toRecompute'] = False
            
            libtcod.map_compute_fov(self.fov_map, position['x'], position['y'], 
                                radius, C.FOV_LIGHT_WALLS, C.FOV_ALGO)

            self.computeFOVProperties()
            
            self.recomputed()
            self.baseMap.recomputedFOV()
        
    def clear(self, con):
        self.baseMap.clear(con)
        
    def draw(self, con, position, radius):
        self.computeFOV(position, radius)
        
        for x in range(self.baseMap.WIDTH):
            for y in range(self.baseMap.HEIGHT):
                coords = Coordinates(x = x, y = y)
                tile = self.baseMap.getTile(coords)
                
                if libtcod.map_is_in_fov(self.fov_map, x, y):  # We can see this tile
                    symbol, color, background = tile.toDraw()
                    self.setTile(coords, tile)  # Remember this tile
                
                elif self.getTile(coords):  # We've seen this one before
                    symbol = self.getTile(coords).symbol()
                    color = libtcod.dark_grey
                    background = libtcod.light_grey
                        
                else:
                    background = libtcod.BKGND_NONE
                    color = colors.colorDarkGround
                    symbol = ' '
                    
                libtcod.console_set_foreground_color(con, color)
                libtcod.console_put_char(con, x, y, symbol, background)
                

                
#def main():
#    SCREEN_WIDTH = 80
#    SCREEN_HEIGHT = 69
#    
#    libtcod.console_set_custom_font(os.path.join('../fonts', 'arial10x10.png'), 
#                                libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
#    libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'delveRL', False)
#    libtcod.sys_set_fps(20)
#    con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
#
#    map = Level(40, 40)
#    lmap = DungeonLevel(40, 50)
#    fovmap = FOVMap(lmap)
#    coords = fovmap.baseMap.getRandOpenSpace()
#    
#    while not libtcod.console_is_window_closed():
# 
#        fovmap.draw(con, coords, 5)
#        libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
#        libtcod.console_flush()
#        fovmap.clear(con)
#        
#        
#    print "Win"
#
#if __name__ == '__main__':
#        main()
                
                
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
#        if (mouse.lbutton_pressed and libtcod.map_is_in_fov(fov_map, x, y) and
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
#def closest_monster(max_range):
#    #find closest enemy, up to a maximum range, and in the player's FOV
#    closest_enemy = None
#    closest_dist = max_range + 1  #start with (slightly more than) maximum range
# 
#    for object in objects:
#        if (object.fighter and not object == player 
#            and libtcod.map_is_in_fov(fov_map, object.x, object.y)):
#
#            #calculate distance between this object and the player
#            dist = player.distance_to(object)
#            if dist < closest_dist:  #it's closer, so remember it
#                closest_enemy = object
#                closest_dist = dist
#    return closest_enemy


def main():
    
    db.saveDB.start(True)
    
    d1 = DungeonLevel(name = "Test", depth = 1, defaultFloorType = T.StoneFloor,
                      defaultWallType = T.RockWall, defaultTunnelFloorType = T.RockTunnel, defaultTunnelWallType = T.RockWall)
    d1.createRooms()

    db.saveDB.save(d1)
#    db.saveDB.saveAll(d1.tiles)


if __name__ == '__main__':
    main()
