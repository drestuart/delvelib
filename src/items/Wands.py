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
    
    color = colors.colorSteel
    description = "wand of lightning"
    
    def __init__(self, **kwargs):
        super(LightningWand, self).__init__(**kwargs)
        

weights = {
           LightningWand : 10
           }