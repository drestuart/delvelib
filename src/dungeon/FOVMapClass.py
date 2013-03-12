'''
Created on Mar 11, 2013

@author: dstu
'''

class FOVMap():
    '''A map subclass for a creature's Field of View.  Keeps track of what the creature can see, and only updates squares that can be seen.  Reads from its corresponding DungeonLevel object.'''


    def __init__(self, baseMap):
        #super(FOVMap, self).__init__(width, height, name, depth)
        self.__dict__['baseMap'] = baseMap
        self.__dict__['toRecompute'] = True
        
        # Initialize the fov_map object for libtcod
        self.__dict__['fov_map'] = libtcod.map_new(C.MAP_WIDTH, C.MAP_HEIGHT)
        
        self.__dict__['tiles'] = [[ None 
                                    for y in range(self.baseMap.HEIGHT) ]
                                    for x in range(self.baseMap.WIDTH) ]
        
        self.computeFOVProperties()
        
    def getTile(self, coords):
        # Return a tile by coordinates, with a Coordinates object.
        x, y = coords['x'], coords['y']
        return self.tiles[x][y]
    
    def setTile(self, coords, tileIn):
        self.__dict__['tiles'][coords['x']][coords['y']] = copy.deepcopy(tileIn)
        
    def computeFOVProperties(self):
        for y in range(self.baseMap.HEIGHT):
            for x in range(self.baseMap.WIDTH):
                libtcod.map_set_properties(self.fov_map, x, y, 
                                           not self.baseMap.blocksMove(x, y), 
                                           not self.baseMap.blocksSight(x, y))
        
        
    def recompute(self):
        self.__dict__['toRecompute'] = True
        
    def recomputed(self):
        self.__dict__['toRecompute'] = False
                
    def computeFOV(self, position, radius):
        '''Compute the field of view of this map with respect to a particular position'''
        if self.toRecompute == False and self.baseMap.toRecomputeFOV == False:
            return
        else:
            
            self.__dict__['toRecompute'] = False
            
            libtcod.map_compute_fov(self.fov_map, position['x'], position['y'], 
                                radius, C.FOV_LIGHT_WALLS, C.FOV_ALGO)

            self.computeFOVProperties()
            
            self.recomputed()
            self.baseMap.recomputedFOV()
        
    def clear(self, con):
        self.baseMap.clear(con)
        
    def draw(self, con, position, radius):
        self.computeFOV(position, radius)
        
        for x in range(self.baseMap.WIDTH):
            for y in range(self.baseMap.HEIGHT):
                coords = Coordinates(x = x, y = y)
                tile = self.baseMap.getTile(coords)
                
                if libtcod.map_is_in_fov(self.fov_map, x, y):  # We can see this tile
                    symbol, color, background = tile.toDraw()
                    self.setTile(coords, tile)  # Remember this tile
                
                elif self.getTile(coords):  # We've seen this one before
                    symbol = self.getTile(coords).symbol()
                    color = libtcod.dark_grey
                    background = libtcod.light_grey
                        
                else:
                    background = libtcod.BKGND_NONE
                    color = colors.colorDarkGround
                    symbol = ' '
                    
                libtcod.console_set_foreground_color(con, color)
                libtcod.console_put_char(con, x, y, symbol, background)