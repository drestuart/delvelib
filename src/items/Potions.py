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
    
    __mapper_args__ = {
        'polymorphic_identity':'petty_healing_potion'
    }
    
    def __init__(self, **kwargs):
        super(PettyHealingPotion, self).__init__(color = colors.lightBlue, description = "potion of petty healing", **kwargs)
        
        
class ModerateHealingPotion(I.Potion):
    
    __mapper_args__ = {
        'polymorphic_identity':'moderate_healing_potion'
    }
    
    def __init__(self, **kwargs):
        super(ModerateHealingPotion, self).__init__(color = colors.blue, description = "potion of moderate healing", **kwargs)
        

class ColossalHealingPotion(I.Potion):
    
    __mapper_args__ = {
        'polymorphic_identity':'colossal_healing_potion'
    }
    
    def __init__(self, **kwargs):
        super(ColossalHealingPotion, self).__init__(color = colors.darkBlue, description = "potion of colossal healing", **kwargs)
        
        
class PoisonPotion(I.Potion):
    
    __mapper_args__ = {
        'polymorphic_identity':'poison_potion'
    }
    
    def __init__(self, **kwargs):
        super(PoisonPotion, self).__init__(color = colors.red, description = "potion of poison", **kwargs)
        
        
weights = {
           PettyHealingPotion : 30,
           ModerateHealingPotion : 20,
           ColossalHealingPotion : 10,
           PoisonPotion : 15
           }