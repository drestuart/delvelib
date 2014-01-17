'''
Created on Mar 12, 2013

@author: dstu
'''

from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey, ForeignKeyConstraint
from sqlalchemy.types import String, Integer, Boolean
import Const as C
import RoomClass as R
import TileClass as T
import colors
import database as db

Base = db.saveDB.getDeclarativeBase()

class DungeonFeature(Base):
    # Dummy class right now.  Will eventually represent dungeon features like traps, altars and stairs
    
    __tablename__ = "dungeon_features"
    __table_args__ = {'extend_existing': True}
    
    def __init__(self, symbol, baseColor, baseBackgroundColor, **kwargs):
#        self.blockSight = kwargs.get('blockSight', False)
#        self.blockMove = kwargs.get('blockMove', False)
        self.symbol = symbol
        
        self.color = baseColor
        
        self.colorR = self.color.r
        self.colorG = self.color.g
        self.colorB = self.color.b
        
        self.backgroundColor = baseBackgroundColor
        
        self.backgroundColorR = self.backgroundColor.r
        self.backgroundColorG = self.backgroundColor.g
        self.backgroundColorB = self.backgroundColor.b
        
        self.tile = kwargs.get('tile', None)
        
        self.visible = kwargs.get('isVisible', True)
        
        
    id = Column(Integer, primary_key=True)
    name = Column(String)
    symbol = Column(String(length=1, convert_unicode = False))
    
    colorR = Column(Integer)
    colorG = Column(Integer)
    colorB = Column(Integer)
    
    backgroundColorR = Column(Integer)
    backgroundColorG = Column(Integer)
    backgroundColorB = Column(Integer)
    
    tileId = Column(Integer) #, ForeignKey('tiles.id')
    
    visible = Column(Boolean)
    
    featureType = Column(String)
    
    __mapper_args__ = {'polymorphic_on': featureType,
                       'polymorphic_identity': 'feature'}

    def isVisible(self):
        return self.visible
    
    def setVisible(self, val):
        self.visible = val

#    def getBlockSight(self):
#        return self.blockSight
#
#
#    def getBlockMove(self):
#        return self.blockMove


    def getSymbol(self):
        return self.symbol


    def getBaseColor(self):        
        if self.__dict__.get('color', None):
            return self.color
        else:
            self.color = (self.colorR, self.colorG, self.colorB)
            return self.color

    
    def getColor(self):
        return self.getBaseColor()


    def getBaseColorR(self):
        return self.colorR


    def getBaseColorG(self):
        return self.colorG


    def getBaseColorB(self):
        return self.colorB
    
    def getBackgroundColor(self):
        return self.getBaseBackgroundColor()


    def getBaseBackgroundColor(self):
        if self.__dict__.get('backgroundColor', None):
            return self.backgroundColor
        else:
            self.backgroundColor = (self.backgroundColorR, self.backgroundColorG, self.backgroundColorB)
            return self.backgroundColor


    def getBaseBackgroundColorR(self):
        return self.backgroundColorR


    def getBaseBackgroundColorG(self):
        return self.backgroundColorG


    def getBaseBackgroundColorB(self):
        return self.backgroundColorB


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
        self.color = value


    def setBaseColorR(self, value):
        self.colorR = value


    def setBaseColorG(self, value):
        self.colorG = value


    def setBaseColorB(self, value):
        self.colorB = value


    def setBaseBackgroundColor(self, value):
        self.backgroundColor = value


    def setBaseBackgroundColorR(self, value):
        self.backgroundColorR = value


    def setBaseBackgroundColorG(self, value):
        self.backgroundColorG = value


    def setBaseBackgroundColorB(self, value):
        self.backgroundColorB = value


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
        self.color = colors.colorWood


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
        return self.closed

    def setClosed(self, value):
        self.closed = value

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
        
        super(upStair, self).__init__(symbol = '<', baseColor = colors.colorStone, baseBackgroundColor = colors.black, **kwargs)
        
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
        super(downStair, self).__init__(symbol = '>', baseColor = colors.colorStone, baseBackgroundColor = colors.black, **kwargs)
        
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

