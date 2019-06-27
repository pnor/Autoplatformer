from abc import ABC, abstractmethod

import pygame
from pygame.math import Vector2
from enum import Enum

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
        owner_body = self.owner.rect
        TILE_SIZE = map_data.tilewidth

        tile_origin_x = int(owner_body.topleft[0] / TILE_SIZE) - 1
        tile_origin_y = int(owner_body.topleft[1] / TILE_SIZE) - 1
        tile_origin_end_x = int(owner_body.topright[0] / TILE_SIZE) + 1 
        tile_origin_end_y = int(owner_body.bottomleft[1] / TILE_SIZE) + 1

        for i in range(tile_origin_x, tile_origin_end_x + 1):
            for j in range(tile_origin_y, tile_origin_end_y + 1):
                # Get tile, skip if not existent/has no property
                try: 
                    properties = GameMap.get_tile_properties(i, j)
                    if not properties: continue
                except:
                    continue

                # Solids 
                if properties.get(MapInfo.SOLID.value):
                    # print('Near: SOLID')
                    bbox = pygame.Rect((i * TILE_SIZE, j * TILE_SIZE), (TILE_SIZE, TILE_SIZE))
                    corrected = False

                    if bbox.colliderect(owner_body):
                        horiz_collided = self.handle_collision(bbox, is_vertical=False)
                        vert_collided = self.handle_collision(bbox, is_vertical=True)
                        corrected = horiz_collided or vert_collided


                    # If solid collision happens, reset velocity
                    if corrected:
                        print('Killing Velocity')
                        self.owner.velocity.x = 0
                        self.owner.velocity.y = 0 

                # Semisolids 
                elif properties.get(MapInfo.SEMISOLID.value):
                    print('Near: SEMISOLID')
                    # bbox = 
                elif properties.get(MapInfo.SLOPE_LEFT.value):
                   print('Near: SLOPE LEFT') 
                elif properties.get(MapInfo.SLOPE_RIGHT.value):
                    print('Near: SLOPE RIGHT')


    def handle_collision(self, bbox, is_vertical=False):
        """ 
        Resolves collisions by moving the owner
        :param bbox: Bounding box of tile
        :param is_vertical: whether the collision being checked is a vertical collision or horizontal 
        collision.
        :return: Boolean whether the owner was changed due to a collision
        """
        owner_body = self.owner.rect

        if is_vertical:
            # Y-component
            # if either are negative, a collision may of happened
            # If either's abs is larger than the height, its NOT a collision 
            owner_top_bbox_bottom = owner_body.top - bbox.bottom  
            owner_bottom_bbox_top = bbox.top - owner_body.bottom
            # Top Collision
            if owner_top_bbox_bottom < 0 and owner_top_bbox_bottom > -owner_body.height:
                print('TOP COLLISION') 
                corrected = True
                new_x = owner_body.left
                new_y = max(owner_body.top, bbox.bottom) 
                owner_body.topleft = (new_x, new_y)
            # Bottom Collision
            elif owner_bottom_bbox_top < 0 and owner_bottom_bbox_top > -owner_body.height:
                print('BOTTOM COLLISION') 
                corrected = True
                new_x = owner_body.left
                new_y = min(owner_body.bottom, bbox.top)
                owner_body.bottomleft = (new_x, new_y) 
        else:
            # X-componenet
            owner_left_bbox_right = owner_body.left - bbox.right
            owner_right_bbox_left = bbox.left - owner_body.right
            # Left Collision
            if owner_left_bbox_right < 0 and owner_left_bbox_right > -owner_body.width:
                print('LEFT COLLISION')
                corrected = True
                new_x = max(owner_body.left, bbox.right) 
                new_y = owner_body.bottom
                owner_body.bottomleft = (new_x, new_y) 
                print('end position: ' + str(owner_body.topleft)) 
            # Right Collision
            elif owner_right_bbox_left < 0 and owner_left_bbox_right > -owner_body.width:
                print('RIGHT COLLISION')
                corrected = True
                new_x = min(owner_body.right, bbox.left) 
                new_y = owner_body.bottom
                owner_body.bottomright = (new_x, new_y) 

                 
class GravityComponent(Component):
    """ Allows Entities to experience the effects of gravity."""

    def __init__(self, owner):
        super().__init__(owner)
        self.state = GravityCompState.AIR
        # Used to make sure gravity is only applied once when leaving the ground 
        self.applied_gravity = False 

    def update(self, delta):
        # Change acceleration when in air and reset it when on ground
        if self.state == GravityCompState.AIR:
            # Get floor tile
            TILE_SIZE = GameMap.map_data.tilewidth
            player_tile_x = int(self.owner.rect.midbottom[0] / TILE_SIZE)
            player_tile_y = GameMap.map_data.height - int(self.owner.rect.midbottom[0] / TILE_SIZE) - 1

            # print('x: ' + str(player_tile_x)) 
            # print('y: ' + str(player_tile_y))
            # Check if on ground tile
            try: 
                properties = GameMap.get_tile_properties(player_tile_x, player_tile_y)
                # print(properties)
                if properties and (properties.get(MapInfo.SOLID.value) or properties.get(MapInfo.SEMISOLID.value)):
                    print('ON GROUND!')
                    self.state = GravityCompState.GROUND
                    self.applied_gravity = False
            except: # Out of Bounds
                print('x: ' + str(player_tile_x)) 
                print('y: ' + str(player_tile_y + 1))
                print('Out of Bounds check in Grav') # Update Acceleration for ground/air

        if self.state == GravityCompState.AIR and not self.applied_gravity:
            print('Applying Gravity!')
            self.owner.acceleration.y = 9.8
            self.applied_gravity = True
        elif self.state == GravityCompState.GROUND:
            print('Stopping Accel from Gravity')
            self.owner.acceleration.y = 0 
            self.state = GravityCompState.AIR
            self.applied_gravity = False
            # TODO change this so it doesnt just reset to AIR. 
            # TODO edit collision to handle multiple blocks in a line

class GravityCompState(Enum): 
    """ Tells the state of an entity. (Used with Gravity Component)"""
    AIR = 'air'
    GROUND = 'ground'

    def __eq__(self, other):
        return self.value == other.value

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
