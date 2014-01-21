#!/usr/bin/env python2.7-32

'''
Created on Mar 10, 2013

@author: dstu
'''

import site
import os

site.addsitedir(os.getcwd())
print os.getcwd()

import Game as G

fontsize = 14

def main():
    x = 100
    y = 50
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)
    os.environ['SDL_VIDEODRIVER'] = 'x11'
# x11, dga, fbcon, directfb, ggi, vgl, svgalib, aalib    

    print '-=delveRL=-'
    
    game = G.Game(fontsize = fontsize)
    
    game.play()



if __name__ == '__main__':
    main()
