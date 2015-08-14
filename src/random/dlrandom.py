'''
Created on Aug 13, 2015

@author: dstuart
'''

from random import sample

def setChoice(_set):
    return sample(_set, 1)[0]

def setShuffle(_set):
    return sample(_set, len(_set))
