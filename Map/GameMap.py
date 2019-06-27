"""
Classes related to the game map.
"""


from enum import Enum

from pytmx.util_pygame import load_pygame

import constants


class GameMap(object):
    map_data = None
    MAIN_LAYER_INDEX = None 
    temp_surface = None

    def set_up_map():
        GameMap.map_data = load_pygame(constants.TEST_MAP)
        print('map data is ' + str(GameMap.map_data))

        # Set main layer of tmx map
        for i, layer in enumerate(GameMap.map_data):
            if not GameMap.MAIN_LAYER_INDEX:
                if layer.properties.get(MapInfo.MAIN.value) :
                    GameMap.MAIN_LAYER_INDEX = i  

    def get_tile_properties(row, col):
        """
        Returns: Tile properties for tile in the main game layer
        """
        return GameMap.map_data.get_tile_properties(row, col, GameMap.MAIN_LAYER_INDEX)

    def get_tile(id):
        """ Returns tile corresponding to tile ID """
        return GameMap.map_data



class MapInfo(Enum):
    """ Property values used to get information from map
    """
    MAIN = 'main' # Main layer of tilemap

    SPAWN = 'spawn'
    SOLID = 'solid'
    SEMISOLID = 'semisolid'
    SLOPE_LEFT = 'slope left'
    SLOPE_RIGHT = 'slope right'
