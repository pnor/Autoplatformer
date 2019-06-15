"""
Classes related to the game map.
"""


import constants
from pytmx.util_pygame import load_pygame
from enum import Enum

class GameMap(object):
    map_data = None
    MAIN_LAYER_INDEX = 0

    def set_up_map():
        GameMap.map_data = load_pygame(constants.SIMPLE_MAP)
        print('map data is ' + str(GameMap.map_data))

        # Set main layer of tmx map
        for i, layer in enumerate(GameMap.map_data):
            GameMap.MAIN_LAYER_INDEX = i if layer.properties.get(MapInfo.MAIN.value) else None

    def get_tile_properties(row, col):
        """
        Returns: Tile properties for tile in the main game layer
        """
        print('row: ' + str(row))
        print('col: ' + str(col))
        print('layer: ' + str(GameMap.MAIN_LAYER_INDEX))
        return GameMap.map_data.get_tile_properties(row, col, GameMap.MAIN_LAYER_INDEX)



class MapInfo(Enum):
    """ Property values used to get information from map
    """
    MAIN = 'main' # Main layer of tilemap

    SPAWN = 'spawn'
    FLOOR = 'floor'
    WALL = 'wall'
    SEMISOLID = 'semisolid'