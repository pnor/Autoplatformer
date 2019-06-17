from abc import ABC, abstractmethod

import pygame

from Entities.Entity import Entity
from Map.GameMap import *


"""
Components for Entities. Components define the traits of all entities in the game, based on what is stored in an Entity's componenet list
"""

class Component(ABC):
    """ Abstraction of the basic component. All components have an owner and an update method"""
    
    def __init__(self, owner):
        assert isinstance(owner, Entity), 'owner is of type ' + str(type(owner)) + ' which is not a subclass of Entity'
        self.owner = owner

    @abstractmethod
    def update(self, delta):
        """ Update entity using information stored in component"""
        pass


class CollisionComponent(Component):
    """ Allows Entities to collide with other entities with Collision Components"""

    def __init__(self, owner):
        super().__init__(owner)

    def update(self, delta):
        # Check collision with world
        # Check collision with other entities 
        map_data = GameMap.map_data 
        body = self.owner.rect
        TILE_SIZE = map_data.tilewidth

        tile_origin = (int(body.topleft[0] / TILE_SIZE), int(body.topleft[1] / TILE_SIZE))
        tiles_width = int(body.topright[0] / TILE_SIZE) - tile_origin[0] 
        tiles_height = int(body.bottomleft[1] / TILE_SIZE) - tile_origin[1] 
        # print('tile origin: ' + str(tile_origin))
        # print('tiles width: ' + str(tiles_width))
        # print('tiles heigh: ' + str(tiles_height))

        for i in range(tile_origin[0], tile_origin[0] + tiles_width):
            for j in range(tile_origin[1], tile_origin[1] + tiles_height):
                print('checking tile ' + str((i, j)))
                properties = GameMap.get_tile_properties(i, j)
                print(properties)

                if not properties: return
                # Walls
                if properties.get(MapInfo.WALL.value):
                    print('Near: Wall')
                    bbox = pygame.Rect((i * TILE_SIZE, j * TILE_SIZE), (TILE_SIZE, TILE_SIZE))
                    if bbox.colliderect(self.owner.rect):
                        print('COLLISION')
                # Floor
                elif properties.get(MapInfo.FLOOR.value):
                    print('Near: Floor')
                    # bbox = 

                # Semisolid Platform
                elif properties.get(MapInfo.SEMISOLID.value):
                    print('Near: Semisolid Platform')

                 
class GravityComponent(Component):
    """ Allows Entities to experience the effects of gravity"""

    def __init__(self, owner):
        super().__init__(owner)

    def update(self, delta):
        # Change acceleration when in air and reset it when on ground
        pass

class PlayerComponent(Component):
    """ Component for player entity, handling all abilities a player can do"""

    def __init__(self, owner):
        super().__init__(self, owner)

    def update(self, delta, buttons):
        # Update with player keypresses
        pass

    def jump(self, spin=False):
        pass

    def move(self, run=False):
        pass
    
    def crouch(self):
        pass
