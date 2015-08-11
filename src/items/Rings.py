'''
Created on Mar 23, 2013

@author: dstu
'''

import ItemClass as I
import colors
from randomChoice import weightedChoice

def getRandomRing():
    ringClass = weightedChoice(weights)
    return ringClass()

class ProtectionRing(I.Ring):
    color = colors.darkMagenta
    itemType = "ring_protection"
    description = "ring of protection"
    
    def __init__(self, **kwargs):
        super(ProtectionRing, self).__init__(**kwargs)
        
        
weights = {
           ProtectionRing : 10
           }