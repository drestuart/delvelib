'''
##########################################################
#
# Voronoi map library.
# Adapted from: http://rosettacode.org/wiki/Voronoi_diagram#Python
# Retrieved 1/15/2014
# Modified by Dan Stuart
#
##########################################################
'''

import random
import math

def generate_voronoi_map(width, height, num_cells, use_symbols = False):
	imgx, imgy = width, height
	nx = []
	ny = []
	symbols = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')',
			   '.', ',', '<', '>', '?', ':', '|', '{', ']', '+']
	points = []
	vmap = ""
	for i in range(num_cells):
		randx = random.randrange(imgx)
		randy = random.randrange(imgy)
		
		nx.append(randx)
		ny.append(randy)
		points.append((randx,randy))
		
	for y in range(imgy):
		for x in range(imgx):
			dmin = math.hypot(imgx-1, imgy-1)
			j = -1
			for i in range(num_cells):
				d = math.hypot(nx[i]-x, ny[i]-y)
				if d < dmin:
					dmin = d
					j = i
			if use_symbols:
				vmap += symbols[j] + " "
			else:
				vmap += str(j) + " "
				
		vmap += "\n"
	return points, vmap

def main():
	
	points, vmap = generate_voronoi_map(50, 50, 20, True)
	
	print "Done!\n"
	print points
	print "\n"
	print vmap


if __name__ == '__main__':
	main()
