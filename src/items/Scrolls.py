'''
Created on Mar 23, 2013

@author: dstu
'''

import ItemClass as I
from randomChoice import weightedChoice


def getRandomScroll():
    scrollClass = weightedChoice(weights)
    return scrollClass()

class TeleportationScroll(I.Scroll):
    def __init__(self, **kwargs):
        super(TeleportationScroll, self).__init__(description = "scroll of teleportation", **kwargs)
        

weights = {
           TeleportationScroll : 10
           }