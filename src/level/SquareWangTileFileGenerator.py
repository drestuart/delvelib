'''
Created on Jul 21, 2014

@author: dstuart
'''

from itertools import product

# File header parameters
width = 21
height = 21
glyphs = '.~#+'

print "width:", width, "height:", height
print "glyphs:", glyphs
print

numConstraints = 4

prod = product('12', repeat=numConstraints)

for cons in prod:
    constraints = "".join(cons)
    print "*TILE*"
    print "constraints:", constraints
    
    for y in range(height):
        print glyphs[0]*width
    
    print "\n"