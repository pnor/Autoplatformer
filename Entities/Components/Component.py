from abc import ABC, abstractmethod
from autoplatformer import MainGame
from Entities.Entity import Entity
from Map.GameMap import *

"""
Components for Entities. Copmonents define the traits of all entities in the game, based on what is stored in an Entity's componenet list
"""

class Component(ABC):
    """ Abstraction of the basic component. All components have an owner and an update method"""
    
    def __init__(self, owner):
        assert issubclass(owner, Entity)
        self.owner = owner

    @abstractmethod
    def update(self, delta):
        """ Update entity using information stored in component"""
        pass


class CollisionComponent(Component):
    """ Allows Entities to collide with other entities with Collision Components"""

    def __init__(self, owner):
        super.__init__(owner)

    def update(self, delta):
        # Check collision with world
        # Check collision with other entities 
        map_data = MainGame.map_data 
        body = self.owner.rect
        TILE_SIZE = map_data.tilewidth

        tile_origin = (int(body.topleft[0] / TILE_SIZE), int(body.topleft[1] / TILE_SIZE))
        tiles_width = int(body.topright[0] / TILE_SIZE) - tile_origin[0] 
        tiles_height = int(body.bottomleft[1] / TILE_SIZE) - tile_origin[1] 

        for i in range(tile_origin[0], tiles_width):
            for j in range(tile_origin[1], tiles_height):
                properties = GameMap.get_properties(i, j)
                # Walls
                # Floor
                 

class GravityComponent(Component):
    """ Allows Entities to experience the effects of gravity"""

    def __init__(self, owner):
        super.__init__(owner)

    def update(self, delta):
        # Change acceleration when in air and reset it when on ground
        pass

class PlayerComponent(Component):
    """ Component for player entity, handling all abilities a player can do"""

    def __init__(self, owner):
        super.__init__(owner)

    def update(self, delta, buttons):
        # Update with player keypresses
        pass

    def jump(self, spin=False):
        pass

    def move(self, run=False):
        pass
    
    def crouch(self):
        pass


