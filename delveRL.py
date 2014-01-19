'''
Created on Mar 10, 2013

@author: dstu
'''

import Game as G
import os


def main():
    x = 100
    y = 50
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)
    
    print '-=delveRL=-'
    
    game = G.Game()
    game.play()



if __name__ == '__main__':
    main()