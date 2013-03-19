'''
Created on May 17, 2012

@author: dstu
'''

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer
import database as db

Base = db.saveDB.getDeclarativeBase()

class Inventory(Base):
    '''
    The inventory class.  Represents a collection of items, either in a container or held by a person.
    Also provides some convenience methods.
    '''

    __tablename__ = "inventories"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    items = relationship("Item", backref=backref("container", uselist=False), primaryjoin="Inventory.id==Item.containerId")
#    personId = Column(Integer, ForeignKey("people.id"))
#    person = relationship("Person", backref=backref("inventory", uselist=False))
    
    def __init__(self, items = [], person = None):
        
        for item in items:
            self.addItem(item)
            
        self.person = person

    
    def printContents(self):
        print self.items
    
    def addItem(self, itemIn):
        if not self.items:
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
    
    def getId(self):
        return self.id
    
    def setId(self, val):
        self.id = val
        return self
    
    def getItems(self):
        return self.items
    
    def setItems(self, val):
        self.items = val
        return self
    
    def getPersonId(self):
        return self.personId
    
    def setPersonId(self, val):
        self.personId = val
        return self
    
    def getPerson(self):
        return self.person
    
    def setPerson(self, val):
        self.person = val
        if val:
            self.setContainingItem(None)
            self.setPersonId(val.getId())
        else:
            self.setPersonId(None)
        return self
    
    def getContainingItemId(self):
        return self.containingItemId
    
    def setContainingItemId(self, val):
        self.containingItemId = val
        return self
    
    def getContainingItem(self):
        return self.containingItem
    
    def setContainingItem(self, val):
        self.containingItem = val
        if val:
            self.setPerson(None)
            self.setContainingItemId(val.getId())
        else:
            self.setContainingItemId(None)
        return self
    
    def pop(self):
        if len(self.items) == 0:
            return None
        itemToPop = self.items[0]
        return self.removeItem(itemToPop)
    
def main():
    pass

if __name__ == "__main__":
    main()
    
