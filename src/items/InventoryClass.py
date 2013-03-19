'''
Created on May 17, 2012

@author: dstu
'''

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String
import ItemClass as I
import colors
import database as db

Base = db.saveDB.getDeclarativeBase()

class Inventory(Base):
    '''
    The inventory class.  Represents a collection of items, either on a tile, in a container or held by a person.
    Also provides some convenience methods.
    '''

    __tablename__ = "inventories"
    __table_args__ = {'extend_existing': True}
    
    def __init__(self, **kwargs):
        
        self.items = []
    
    id = Column(Integer, primary_key=True)
    items = relationship("Item", backref=backref("container", uselist=False), primaryjoin="Inventory.id == Item.containerId")
    inventoryType = Column(String)
    
    # If this inventory belongs to an item
    containingItemId = Column(Integer, ForeignKey("items.id", use_alter=True, name='containing_item_fk'))
    containingItem = relationship("Item", uselist=False, backref=backref("myInventory", uselist=False), primaryjoin="Inventory.id == Item.myInventoryId")

    
    __mapper_args__ = {
        'polymorphic_on':inventoryType,
        'polymorphic_identity':'item'
    }
    
    
    def printContents(self):
        print self.items
    
    def addItem(self, itemIn):
        if self.items is None:
            self.items = []
        if not itemIn in self.items:
            self.items.append(itemIn)
#            itemIn.setContainer(self)
            return self
        
        raise ValueError(itemIn + " already exists in container " + self)
    
    def removeItem(self, itemIn):
        if itemIn in self.items:
            self.items.remove(itemIn)
#            itemIn.setContainer(None)
            return itemIn
        
        raise ValueError(itemIn + " does not exist in container " + self)
    
    def pop(self):
        if len(self.items) == 0:
            return None
        itemToPop = self.items[0]
        return self.removeItem(itemToPop)
    
    def getItem(self, ind):
        return self.items[ind]

    def getItems(self):
        return self.items


    def getContainingItem(self):
        return self.containingItem


    def setItems(self, value):
        self.items = value


    def setContainingItem(self, value):
        self.containingItem = value

    def length(self):
        return len(self.items)
    


def main():
    db.saveDB.start(True)
    
    item1 = I.Item(symbol = '!', color = colors.white)
    item2 = I.Item(symbol = '!', color = colors.red)
    
    inv1 = Inventory()
    inv1.addItem(item1)
    inv1.addItem(item2)
    
    db.saveDB.save(inv1)




    
if __name__ == '__main__':
    main()
    
