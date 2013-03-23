'''
Created on Mar 23, 2013

@author: dstu
'''

import ItemClass as I
import colors
from randomChoice import weightedChoice


def getRandomCoins():
    coinClass = weightedChoice(weights)
    return coinClass()

class Coins(I.Coins):
    def __init__(self, **kwargs):
        super(Coins, self).__init__(color = colors.colorGold, description = "gold coin", **kwargs)
        
        
weights = {
           Coins : 10
           }