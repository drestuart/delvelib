'''
Created on Jan 19, 2014
Retrieved from: https://gist.github.com/jdp/1687840#file_astar.py

Copyright (C) 2012 Justin Poliey <justin.d.poliey@gmail.com>
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from math import sqrt
from itertools import product
import Const as C

class AStar(object):
    def __init__(self, graph):
        self.graph = graph
        
    def heuristic(self, node, start, end):
        raise NotImplementedError
        
    def search(self, start, end):
        openset = set()
        closedset = set()
        current = start
        openset.add(current)
        while openset:
            current = min(openset, key=lambda o:o.g + o.h)
            if current == end:
                path = []
                while current.parent:
                    path.append(current)
                    current = current.parent
                path.append(current)
                return path[::-1]
            openset.remove(current)
            closedset.add(current)
            for node in self.graph[current]:
                if node in closedset:
                    continue
                if node in openset:
                    new_g = current.g + current.move_cost(node)
                    if node.g > new_g:
                        node.g = new_g
                        node.parent = current
                else:
                    node.g = current.g + current.move_cost(node)
                    node.h = self.heuristic(node, start, end)
                    node.parent = current
                    openset.add(node)
        return None
 
class AStarNode(object):
    def __init__(self):
        self.g = 0
        self.h = 0
        self.parent = None
        
    def move_cost(self, other):
        raise NotImplementedError

class AStarGrid(AStar):
    def heuristic(self, node, start, end):
        return sqrt((end.x - node.x)**2 + (end.y - node.y)**2)
 
class AStarGridNode(AStarNode):
    def __init__(self, x, y):
        self.x, self.y = x, y
        super(AStarGridNode, self).__init__()
 
    def move_cost(self, other):
        diagonal = abs(self.x - other.x) == 1 and abs(self.y - other.y) == 1
        return C.DIAGONALCOST if diagonal else C.HVCOST

def make_graph(mapinfo, blocked):
    nodes = [[AStarGridNode(x, y) for y in range(mapinfo["height"])] for x in range(mapinfo["width"])]
    graph = {}
    for x, y in product(range(mapinfo["width"]), range(mapinfo["height"])):
        node = nodes[x][y]
        graph[node] = []
        for i, j in product([-1, 0, 1], [-1, 0, 1]):
            if not (0 <= x + i < mapinfo["width"]): continue
            if not (0 <= y + j < mapinfo["height"]): continue
            if blocked[x][y] and blocked[x+i][y+j]: continue
            graph[nodes[x][y]].append(nodes[x+i][y+j])
    return graph, nodes


def main():
    blocked = []
    width = 8
    height = 8
    
    for dummyx in range(width):
            newCol = []
            for dummyy in range(height):
                newCol.append(False)
            blocked.append(newCol)
    
    blocked[3][3] = True
    blocked[2][2] = True
#    print blocked
#    exit()   
    
    graph, nodes = make_graph({"width": width, "height": height}, blocked)
    paths = AStarGrid(graph)
    start, end = nodes[1][1], nodes[5][7]
    path = paths.search(start, end)
    path = [(node.x, node.y) for node in path]
    if path is None:
        print "No path found"
    else:
        print "Path found:"
        print path
#        for node in path:
#            print node.x, node.y
        
        
if __name__ == '__main__':
    main()

