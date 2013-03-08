'''
Created on May 29, 2012

@author: dstu
'''

__all__ = ['importLibtcod']

import os
import sys

__LTCOD_DIR_MAC = "/Users/dstu/Documents/workspace/delveRL/lib/libtcod"
__LTCOD_DIR_WIN = "C:\\Users\\dstu\\workspace\\delveRL\\lib\\libtcod"

def importLibtcod(directory = None):
    
    if not directory:
        if sys.platform.find('darwin') != -1:
            directory = __LTCOD_DIR_MAC
        else:
            directory = __LTCOD_DIR_WIN
    
    oldWD = os.getcwd()
    os.chdir(directory)
    import libtcodpy as libtcod
    os.chdir(oldWD)
    
    return libtcod

def main():
    importLibtcod()

if __name__ == "__main__":
    main()