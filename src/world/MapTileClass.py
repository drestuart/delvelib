'''
Created on Feb 25, 2014

@author: dstuart
'''

from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Integer, Boolean

from TileClass import TileBase
import colors
import database as db

Base = db.saveDB.getDeclarativeBase()

class MapTile(TileBase):
    
    __tablename__ = "tiles"
    __table_args__ = {'extend_existing': True}
    
    def __init__(self, x, y, **kwargs):
        super(MapTile, self).__init__(**kwargs)
        
        self.x = x
        self.y = y
        
        self.blockMove = kwargs.get('blockMove', False)

        
        
        
        
        
        
        
        

