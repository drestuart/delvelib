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
    
    color = colors.lightBlue
    description = "potion of petty healing"
    
    def __init__(self, **kwargs):
        super(PettyHealingPotion, self).__init__(**kwargs)
        
        
class ModerateHealingPotion(I.Potion):
    
    color = colors.blue
    description = "potion of moderate healing"
    
    def __init__(self, **kwargs):
        super(ModerateHealingPotion, self).__init__(**kwargs)
        

class ColossalHealingPotion(I.Potion):
    
    color = colors.darkBlue
    description = "potion of colossal healing"
    
    def __init__(self, **kwargs):
        super(ColossalHealingPotion, self).__init__(**kwargs)
        
        
class PoisonPotion(I.Potion):
    
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