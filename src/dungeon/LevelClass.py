# The map class.  This will contain the code for creating and displaying maps.
# The plan is to have two maps: the *actual* level map, and the player's map
# showing what they know/remember about the level.

from Import import *
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Integer, Boolean
import Const as C
import RoomClass as R
import TileClass as T
import colors
import copy
import database as db
import os
import random
import sqlalchemy.exc


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
    

    def recomputeFOV(self):
        self.__dict__['toRecomputeFOV'] = True
    
    def recomputedFOV(self):
        self.__dict__['toRecomputeFOV'] = False
        
        
    def getTile(self, x, y):
        for tile in self.tiles:
            if tile.x == x and tile.y == y:
                return tile
    
    
    def getTileFromDB(self, x, y, level):
        query = db.saveDB.getQueryObj(T.Tile)
        query.filter(T.Tile.x == x).filter(T.Tile.y == y).filter(T.Tile.level == level)
        return db.saveDB.runQuery(query)
        
    def getMapConsole(self):
        return self.mapConsole

    def setMapConsole(self, con):
        self.mapConsole = con

    # Test if a square is blocked
#    def isBlocked(self, x, y):
#        return self.getTile(x, y).blocksMove()
#    
#    def blocksMove(self, x, y):
#        return self.isBlocked(x, y)
#    
#    def blocksSight(self, x, y):
#        return self.getTile(x, y).blocksSight()


                
    # Draw that map!
    def draw(self):

        for tile in self.tiles:
            if tile:
                x = tile.x
                y = tile.y
#                print "Drawing", x, ",", y, ":", tile.toDraw()
                symbol, color, background = tile.toDraw()
                symbol = symbol.encode('ascii', 'ignore')
                
                libtcod.console_put_char_ex(self.mapConsole, x, y, symbol, color, background)
                    
    # Erase that map!
    def clear(self):
        for x in range(C.MAP_WIDTH):
            for y in range(C.MAP_HEIGHT):
                libtcod.console_put_char_ex(self.mapConsole, x, y, ' ', colors.black, libtcod.BKGND_NONE)
                
            
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
                
                #add some contents to this room, such as monsters
                #self.placeObjects(newRoom)
                
                # Append the new room to the list
                rooms.append(newRoom)
                self.rooms.append(newRoom)

        # Connect them with tunnels
        if len(self.rooms) >= 1:
            for rn in range(len(self.rooms) - 1):
                thisRoom, nextRoom = self.rooms[rn], self.rooms[rn + 1]
                
                self.createTunnel(thisRoom, nextRoom)
            
            lastRoom = self.rooms[-1]
            firstRoom = self.rooms[0]
            self.createTunnel(lastRoom, firstRoom)
        
        print "Saving open tiles"
        db.saveDB.save(self)
        
        print "Placing walls"
        # Fill in empty spaces
        self.fillInSpaces()
        


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

    def createHTunnel(self, prevRoom, newRoom, x1, x2, y):
        
        for x in range(min(x1, x2), max(x1, x2)):
            skip = False
            tilesHere = self.hasTile[x][y]
            if tilesHere:
                skip = True
            
            if not skip:
#                newTunnelTile = self.defaultTunnelFloorType(x = x, y = y, level = self, room = None)
                newTunnelTile = self.defaultTunnelFloorType(x = x, y = y, room = None)
                self.tiles.append(newTunnelTile)
                self.hasTile[x][y] = True
#                self.hasTile[x][y] = newTunnelTile
#                self.addTile(newTunnelTile)

    def createVTunnel(self, prevRoom, newRoom, x, y1, y2):
        
        for y in range(min(y1, y2), max(y1, y2)):
            skip = False
            tilesHere = self.hasTile[x][y]
            if tilesHere:
                skip = True

            if not skip:
#                newTunnelTile = self.defaultTunnelFloorType(x = x, y = y, level = self, room = None)
                newTunnelTile = self.defaultTunnelFloorType(x = x, y = y, room = None)
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
            
            self.createHTunnel(prevRoom, newRoom, x1, x2, min(y1, y2))
            self.createVTunnel(prevRoom, newRoom, max(x1, x2), y1, y2)
            
                
        else:
            #Vertical first
            self.createVTunnel(prevRoom, newRoom, min(x1, x2), y1, y2)
            self.createHTunnel(prevRoom, newRoom, x1, x2, max(y1, y2))
            

    def placeStairs(self):
        pass

    
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
#            if not self.isBlocked(randx, randy):
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
    
    import UIClass as ui
    
    db.saveDB.start(True)
    
#    seed = random.randint(0, sys.maxint)
    seed = 1155272238
    print seed
    random.seed(seed)
    
    d1 = DungeonLevel(name = "Test", depth = 1, defaultFloorType = T.StoneFloor,
                      defaultWallType = T.RockWall, defaultTunnelFloorType = T.RockTunnel, defaultTunnelWallType = T.RockWall)
    
    d1.createRooms()
    
    db.saveDB.save(d1)
#    db.saveDB.saveAll(d1.tiles)

    print len(d1.tiles), "tiles"
    
    myUI = ui.UI(level=d1)
    myUI.createWindow()
    myUI.gameLoop()



if __name__ == '__main__':
    main()
