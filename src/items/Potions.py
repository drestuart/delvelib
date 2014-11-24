'''
Created on Mar 23, 2013

@author: dstu
'''

import ItemClass as I
import colors
from randomChoice import weightedChoice

def getRandomPotion():
    potClass = weightedChoice(weights)
    return potClass()
    

class PettyHealingPotion(I.Potion):
    
    __mapper_args__ = {'polymorphic_identity':u'petty_healing_potion'}
    color = colors.lightBlue
    description = "potion of petty healing"
    
    def __init__(self, **kwargs):
        super(PettyHealingPotion, self).__init__(**kwargs)
        
        
class ModerateHealingPotion(I.Potion):
    
    __mapper_args__ = {'polymorphic_identity':u'moderate_healing_potion'}
    color = colors.blue
    description = "potion of moderate healing"
    
    def __init__(self, **kwargs):
        super(ModerateHealingPotion, self).__init__(**kwargs)
        

class ColossalHealingPotion(I.Potion):
    
    __mapper_args__ = {'polymorphic_identity':u'colossal_healing_potion'}
    color = colors.darkBlue
    description = "potion of colossal healing"
    
    def __init__(self, **kwargs):
        super(ColossalHealingPotion, self).__init__(**kwargs)
        
        
class PoisonPotion(I.Potion):
    
    __mapper_args__ = {'polymorphic_identity':u'poison_potion'}
    color = colors.red
    description = "potion of poison"
    
    def __init__(self, **kwargs):
        super(PoisonPotion, self).__init__(**kwargs)
        
        
weights = {
           PettyHealingPotion : 30,
           ModerateHealingPotion : 20,
           ColossalHealingPotion : 10,
           PoisonPotion : 15
           }