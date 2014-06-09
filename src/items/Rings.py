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
    
    __mapper_args__ = {
        'polymorphic_identity':'protection_ring'
    }
    color = colors.darkMagenta
    
    def __init__(self, **kwargs):
        super(ProtectionRing, self).__init__(description = "ring of protection", **kwargs)
        
        
weights = {
           ProtectionRing : 10
           }