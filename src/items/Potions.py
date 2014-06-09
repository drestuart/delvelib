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
    color = colors.lightBlue
    
    def __init__(self, **kwargs):
        super(PettyHealingPotion, self).__init__(description = "potion of petty healing", **kwargs)
        
        
class ModerateHealingPotion(I.Potion):
    
    __mapper_args__ = {
        'polymorphic_identity':'moderate_healing_potion'
    }
    color = colors.blue
    
    def __init__(self, **kwargs):
        super(ModerateHealingPotion, self).__init__(description = "potion of moderate healing", **kwargs)
        

class ColossalHealingPotion(I.Potion):
    
    __mapper_args__ = {
        'polymorphic_identity':'colossal_healing_potion'
    }
    color = colors.darkBlue
    
    def __init__(self, **kwargs):
        super(ColossalHealingPotion, self).__init__(description = "potion of colossal healing", **kwargs)
        
        
class PoisonPotion(I.Potion):
    
    __mapper_args__ = {
        'polymorphic_identity':'poison_potion'
    }
    color = colors.red
    
    def __init__(self, **kwargs):
        super(PoisonPotion, self).__init__(description = "potion of poison", **kwargs)
        
        
weights = {
           PettyHealingPotion : 30,
           ModerateHealingPotion : 20,
           ColossalHealingPotion : 10,
           PoisonPotion : 15
           }