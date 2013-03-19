'''
Created on Mar 10, 2013

@author: dstu
'''

from Import import *
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Integer, Float
import colors
import database as db

libtcod = importLibtcod()

Base = db.saveDB.getDeclarativeBase()

class Item(Base):
    '''
    The abstract item baseclass
    '''
    __tablename__ = "items"
    __table_args__ = {'extend_existing': True}


    def __init__(self, **kwargs):
        self.weight = kwargs.get('weight', 0)
        self.material = kwargs.get('material', None)
        
        self.symbol = kwargs['symbol']
        self.color = kwargs['color']
        self.backgroundColor = kwargs.get('baseBackground', colors.black)
        
        self.colorR = self.color.r
        self.colorG = self.color.g
        self.colorB = self.color.b
        
        self.backgroundColorR = self.backgroundColor.r
        self.backgroundColorG = self.backgroundColor.g
        self.backgroundColorB = self.backgroundColor.b
        

    id = Column(Integer, primary_key=True)
    weight = Column(Float)
    itemType = Column(String)
    material = Column(String)
    
    symbol = Column(String(length=1, convert_unicode = False))
    
    colorR = Column(Integer)
    colorG = Column(Integer)
    colorB = Column(Integer)
    
    backgroundColorR = Column(Integer)
    backgroundColorG = Column(Integer)
    backgroundColorB = Column(Integer)

    containerId = Column(Integer, ForeignKey("inventories.id"))
    
    # For items that have an inventory of their own
    myInventoryId = Column(Integer, ForeignKey("inventories.id", use_alter=True, name='my_inventory_fk'))
#    inventory = relationship("Inventory", uselist=False, backref=backref("containingItem", uselist=False), primaryjoin="Inventory.id==Item.inventoryId")

    
    __mapper_args__ = {
        'polymorphic_on':itemType,
        'polymorphic_identity':'item'
    }
    
    
    def drop(self):
        # TODO: Handle universal dropping logic
        self.onDrop()
        
    def pickup(self):
        # TODO: Handle universal pickup logic
        self.onPickup()
        
    def use(self):
        self.onUse()

    def getWeight(self):
        return self.weight


    def getMaterial(self):
        return self.material


    def getSymbol(self):
        return self.symbol


    def setWeight(self, value):
        self.weight = value


    def setMaterial(self, value):
        self.material = value


    def setSymbol(self, value):
        self.symbol = value

    def getColor(self):        
        if self.__dict__.get('color', None):
            return self.color
        else:
            self.color = libtcod.Color(self.colorR, self.colorG, self.colorB)
            return self.color

    def getBackgroundColor(self):        
        if self.__dict__.get('backgroundColor', None):
            return self.backgroundColor
        else:
            self.backgroundColor = libtcod.Color(self.backgroundColorR, self.backgroundColorG, self.backgroundColorB)
            return self.backgroundColor
        
    def setColor(self, value):
        self.color = value
        self.setColorB(value.b)
        self.setColorG(value.g)
        self.setColorR(value.r)


    def setBackgroundColor(self, value):
        self.backgroundColor = value
        self.setBackgroundColorB(value.b)
        self.setBackgroundColorG(value.g)
        self.setBackgroundColorR(value.r)

    def getColorR(self):
        return self.colorR


    def getColorG(self):
        return self.colorG


    def getColorB(self):
        return self.colorB


    def getBackgroundColorR(self):
        return self.backgroundColorR


    def getBackgroundColorG(self):
        return self.backgroundColorG


    def getBackgroundColorB(self):
        return self.backgroundColorB


    def setColorR(self, value):
        self.colorR = value


    def setColorG(self, value):
        self.colorG = value


    def setColorB(self, value):
        self.colorB = value


    def setBackgroundColorR(self, value):
        self.backgroundColorR = value


    def setBackgroundColorG(self, value):
        self.backgroundColorG = value


    def setBackgroundColorB(self, value):
        self.backgroundColorB = value

    
    
    
def main():
    import InventoryClass as I
    
    db.saveDB.start(True)
    
    
    item1 = Item(symbol = '!', color = colors.white)
    item2 = Item(symbol = '!', color = colors.red)
    
    db.saveDB.save(item1)
    db.saveDB.save(item2)



    
if __name__ == '__main__':
    main()
    
    
    
    
    
    
