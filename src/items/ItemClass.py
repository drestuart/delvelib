'''
Created on Mar 10, 2013

@author: dstu
'''

import colors
from randomChoice import weightedChoice
from pubsub import pub

pickupEventPrefix = "event.item.pickup."
dropEventPrefix = "event.item.drop."

questPickupEventPrefix = "event.quest.item.pickup."
questDropEventPrefix = "event.quest.item.drop."

class Item(colors.withColor):
    '''
    The abstract item (stack) baseclass
    '''

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
        
        self.questItem = kwargs.get('questItem', False)
        self.container = None
        self.inventory = None
        
# TODO:
#    inventory = relationship("Inventory", uselist=False, backref=backref("containingItem", uselist=False), primaryjoin="Inventory.id==Item.inventoryId")

    def pickupEvent(self):
        pub.sendMessage(self.getPickupEvent(), item=self)
        if self.isQuestItem():
            pub.sendMessage(self.getQuestPickupEvent(), item=self)
    
    @classmethod
    def getPickupEvent(cls):
        return pickupEventPrefix + cls.__mapper_args__['polymorphic_identity']
#         return pickupEventPrefix + cls.itemType
    
    @classmethod
    def getQuestPickupEvent(cls):
        return questPickupEventPrefix + cls.__mapper_args__['polymorphic_identity']
#         return questPickupEventPrefix + cls.itemType
    
    def dropEvent(self):
        pub.sendMessage(self.getDropEvent(), item=self)
        if self.isQuestItem():
            pub.sendMessage(self.getQuestDropEvent(), item=self)
    
    @classmethod
    def getDropEvent(cls):
        return dropEventPrefix + cls.__mapper_args__['polymorphic_identity']
#         return dropEventPrefix + cls.itemType
    
    @classmethod
    def getQuestDropEvent(cls):
        return questDropEventPrefix + cls.__mapper_args__['polymorphic_identity']
#         return questDropEventPrefix + cls.itemType
        
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
        try:
            return self.__class__.pluralDescription
        except AttributeError:
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
        if not (self.stackable and other.stackable):
            return False
        
        elif self.__class__ != other.__class__:
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
    
    def isQuestItem(self):
        return self.questItem


class Amulet(Item):
    wearable = True
    
    def __init__(self, **kwargs):
        super(Amulet, self).__init__(symbol = u'"', **kwargs)

class Armor(Item):
    wearable = True
    
    def __init__(self, **kwargs):
        super(Armor, self).__init__(symbol = u'[', **kwargs)
        
class Coins(Item):
    stackable = True
    color = colors.colorGold
    
    description = "gold coin"
    
    def __init__(self, **kwargs):
        super(Coins, self).__init__(symbol = u'$', **kwargs)
    

class Food(Item):
    edible = True
    
    def __init__(self, **kwargs):
        super(Food, self).__init__(symbol = u'%', **kwargs)

class Gem(Item):
    
    def __init__(self, **kwargs):
        super(Gem, self).__init__(symbol = u'*', **kwargs)

class Potion(Item):
    drinkable = True
    
    def __init__(self, **kwargs):
        super(Potion, self).__init__(symbol = u'!', **kwargs)

class Ring(Item):
    wearable = True
    
    def __init__(self, **kwargs):
        super(Ring, self).__init__(symbol = u'=', **kwargs)

class Scroll(Item):
    readable = True
    color = colors.white
    
    def __init__(self, **kwargs):
        super(Scroll, self).__init__(symbol = u'?', **kwargs)
        
class Spellbook(Item):
    readable = True
    
    def __init__(self, **kwargs):
        super(Spellbook, self).__init__(symbol = u'+', **kwargs)
        
class Wand(Item):
    zappable = True
    
    def __init__(self, **kwargs):
        super(Wand, self).__init__(symbol = u'/', **kwargs)

class Weapon(Item):
    wieldable = True
    
    def __init__(self, **kwargs):
        super(Weapon, self).__init__(symbol = u')', **kwargs)

class MacGuffin(Item):
    color = colors.colorSteel
    description = u"Mystic MacGuffin"
    
    def __init__(self, **kwargs):
        super(MacGuffin, self).__init__(symbol = u'^', **kwargs)

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

