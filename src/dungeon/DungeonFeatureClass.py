'''
Created on Mar 12, 2013

@author: dstu
'''

from Import import *
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey, ForeignKeyConstraint
from sqlalchemy.types import String, Integer, Boolean
import Const as C
import RoomClass as R
import TileClass as T
import colors
import database as db

libtcod = importLibtcod()


Base = db.saveDB.getDeclarativeBase()

class DungeonFeature(Base):
    # Dummy class right now.  Will eventually represent dungeon features like traps, altars and stairs
    
    __tablename__ = "dungeon_features"
    __table_args__ = {'extend_existing': True}
    
    def __init__(self, symbol, baseColor, baseBackgroundColor, **kwargs):
        self.blockSight = kwargs.get('blockSight', False)
        self.blockMove = kwargs.get('blockMove', False)
        self.symbol = symbol
        
        self.baseColor = baseColor
        
        self.baseColorR = self.baseColor.r
        self.baseColorG = self.baseColor.g
        self.baseColorB = self.baseColor.b
        
        self.baseBackgroundColor = baseBackgroundColor
        
        self.baseBackgroundColorR = self.baseBackgroundColor.r
        self.baseBackgroundColorG = self.baseBackgroundColor.g
        self.baseBackgroundColorB = self.baseBackgroundColor.b
        
        self.tile = kwargs.get('tile', None)
        
        self.visible = kwargs.get('isVisible', True)
        
        
    id = Column(Integer, primary_key=True)
    name = Column(String)
    symbol = Column(String(length=1, convert_unicode = False))
    
    baseColorR = Column(Integer)
    baseColorG = Column(Integer)
    baseColorB = Column(Integer)
    
    baseBackgroundColorR = Column(Integer)
    baseBackgroundColorG = Column(Integer)
    baseBackgroundColorB = Column(Integer)
    
    tileId = Column(Integer) #, ForeignKey('tiles.id')
    
    visible = Column(Boolean)
    
    featureType = Column(String)
    
    __mapper_args__ = {'polymorphic_on': featureType,
                       'polymorphic_identity': 'feature'}

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


    def getBaseColor(self):        
        if self.__dict__.get('baseColor', None):
            return self.baseColor
        else:
            self.baseColor = libtcod.Color(self.baseColorR, self.baseColorG, self.baseColorB)
            return self.baseColor

    
    def getColor(self):
        return self.getBaseColor()


    def getBaseColorR(self):
        return self.baseColorR


    def getBaseColorG(self):
        return self.baseColorG


    def getBaseColorB(self):
        return self.baseColorB
    
    def getBackgroundColor(self):
        return self.getBaseBackgroundColor()


    def getBaseBackgroundColor(self):
        if self.__dict__.get('baseBackgroundColor', None):
            return self.baseBackgroundColor
        else:
            self.baseBackgroundColor = libtcod.Color(self.baseBackgroundColorR, self.baseBackgroundColorG, self.baseBackgroundColorB)
            return self.baseBackgroundColor


    def getBaseBackgroundColorR(self):
        return self.baseBackgroundColorR


    def getBaseBackgroundColorG(self):
        return self.baseBackgroundColorG


    def getBaseBackgroundColorB(self):
        return self.baseBackgroundColorB


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


    def setBaseColor(self, value):
        self.baseColor = value


    def setBaseColorR(self, value):
        self.baseColorR = value


    def setBaseColorG(self, value):
        self.baseColorG = value


    def setBaseColorB(self, value):
        self.baseColorB = value


    def setBaseBackgroundColor(self, value):
        self.baseBackgroundColor = value


    def setBaseBackgroundColorR(self, value):
        self.baseBackgroundColorR = value


    def setBaseBackgroundColorG(self, value):
        self.baseBackgroundColorG = value


    def setBaseBackgroundColorB(self, value):
        self.baseBackgroundColorB = value


    def setTile(self, value):
        self.tile = value


    def setName(self, value):
        self.name = value


    def setBaseSymbol(self, value):
        self.baseSymbol = value


class Door(DungeonFeature):
    
    def __init__(self, **kwargs):
        super(Door, self).__init__(symbol = '+', baseColor = colors.colorWood, baseBackgroundColor = colors.black, **kwargs)
        self.closed = True
        self.baseColor = colors.colorWood


    closed = Column(Boolean)
    
    __mapper_args__ = {'polymorphic_identity': 'door'}


    def open_(self):
        if self.closed:
            self.closed = False
            self.symbol = "'"
            return True
        
        else:
            return False
        
    def close(self):
        if self.closed:
            return False
        
        else:
            self.closed = True
            self.symbol = "+"
            return True

    def isClosed(self):
        return self.__closed

    def setClosed(self, value):
        self.__closed = value

    def getSymbol(self):
        if self.closed:
            self.symbol = "+"
        else:
            self.symbol = "'"
        return self.symbol
    
class Stair(DungeonFeature):
    
    def __init__(self, **kwargs):
        super(Stair, self).__init__(**kwargs)
    
    __mapper_args__ = {'polymorphic_identity': 'Stair'}
    
    def getDestination(self):
        return self.destination
    
    def setDestination(self, d):
        self.destination = d
    
class upStair(DungeonFeature):
    
    def __init__(self, **kwargs):
        super(upStair, self).__init__(symbol = '<', baseColor = colors.colorStone, baseBackgroundColor = colors.black, **kwargs)
        self.destination = kwargs.get('destination', None)
        
    __mapper_args__ = {'polymorphic_identity': 'upStair'}
 
    
    def goUp(self, creature):
        creature.setTile(self.getDestination())
        creature.setLevel(self.getDestination().getLevel())

class downStair(DungeonFeature):
    
    def __init__(self, **kwargs):
        super(downStair, self).__init__(symbol = '>', baseColor = colors.colorStone, baseBackgroundColor = colors.black, **kwargs)
        self.destination = kwargs.get('destination', None)
        
    __mapper_args__ = {'polymorphic_identity': 'downStair'}

    def goDown(self, creature):
        creature.setTile(self.getDestination())
        creature.setLevel(self.getDestination().getLevel())




















    
    
    
    
    
    
    
    
    
    
