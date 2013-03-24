'''
Created on Mar 10, 2013

@author: dstu
'''

from Import import *
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Integer, Float
import colors
import database as db
from randomChoice import weightedChoice


libtcod = importLibtcod()

Base = db.saveDB.getDeclarativeBase()

class Item(Base):
    '''
    The abstract item (stack) baseclass
    '''
    __tablename__ = "items"
    __table_args__ = {'extend_existing': True}

    # Default class variables
    drinkable = False
    edible = False
    readable = False
    wearable = False
    wieldable = False
    zappable = False
    
    stackable = False

    def __init__(self, **kwargs):
        self.weight = kwargs.get('weight', 0)
        self.material = kwargs.get('material', None)
        
        self.symbol = kwargs['symbol']
        self.color = kwargs['color']
        self.backgroundColor = kwargs.get('backgroundColor', colors.black)
        self.description = kwargs.get('description', 'some item')
        self.pluralDescription = kwargs.get('plural description', self.description + 's')
        
        self.colorR = self.color.r
        self.colorG = self.color.g
        self.colorB = self.color.b
        
        self.backgroundColorR = self.backgroundColor.r
        self.backgroundColorG = self.backgroundColor.g
        self.backgroundColorB = self.backgroundColor.b
        
        self.quantity = kwargs.get('quantity', 1)

        

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
    
    description = Column(String)
    pluralDescription = Column(String)

    quantity = Column(Integer)

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
    
    def getDescription(self):
        if self.quantity == 1:
            return self.description
        else:
            return str(self.quantity) + " " + self.pluralDescription


    def setDescription(self, value):
        self.description = value

    def passTime(self, turns):
        pass
    
    def the(self):
        return "the " + self.getDescription()
    
    def The(self):
        return "The " + self.getDescription()
    
    def a_an(self):
        if self.quantity == 1:
            if self.getDescription().startswith(('a', 'e', 'i', 'o', 'u')):
                return "an " + self.getDescription()
            else:
                return "a " + self.getDescription()
        else:
            return self.getDescription()
    
    def A_An(self):
        if self.quantity == 1:
            if self.getDescription().startswith(('a', 'e', 'i', 'o', 'u')):
                return "An " + self.getDescription()
            else:
                return "A " + self.getDescription()
        else:
            return self.getDescription()

    def getQuantity(self):
        return self.quantity

    def setQuantity(self, value):
        self.quantity = value
        
    def canStackWith(self, other):
#        print "Determining stacking for " + self.getDescription() + " and " + other.getDescription()
        if not (self.stackable and other.stackable):
#            print "Not stackable!"
            return False
        
        elif self.__class__ != other.__class__:
#            print "Items incompatible!"
            return False
        
        return True

    def stackWith(self, other):
        if self.canStackWith(other):
            self.quantity += other.getQuantity()
            other.setQuantity(0)

    @classmethod
    def getStackable(cls):
        return cls.stackable



class Amulet(Item):
    wearable = True
    
    __mapper_args__ = {
        'polymorphic_identity':'amulet'
    }
    
    def __init__(self, **kwargs):
        super(Amulet, self).__init__(symbol = '"', **kwargs)

class Armor(Item):
    wearable = True
    
    __mapper_args__ = {
        'polymorphic_identity':'armor'
    }
    
    def __init__(self, **kwargs):
        super(Armor, self).__init__(symbol = '[', **kwargs)
        
class Coins(Item):
    stackable = True
    
    __mapper_args__ = {
        'polymorphic_identity':'coins'
    }
    
    def __init__(self, **kwargs):
        super(Coins, self).__init__(symbol = '$', color = colors.colorGold, description = "gold coin", **kwargs)
    

class Food(Item):
    edible = True
    
    __mapper_args__ = {
        'polymorphic_identity':'food'
    }
    
    def __init__(self, **kwargs):
        super(Food, self).__init__(symbol = '%', **kwargs)

class Gem(Item):
    
    __mapper_args__ = {
        'polymorphic_identity':'gem'
    }
    
    def __init__(self, **kwargs):
        super(Gem, self).__init__(symbol = '*', **kwargs)

class Potion(Item):
    drinkable = True
    
    __mapper_args__ = {
        'polymorphic_identity':'potion'
    }
    
    def __init__(self, **kwargs):
        super(Potion, self).__init__(symbol = '!', **kwargs)

class Ring(Item):
    wearable = True
    
    __mapper_args__ = {
        'polymorphic_identity':'ring'
    }
    
    def __init__(self, **kwargs):
        super(Ring, self).__init__(symbol = '=', **kwargs)

class Scroll(Item):
    readable = True
    
    __mapper_args__ = {
        'polymorphic_identity':'scroll'
    }
    
    def __init__(self, **kwargs):
        super(Scroll, self).__init__(symbol = '?', color = colors.white, **kwargs)
        
class Spellbook(Item):
    readable = True
    
    __mapper_args__ = {
        'polymorphic_identity':'spellbook'
    }
    
    def __init__(self, **kwargs):
        super(Spellbook, self).__init__(symbol = '+', **kwargs)
        
class Wand(Item):
    zappable = True
    
    __mapper_args__ = {
        'polymorphic_identity':'wand'
    }
    
    def __init__(self, **kwargs):
        super(Wand, self).__init__(symbol = '/', **kwargs)

class Weapon(Item):
    wieldable = True
    
    __mapper_args__ = {
        'polymorphic_identity':'weapon'
    }
    
    def __init__(self, **kwargs):
        super(Weapon, self).__init__(symbol = ')', **kwargs)





def getRandomItem():
    
    import Armors
    import Coins
    import Foods
    import Gems
    import Potions
    import Rings
    import Scrolls
    import Spellbooks
    import Wands
    import Weapons
    
    weights = {
               Armors.getRandomArmor : 9,
               Coins.getRandomCoins : 15,
               Foods.getRandomFood : 15,
               Gems.getRandomGem : 5,
               Potions.getRandomPotion : 10,
               Rings.getRandomRing : 5,
               Scrolls.getRandomScroll : 10,
               Spellbooks.getRandomSpellbook : 6,
               Wands.getRandomWand : 7,
               Weapons.getRandomWeapon : 12
               }
    
    itemFunc = weightedChoice(weights)
    item = itemFunc()
    return item




    
def main():
#    import InventoryClass as I
#    
#    db.saveDB.start(True)
#    
#    
#    item1 = Item(symbol = '!', color = colors.white)
#    item2 = Item(symbol = '!', color = colors.red)
#    
#    db.saveDB.save(item1)
#    db.saveDB.save(item2)

    coins1 = Coins(quantity = 5)
    coins2 = Coins(quantity = 10)
    
    print coins1.canStackWith(coins2)
    coins1.stackWith(coins2)
    print coins1.quantity

    
if __name__ == '__main__':
    main()
    
    
    
    
    
    
