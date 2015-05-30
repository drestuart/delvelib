'''
Created on Mar 10, 2013

@author: dstu
'''

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Unicode, Integer, Float
import colors
import database as db
from randomChoice import weightedChoice

Base = db.saveDB.getDeclarativeBase()

class Item(colors.withColor, Base):
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
    
    description = "item"

    def __init__(self, **kwargs):
        super(Item, self).__init__(**kwargs)
        
        self.weight = kwargs.get('weight', 0)
        self.material = kwargs.get('material', None)
        
        self.symbol = kwargs['symbol']
        
        self.quantity = kwargs.get('quantity', 1)

        

    id = Column(Integer, primary_key=True)
    weight = Column(Float)
    itemType = Column(Unicode)
    material = Column(Unicode)
    
    symbol = Column(Unicode(length=1))
    
    quantity = Column(Integer)

    containerId = Column(Integer, ForeignKey("inventories.id"))
    
    # For items that have an inventory of their own
    myInventoryId = Column(Integer, ForeignKey("inventories.id", use_alter=True, name='my_inventory_fk'))
#    inventory = relationship("Inventory", uselist=False, backref=backref("containingItem", uselist=False), primaryjoin="Inventory.id==Item.inventoryId")

    
    __mapper_args__ = {
        'polymorphic_on':itemType,
        'polymorphic_identity':u'item'
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
    
    def getDescription(self):
        if self.quantity == 1:
            return self.description
        else:
            return str(self.quantity) + " " + self.getPluralDescription()
        
    def getPluralDescription(self):
        if self.__class__.pluralDescription:
            return self.__class__.pluralDescription
        return self.description + "s"

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
    
    @classmethod
    def getDrinkable(cls):
        return cls.drinkable
    
    @classmethod
    def getEdible(cls):
        return cls.edible
    
    @classmethod
    def getReadable(cls):
        return cls.readable
    
    @classmethod
    def getWearable(cls):
        return cls.wearable
    
    @classmethod
    def getWieldable(cls):
        return cls.wieldable
    
    @classmethod
    def getZappable(cls):
        return cls.zappable


class Amulet(Item):
    wearable = True
    
    __mapper_args__ = {'polymorphic_identity':u'amulet'}
    
    def __init__(self, **kwargs):
        super(Amulet, self).__init__(symbol = u'"', **kwargs)

class Armor(Item):
    wearable = True
    
    __mapper_args__ = {'polymorphic_identity':u'armor'}
    
    def __init__(self, **kwargs):
        super(Armor, self).__init__(symbol = u'[', **kwargs)
        
class Coins(Item):
    stackable = True
    color = colors.colorGold
    
    __mapper_args__ = {'polymorphic_identity':u'coins'}
    description = "gold coin"
    
    def __init__(self, **kwargs):
        super(Coins, self).__init__(symbol = u'$', **kwargs)
    

class Food(Item):
    edible = True
    
    __mapper_args__ = {'polymorphic_identity':u'food'}
    
    def __init__(self, **kwargs):
        super(Food, self).__init__(symbol = u'%', **kwargs)

class Gem(Item):
    
    __mapper_args__ = {'polymorphic_identity':u'gem'}
    
    def __init__(self, **kwargs):
        super(Gem, self).__init__(symbol = u'*', **kwargs)

class Potion(Item):
    drinkable = True
    
    __mapper_args__ = {'polymorphic_identity':u'potion'}
    
    def __init__(self, **kwargs):
        super(Potion, self).__init__(symbol = u'!', **kwargs)

class Ring(Item):
    wearable = True
    
    __mapper_args__ = {'polymorphic_identity':u'ring'}
    
    def __init__(self, **kwargs):
        super(Ring, self).__init__(symbol = u'=', **kwargs)

class Scroll(Item):
    readable = True
    color = colors.white
    __mapper_args__ = {'polymorphic_identity':u'scroll'}
    
    def __init__(self, **kwargs):
        super(Scroll, self).__init__(symbol = u'?', **kwargs)
        
class Spellbook(Item):
    readable = True
    
    __mapper_args__ = {'polymorphic_identity':u'spellbook'}
    
    def __init__(self, **kwargs):
        super(Spellbook, self).__init__(symbol = u'+', **kwargs)
        
class Wand(Item):
    zappable = True
    
    __mapper_args__ = {'polymorphic_identity':u'wand'}
    
    def __init__(self, **kwargs):
        super(Wand, self).__init__(symbol = u'/', **kwargs)

class Weapon(Item):
    wieldable = True
    
    __mapper_args__ = {'polymorphic_identity':u'weapon'}
    
    def __init__(self, **kwargs):
        super(Weapon, self).__init__(symbol = u')', **kwargs)





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
#    item1 = Item(symbol = u'!', color = colors.white)
#    item2 = Item(symbol = u'!', color = colors.red)
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
    
    
    
    
    
    
