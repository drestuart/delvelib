'''
Created on Mar 10, 2013

@author: dstu
'''

from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Integer, Boolean
import database as db
import TileClass as T

Base = db.saveDB.getDeclarativeBase()

# The Rectangle class
class Rect(object):
    #a rectangle on the map. used to characterize a room.
    def __init__(self, x, y, width, height):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    def getX1(self):
        return self.x1

    def getY1(self):
        return self.y1

    def getX2(self):
        return self.x2

    def getY2(self):
        return self.y2

    def getCenterX(self):
        return self.centerX

    def getCenterY(self):
        return self.centerY

    def setX1(self, value):
        self.x1 = value

    def setY1(self, value):
        self.y1 = value

    def setX2(self, value):
        self.x2 = value

    def setY2(self, value):
        self.y2 = value

    def setCenterX(self, value):
        self.centerX = value

    def setCenterY(self, value):
        self.centerY = value

    def delX1(self):
        del self.x1

    def delY1(self):
        del self.y1

    def delX2(self):
        del self.x2

    def delY2(self):
        del self.y2

    def delCenterX(self):
        del self.centerX

    def delCenterY(self):
        del self.centerY

    def getCenter(self):
        self.centerX = (self.x1 + self.x2) / 2
        self.centerY = (self.y1 + self.y2) / 2
        return (self.centerX, self.centerY)
 
    def intersect(self, other):
        #returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)
        
    def contains(self, x, y):
        return (self.x1 <= x and self.x2 >= x and
                self.y1 <= y and self.y2 >= y)


class Room(Rect, Base):
    
    __tablename__ = "rooms"
    __table_args__ = {'extend_existing': True}

    def __init__(self, **kwargs):
        super(Room, self).__init__(kwargs['x'], kwargs['y'], kwargs['width'], kwargs['height'])
        
        self.getCenter()
        self.tiles = []
    
    id = Column(Integer, primary_key=True)
    
    x1 = Column(Integer)
    y1 = Column(Integer)
    
    x2 = Column(Integer)
    y2 = Column(Integer)
    
    centerX = Column(Integer)
    centerY = Column(Integer)
    
#    level = relationship("Level", primaryjoin="Level.id==Room.levelId")
    levelId = Column(Integer, ForeignKey("levels.id"))

    tiles = relationship("Tile", backref=backref("room"), primaryjoin="Room.id==Tile.roomId")
    
#    def fillWithTiles(self):
#        # Create wall tiles
#        
#        # Top and bottom walls
#        for x in range(self.x1 - 1, self.x2 + 1):
##            topWall = self.defaultWallType(x=x, y=self.y2 + 1, level=self.getLevel())
##            self.tiles.append(topWall)
##            bottomWall = self.defaultWallType(x=x, y=self.y1 - 1, level=self.getLevel())
##            self.tiles.append(bottomWall)
#            pass
#            
##            print topWall
##            print bottomWall
#        
#        # Left and right walls
#        for y in range(self.y1, self.y2):  # Don't need to do the corners again!
##            leftWall = self.defaultWallType(x=self.x1 - 1, y=y, level=self.getLevel())
##            self.tiles.append(leftWall)
##            rightWall = self.defaultWallType(x=self.x2 + 1, y=y, level=self.getLevel())
##            self.tiles.append(rightWall)
#            pass
#            
##            print rightWall
##            print leftWall
#        
#        
#        # Create floor tiles
#        for x in range(self.x1, self.x2):
#            for y in range(self.y1, self.y2):
#                # Add some chance for a dungeon feature here
#                
##                floor = self.defaultFloorType(x = x, y = y, room = self, level = self.getLevel())
#                floor = self.defaultFloorType(x = x, y = y, room = self)
##                self.tiles.append(floor)
##                print floor
#                
#        # Save
##        db.saveDB.saveAll(self.tiles)
        

    def getLevel(self):
        return self.level

    def getX1(self):
        return self.x1

    def getY1(self):
        return self.y1

    def getX2(self):
        return self.x2

    def getY2(self):
        return self.y2

    def getCenterX(self):
        return self.centerX

    def getCenterY(self):
        return self.centerY

    def getLevelId(self):
        return self.levelId
    
    def getTiles(self):
        return self.tiles

    def setLevel(self, value):
        self.level = value
        if value:
            self.setLevelId(value.id)
        else:
            self.setLevelId(None)

    def setX1(self, value):
        self.x1 = value

    def setY1(self, value):
        self.y1 = value

    def setX2(self, value):
        self.x2 = value

    def setY2(self, value):
        self.y2 = value

    def setCenterX(self, value):
        self.centerX = value

    def setCenterY(self, value):
        self.centerY = value

    def setLevelId(self, value):
        self.levelId = value

    def delLevel(self):
        del self.level

    def delX1(self):
        del self.x1

    def delY1(self):
        del self.y1

    def delX2(self):
        del self.x2

    def delY2(self):
        del self.y2

    def delCenterX(self):
        del self.centerX

    def delCenterY(self):
        del self.centerY

    def delLevelId(self):
        del self.levelId
        
    def contains(self, x, y):
        return (self.x1 <= x and self.x2 >= x and
                self.y1 <= y and self.y2 >= y)
    
    
def main():
    
    import LevelClass
    
    db.saveDB.start(True)


    r1 = Room(x = 10, y = 20, width = 5, height = 5,
              defaultFloorType = T.WoodFloor, defaultWallType = T.WoodWall)
    
    r1.fillWithTiles()
    db.saveDB.save(r1)
    db.saveDB.saveAll(r1.tiles)

    
    
if __name__ == '__main__':
    main()
    
    
    
    