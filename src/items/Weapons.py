'''
Created on Mar 23, 2013

@author: dstu
'''

import ItemClass as I
import colors
from randomChoice import weightedChoice


def getRandomWeapon():
    weaponClass = weightedChoice(weights)
    return weaponClass()

class Longsword(I.Weapon):
    
    __mapper_args__ = {
        'polymorphic_identity':'longsword'
    }
    
    def __init__(self, **kwargs):
        super(Longsword, self).__init__(color = colors.colorSteel, description = "longsword", **kwargs)
        
        
weights = {
           Longsword : 10
           }