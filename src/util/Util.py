'''
Created on Mar 14, 2013

@author: dstu
'''

import math
import PIL.Image
import Const as C

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

def readTemplateFile(path): 
    
    templateFile = open(path, 'r')
    templates = []
    temp = []
    
    def addTemplate(temp):
        templates.append(temp)
        templates.append(rotateCW(temp))
        templates.append(rotateCCW(temp))
        templates.append(rotateCCW(rotateCCW(temp)))
        
    for line in templateFile.readlines():
        line = line.strip()
        
        if line == '':
            if temp:
                # If we've reached the end of a template, add it and its rotations
                addTemplate(temp)
            temp = []
        else:
            temp.append(line)
        
    templateFile.close()
    
    if temp:
        # Add the last one if we haven't already
        addTemplate(temp)
    
    return templates

def readTemplateImage(path, colormap):
    img = PIL.Image.open(path)
    rgb_im = img.convert('RGB')
    
    sizex, sizey = rgb_im.size
    
    assert sizex, sizey == (C.WORLD_MAP_WIDTH, C.WORLD_MAP_HEIGHT)
    
    emap = []

    for y in range(sizey):
        row = []
        for x in range(sizex):
            color = rgb_im.getpixel((x,y))
            symbol = '!'
            if color in colormap:
                symbol = colormap[color]
            else:
                raise ValueError("Bad color value: " + str(color))
    
            row.append(symbol)
        emap.append(row)
        
    assert len(emap[0]), len(emap) == (C.WORLD_MAP_WIDTH, C.WORLD_MAP_HEIGHT)
    
    return emap
    
def twoDArray(width, height, val=True):
    '''Initialize a 2-D array with values val'''
    arr = []
        
    for dummyx in range(width):
        newCol = []
        for dummyy in range(height):
            newCol.append(val)
        arr.append(newCol)
    
    return arr

def rotateCW(arr):
    rot = zip(*arr[::-1])
    retArr = []
    for row in rot:
        retArr.append(''.join(row))
    return retArr

def rotateCCW(arr):
    rot = zip(*arr)[::-1]
    retArr = []
    for row in rot:
        retArr.append(''.join(row))
    return retArr
    
def printArray(arr):
    for row in arr:
        rowStr = ''
        for item in row:
            rowStr += str(item)
        print rowStr
    print

def main():
    arr = [ '*...++...$',
            '....++....',
            '++++++++++',
            '....++....',
            '?...++...!']
    cw = rotateCW(arr)
    ccw = rotateCCW(arr)
    
    printArray(arr)
    printArray(cw)
    printArray(ccw)


if __name__ == '__main__':
    main()

    