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

        # Used to create total collision fix vector
        positive_y = 0
        negative_y = 0
        positive_x = 0
        negative_x = 0

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

                    if bbox.colliderect(owner_body):
                        fix_velocity = self.handle_collision(bbox)
                        negative_x = min(negative_x, fix_velocity.x)
                        positive_x = max(positive_x, fix_velocity.x)
                        negative_y = min(negative_y, fix_velocity.y)
                        positive_y = max(positive_y, fix_velocity.y)
                        # print('x: ' + str(negative_x) + ' - ' + str(positive_x))
                        # print('y: ' + str(negative_y) + ' - ' + str(positive_y))

                # Semisolids 
                elif properties.get(MapInfo.SEMISOLID.value):
                    print('Near: SEMISOLID')
                    # bbox = 
                elif properties.get(MapInfo.SLOPE_LEFT.value):
                   print('Near: SLOPE LEFT') 
                elif properties.get(MapInfo.SLOPE_RIGHT.value):
                    print('Near: SLOPE RIGHT')

        
        # Create collision fix vector
        net_fix_vector =  Vector2(positive_x, positive_y) + Vector2(negative_x, negative_y)

        # Kill velocity if total fix velocity was large enough 
        
        tolerance = 1
        if net_fix_vector.length() > tolerance:
            print('NET FIX VELCOTIY WAS...')
            print(net_fix_vector)
            print('')
            # Apply net fix vector 
            owner_body.left += net_fix_vector.x
            owner_body.top += net_fix_vector.y
            # Kill velocity
            self.owner.velocity.x = 0
            self.owner.velocity.y = 0 
        elif net_fix_vector.length() > 0 :
            print('Was too small to do anything...')
            print('fix vector: ' + str(net_fix_vector))

    def handle_collision(self, bbox):
        """ 
        Resolves collisions by moving the owner
        :param bbox: Bounding box of tile
         REWRITE!
        """
        owner_body = self.owner.rect
        fix_vector = Vector2()

        # Y-component
        # if either are negative, a collision may of happened
        # If either's abs is larger than the height, its NOT a collision 
        print('owner size: ' + str(owner_body.size))
        owner_top_bbox_bottom = owner_body.top - bbox.bottom  
        owner_bottom_bbox_top = bbox.top - owner_body.bottom
        print('owner top - bbox bottom: ' + str(owner_top_bbox_bottom))
        print('owner bottom- bbox top: ' + str(owner_bottom_bbox_top))
        # Top Collision
        if owner_top_bbox_bottom < 0 and -owner_top_bbox_bottom < bbox.height * 0.2:
            print('TOP COLLISION') 
            fix_vector.y = -owner_top_bbox_bottom

        # Bottom Collision
        elif owner_bottom_bbox_top < 0 and -owner_bottom_bbox_top < bbox.height * 0.2:
            print('BOTTOM COLLISION') 
            fix_vector.y = owner_bottom_bbox_top

        # X-componenet
        owner_left_bbox_right = owner_body.left - bbox.right
        owner_right_bbox_left = bbox.left - owner_body.right
        # Left Collision
        if owner_left_bbox_right < 0 and -owner_left_bbox_right < bbox.width * 0.2:
            print('LEFT COLLISION')
            fix_vector.x = -owner_left_bbox_right
        # Right Collision
        elif owner_right_bbox_left < 0 and -owner_right_bbox_left < bbox.width * 0.2:
            print('RIGHT COLLISION')
            fix_vector.x = owner_right_bbox_left 

        return fix_vector


                 
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
                    # print('ON GROUND!')
                    self.state = GravityCompState.GROUND
                    self.applied_gravity = False
            except: # Out of Bounds
                pass
                # print('x: ' + str(player_tile_x)) 
                # print('y: ' + str(player_tile_y + 1))
                # print('Out of Bounds check in Grav') # Update Acceleration for ground/air

        if self.state == GravityCompState.AIR and not self.applied_gravity:
            print('Applying Gravity!')
            self.owner.acceleration.y = 9.8
            self.applied_gravity = True
        elif self.state == GravityCompState.GROUND:
            # print('Stopping Accel from Gravity')
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
