'''
Created on May 17, 2012

@author: dstu
'''

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, Unicode
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
    inventoryType = Column(Unicode)
    
    # If this inventory belongs to an item
    containingItemId = Column(Integer, ForeignKey("items.id", use_alter=True, name='containing_item_fk'))
    containingItem = relationship("Item", uselist=False, backref=backref("myInventory", uselist=False), primaryjoin="Inventory.id == Item.myInventoryId")

    
    __mapper_args__ = {
        'polymorphic_on':inventoryType,
        'polymorphic_identity':'inventory'
    }
    
    
    def printContents(self):
        for item in self.items:
            print item.getDescription()
    
    def addItem(self, itemIn):
        if self.items is None:
            self.items = []
        
        if self.items == []:
            self.items.append(itemIn)
            return self
        
        if not itemIn in self.items:
            if not type(itemIn).getStackable():
#                print itemIn.getDescription() + " is not stackable"
                self.items.append(itemIn)
                
            else:
                stacked = False
                for item in self.items:
                    if item.canStackWith(itemIn):
#                        print "Stacking " + itemIn.getDescription() + " and " + item.getDescription()
                        item.stackWith(itemIn)
                        stacked = True
                        del itemIn
                        break
                
                if not stacked:
                    self.items.append(itemIn)
                
            return self
        
        raise ValueError(itemIn + " already exists in container " + self)
    
    def removeItem(self, itemIn):
        if itemIn in self.items:
            self.items.remove(itemIn)
#            itemIn.setContainer(None)
            return itemIn
        
        raise ValueError(itemIn + " does not exist in container " + self)
    
    def pop(self, ind = 0):
        if len(self.items) <= ind:
            return None
        itemToPop = self.items[ind]
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
    
    coins1 = I.Coins(quantity = 5)
    coins2 = I.Coins(quantity = 10)
    
    print coins1.canStackWith(coins2)
    coins1.stackWith(coins2)
    print coins1.quantity

    coins2 = I.Coins(quantity = 10)

    inv = Inventory()
    inv.addItem(coins1)
    inv.addItem(coins2)
    
    inv.printContents()


    
if __name__ == '__main__':
    main()
    
