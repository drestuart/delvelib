'''
Created on Mar 23, 2013

@author: dstu
'''

import ItemClass as I
import colors
from randomChoice import weightedChoice


def getRandomWand():
    wandClass = weightedChoice(weights)
    return wandClass()

class LightningWand(I.Wand):
    
    __mapper_args__ = {
        'polymorphic_identity':'lightning_wand'
    }
    color = colors.colorSteel
    
    def __init__(self, **kwargs):
        super(LightningWand, self).__init__(description = "wand of lightning", **kwargs)
        

weights = {
           LightningWand : 10
           }