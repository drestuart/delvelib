'''
Created on Jul 21, 2014

@author: dstuart
'''

from itertools import product

# File header parameters
width = 11
height = 22
glyphs = '#,+.'

print "width:", width, "height:", height
print "glyphs:", glyphs
print

numConstraints = 6

prod = product('12', repeat=numConstraints)

for cons in prod:
    constraints = "".join(cons)
    print "*TILE*"
    print "constraints:", constraints
    
    tile = []
    
    for y in range(height):
        tile.append([glyphs[0]]*width)
        
    # Apply constraints
    # G:
    if constraints[0] == '1':
        tile[height/4][0] = glyphs[1]
    else:
        tile[height/8][0] = glyphs[1]
    
    # H:
    if constraints[0] == '1':
        tile[0][width/2] = glyphs[1]
    else:
        tile[0][width/4] = glyphs[1]
    
    # I:
    if constraints[0] == '1':
        tile[height/4][width - 1] = glyphs[1]
    else:
        tile[height/8][width - 1] = glyphs[1]
    
    # J:
    if constraints[0] == '1':
        tile[3*height/4][width - 1] = glyphs[1]
    else:
        tile[7*height/8][width - 1] = glyphs[1]
    
    # K:
    if constraints[0] == '1':
        tile[height - 1][width/2] = glyphs[1]
    else:
        tile[height - 1][3*width/4] = glyphs[1]
    
    # L:
    if constraints[0] == '1':
        tile[3*height/4][0] = glyphs[1]
    else:
        tile[7*height/8][0] = glyphs[1]
    
    
    for y in range(height):
        print "".join(tile[y])
    
    print "\n"