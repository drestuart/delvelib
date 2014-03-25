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
import bline

class VMapRegion(object):
	
	def __init__(self, x, y, symb):
		self.memberPoints = []
		self.symbol = symb
		self.centerPoint = x, y
		self.x = x
		self.y = y
		
	def distance(self, tox, toy):
		return math.hypot(self.x - tox, self.y - toy)
	
	def addPoint(self, x, y):
		self.memberPoints.append((x, y))
		
	def containsPoint(self, x, y):
		return (x, y) in self.memberPoints

class VMap(object):
	
	def __init__(self, width, height, num_cells, mask = None):
		self.width = width
		self.height = height
		self.num_cells = num_cells
		self.mask = mask
		self.vmap = ""
		self.centerPoints = []
		self.adjacency = {}
		self.regions = []
		self.pointsToRegions = {}
	
	def generate_voronoi_map(self, use_symbols = False):

		symbols = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')',
				   '.', ',', '<', '>', '?', ':', '|', '{', ']', '+']
		centerPoints = []
		vmap = ""
		
		for i in range(self.num_cells):
			while True:
				randx = random.randrange(self.width)
				randy = random.randrange(self.height)
				
				# Make sure the random point is not excluded by the mask
				if self.mask and not self.mask[randx][randy]:
					continue
				
				# Make sure this isn't a duplicate point!
				if (randx, randy) in centerPoints:
					continue
				
				if use_symbols:
					symb = symbols[i]
				else:
					symb = str(i)
	
				centerPoints.append((randx, randy))
				newRegion = VMapRegion(randx, randy, symb)
				self.regions.append(newRegion)
				break

		for y in range(self.height):
			for x in range(self.width):
				dmin = math.hypot(self.width-1, self.height-1)
				closestRegion = None
				for reg in self.regions:
					d = reg.distance(x, y)
					if d < dmin:
						closestRegion = reg
						dmin = d
				
				vmap += closestRegion.symbol + " "
				closestRegion.addPoint(x, y)
				self.pointsToRegions[(x, y)] = closestRegion
					
			vmap += "\n"
			
		self.centerPoints = centerPoints
		self.vmap = vmap
		return centerPoints, vmap
	
	def getAdjacency(self):
		# Initialize adjacency matrix
		for reg in self.regions:
			self.adjacency[reg] = set()
			
		for y in range(self.height):
			for x in range(self.width):
				
				thisReg = self.pointsToRegions[(x,y)]
				for i in (-1, 0, 1):
					for j in (-1, 0, 1):
						if (i == 0 and j == 0):
							continue
						if (x + i < 0 or y + j < 0 or x + i > self.width-1 or y + j > self.height-1):
							continue
						
						adjReg = self.pointsToRegions[(x + i, y + j)]
						if not (adjReg is thisReg):
							self.adjacency[thisReg].add(adjReg)
							self.adjacency[adjReg].add(thisReg)
							
		return self.adjacency

	def getAdjacentRegions(self, reg):
		return self.adjacency[reg]
	
	def printAdjacency(self):
		for key, values in self.adjacency.iteritems(): 
			print key.symbol, "=> [",
			for v in values:
				print v.symbol,
			print "]\n"
		

def main():
	
	vmapObj = VMap(50, 50, 20)
	points, vmap = vmapObj.generate_voronoi_map(True)
	vmapObj.getAdjacency()
	
	print "Done!\n"
	print points
	print "\n"
	print vmap
	print "\n"
	vmapObj.printAdjacency()


if __name__ == '__main__':
	main()
