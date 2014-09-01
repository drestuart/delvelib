'''
Created on Mar 23, 2013

@author: dstu
'''

import ItemClass as I
import colors
from randomChoice import weightedChoice
#import random

def getRandomCoins():
#    q = random.randint(1, 100)
    q = 5
    coinStack = I.Coins(quantity = q)
    return coinStack