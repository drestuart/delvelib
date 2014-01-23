'''
Created on Mar 14, 2013

@author: dstu
'''

import math

def get_key(key):
    '''
    A convenience method for libtcod's draconian keyboard support
    '''
    raise Exception("Deprecated Util.get_key")
    
#     if key.vk == libtcod.KEY_CHAR:
#         return chr(key.c)
#     else:
#         return key.vk

def ManhattanDistance(x1, x2, y1, y2):
    return abs(x1-x2) + abs(y1-y2)

def ChebyshevDistance(x1, x2, y1, y2):
    return max(abs(x1-x2), abs(y1-y2))

def getAngle(fromPoint, toPoint):
    fromx, fromy = fromPoint
    tox, toy = toPoint
    
    vec = tox - fromx, toy - fromy
    ang = math.degrees(math.atan2(vec[1], vec[0]))
    if ang < 0:
        ang = ang + 360
    return ang

directionNames = {
                    (0, 11.25) : 'east',
                    (11.25, 33.75) : 'east-northeast',
                    (33.75, 56.25) : 'northeast',
                    (56.25, 78.75) : 'north-northeast',
                    (78.75, 101.25) : 'north',
                    (101.25, 123.75) : 'north-northwest',
                    (123.75, 146.25) : 'northwest',
                    (146.25, 168.75) : 'west-northwest',
                    (168.75, 191.25) : 'west',
                    (191.25, 213.75) : 'west-southwest',
                    (213.75, 236.25) : 'southwest',
                    (236.25, 258.75) : 'south-southwest', 
                    (258.75, 281.25) : 'south',
                    (281.25, 303.75) : 'south-southeast',
                    (303.75, 326.25) : 'southeast', 
                    (326.25, 348.75) : 'east-southeast',
                    (348.75, 360) : 'east'
                  }

def getDirectionName(fromPoint, toPoint):
    angle = getAngle(fromPoint, toPoint)
    return getDirectionNameFromAngle(angle)
    
    
def getDirectionNameFromAngle(angle):
    for (mina, maxa), name in directionNames.items():
        if angle >= mina and angle < maxa:
            return name

def main():
    print getDirectionName((10, 10), (10,11))
    
    
if __name__ == '__main__':
    main()
    
    
    
    
    
    
    