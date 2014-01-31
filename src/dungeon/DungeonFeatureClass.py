'''
Created on Mar 12, 2013

@author: dstu
'''

from pubsub import pub
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey, ForeignKeyConstraint
from sqlalchemy.types import String, Integer, Boolean
import Const as C
import RoomClass as R
import TileClass as T
import colors
import database as db

Base = db.saveDB.getDeclarativeBase()

class DungeonFeature(colors.withBackgroundColor, Base):
    # Dummy class right now.  Will eventually represent dungeon features like traps, altars and stairs
    
    __tablename__ = "dungeon_features"
    __table_args__ = {'extend_existing': True}
    
    def __init__(self, symbol, **kwargs):
        super(DungeonFeature, self).__init__(**kwargs)
        self.symbol = symbol
        
        self.tile = kwargs.get('tile', None)
        
        self.visible = kwargs.get('isVisible', True)
        self.description = kwargs.get('description', '')
        
        
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    symbol = Column(String(length=1, convert_unicode = False))
    
    tileId = Column(Integer)
    visible = Column(Boolean)
    featureType = Column(String)
    
    __mapper_args__ = {'polymorphic_on': featureType,
                       'polymorphic_identity': 'feature'}

    def handleBump(self, creature):
        return False
    
    def isVisible(self):
        return self.visible
    
    def setVisible(self, val):
        self.visible = val

    def getBlockSight(self):
        return self.blockSight

    def getBlockMove(self):
        return self.blockMove


    def getSymbol(self):
        return self.symbol

    def getTile(self):
        return self.tile


    def getName(self):
        return self.name


    def getBaseSymbol(self):
        return self.baseSymbol


    def setBlockSight(self, value):
        self.blockSight = value


    def setBlockMove(self, value):
        self.blockMove = value


    def setSymbol(self, value):
        self.symbol = value


    def setTile(self, value):
        self.tile = value


    def setName(self, value):
        self.name = value


    def setBaseSymbol(self, value):
        self.baseSymbol = value


class Door(DungeonFeature):
    
    def __init__(self, **kwargs):
        super(Door, self).__init__(symbol = '+', description = 'a door', color = colors.colorWood, backgroundColor = colors.black, **kwargs)
        self.closed = True
        self.color = colors.colorWood


    closed = Column(Boolean)
    
    __mapper_args__ = {'polymorphic_identity': 'door'}


    def open_(self):
        if self.isClosed():
            self.setClosed(False)
            pub.sendMessage("event.doorOpen", tile = self.tile)
            return True
        else:
            return False
        
    def close(self):
        if self.isClosed():
            return False
        else:
            self.setClosed(True)
            pub.sendMessage("event.doorClose", tile = self.tile)
            return True
    
    def handleBump(self, creature):
        if self.isClosed():
            return self.open_()
        return False

    def isClosed(self):
        return self.closed
    
    def isOpen(self):
        return not self.isClosed()

    def setClosed(self, value):
        self.closed = value
        if value:
            self.symbol = "+"
        else:
            self.symbol = "'"

    def getSymbol(self):
        if self.closed:
            self.symbol = "+"
        else:
            self.symbol = "'"
        return self.symbol
    
    def getBlockSight(self):
        return self.isClosed()
    
    def getBlockMove(self):
        return self.isClosed()
    
    
class Stair(DungeonFeature):
    
    def __init__(self, **kwargs):
        super(Stair, self).__init__(**kwargs)
        self.blockMove = False
        self.blockSight = False
    
    __mapper_args__ = {'polymorphic_identity': 'Stair'}
    
    def getDestination(self):
        return self.destination
    
    def setDestination(self, d):
        self.destination = d

        
class upStair(Stair):
    
    def __init__(self, **kwargs):
        
        super(upStair, self).__init__(symbol = '<', description = 'a stairway leading up', color = colors.colorStone, backgroundColor = colors.black, **kwargs)
        
        self.destination = kwargs.get('destination', None)
        
    __mapper_args__ = {'polymorphic_identity': 'upStair'}
 
    blockMove = False
    blockSight = False
    
    def goUp(self, creature):
        creature.setTile(self.getDestination())
        creature.setLevel(self.getDestination().getLevel())
        
    def getBlockSight(self):
        return self.blockSight


    def getBlockMove(self):
        return self.blockMove

class downStair(Stair):
    
    def __init__(self, **kwargs):
        super(downStair, self).__init__(symbol = '>', description = 'a stairway leading down', color = colors.colorStone, backgroundColor = colors.black, **kwargs)
        
        self.destination = kwargs.get('destination', None)
        
    __mapper_args__ = {'polymorphic_identity': 'downStair'}
    
    blockMove = False
    blockSight = False

    def goDown(self, creature):
        creature.setTile(self.getDestination())
        creature.setLevel(self.getDestination().getLevel())

    def getBlockSight(self):
        return self.blockSight


    def getBlockMove(self):
        return self.blockMove

