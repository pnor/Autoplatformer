from abc import ABC, abstractmethod

import pygame
from pygame.math import Vector2
from enum import Enum

from Entities.Entity import Entity
from Map.GameMap import *
from Input.Buttons import Buttons


"""
Components for Entities. Components define the traits of all entities in the game, based on what is stored in an Entity's componenet list
"""

class Component(ABC):
    """ Abstraction of the basic component. All components have an owner and an update method"""

    
    def __init__(self, owner):
        assert isinstance(owner, Entity), 'owner is of type ' + str(type(owner)) + ' which is not a subclass of Entity'
        self.owner = owner
        # Set id type of subclass so it can be used key for Entity's map
        print('!')
        self.__set_id_class()

    @abstractmethod
    def update(self, delta):
        """ Update entity using information stored in component"""
        pass

    @classmethod
    def __set_id_class(cls):
        """ Sets the id_class of the subclass Component object with the class object of the Component
        """
        cls.id_class = cls

    @classmethod
    @property
    def id_class(cls):
        """
        Return class object of the Component. Used to identify Components and retrieve components from
        an Entity's Component dict without instantiating a new one each time
        """
        return cls.id_class
            

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
        # print('owner size: ' + str(owner_body.size))
        owner_top_bbox_bottom = owner_body.top - bbox.bottom  
        owner_bottom_bbox_top = bbox.top - owner_body.bottom
        # print('owner top - bbox bottom: ' + str(owner_top_bbox_bottom))
        # print('owner bottom- bbox top: ' + str(owner_bottom_bbox_top))
        # Top Collision
        if owner_top_bbox_bottom < 0 and -owner_top_bbox_bottom < bbox.height * 0.2:
            # print('TOP COLLISION') 
            fix_vector.y = -owner_top_bbox_bottom

        # Bottom Collision
        elif owner_bottom_bbox_top < 0 and -owner_bottom_bbox_top < bbox.height * 0.2:
            # print('BOTTOM COLLISION') 
            fix_vector.y = owner_bottom_bbox_top

        # X-componenet
        owner_left_bbox_right = owner_body.left - bbox.right
        owner_right_bbox_left = bbox.left - owner_body.right
        # Left Collision
        if owner_left_bbox_right < 0 and -owner_left_bbox_right < bbox.width * 0.2:
            # print('LEFT COLLISION')
            fix_vector.x = -owner_left_bbox_right
        # Right Collision
        elif owner_right_bbox_left < 0 and -owner_right_bbox_left < bbox.width * 0.2:
            # print('RIGHT COLLISION')
            fix_vector.x = owner_right_bbox_left 

        return fix_vector


                 
class GravityComponent(Component):
    """ Allows Entities to experience the effects of gravity."""

    GRAVITY = 9.8 * 8

    def __init__(self, owner):
        super().__init__(owner)
        # Whether the player is on solid ground or in freefall
        self.state = GravityCompState.AIR
        # Used to make sure gravity is only applied once when leaving the ground 
        self.should_apply_gravity = True 
        self.debug = -1000000 

    def left_ground(self):
        """
        Updates status of component if owner has done something to leave ground
        """
        self.state = GravityCompState.AIR
        self.should_apply_gravity = True

    def entered_ground(self):
        """
        Updates status of component if owner has done something to now be on the ground
        """
        self.state = GravityCompState.GROUND
        self.should_apply_gravity = False

    def update(self, delta):
        self.debug+=1
        if self.debug % 20 == 0:
            print(self.state)

        # Get floor tile
        TILE_SIZE = GameMap.map_data.tilewidth
        player_tile_x = int(self.owner.rect.midbottom[0] / TILE_SIZE)
        player_tile_y = int((self.owner.rect.midbottom[1] + 5) / TILE_SIZE)
        try:
            properties = GameMap.get_tile_properties(player_tile_x, player_tile_y)
        except:
            print('Out of Bounds check for Gravity Comp...')
            properties = None

        # Air -> Ground
        if self.state == GravityCompState.AIR:
            if properties and (properties.get(MapInfo.SOLID.value) or properties.get(MapInfo.SEMISOLID.value)):
                print('ON GROUND!')
                self.entered_ground()
                 
        # Ground -> Air
        elif self.state == GravityCompState.GROUND:
            if not properties:
                print('Midair now') 
                self.left_ground()
                

        # If in the air, and needs to apply gravity
        if self.state == GravityCompState.AIR and self.should_apply_gravity:
            print('Applying Gravity!')
            self.owner.acceleration.y = self.GRAVITY
            self.should_apply_gravity = False 
        # If on the ground
        elif self.state == GravityCompState.GROUND and self.owner.acceleration.y > 0:
            # print('Stopping Accel from Gravity')
            self.owner.acceleration.y = 0 
            self.should_apply_gravity = False

class GravityCompState(Enum): 
    """ Tells the state of an entity. (Used with Gravity Component)"""
    AIR = 'air'
    GROUND = 'ground'

    def __eq__(self, other):
        return self.value == other.value

class PlayerComponent(Component):
    """ Component for player entity, handling all abilities a player can do"""

    def __init__(self, owner):
        super().__init__(owner)
        # Player State
        self.player_state = PlayerState.STAND
        self.power_up = PowerUp.NORMAL
        # Player Constants
        self.MAX_RUN_SPEED = 150 
        self.MAX_WALK_SPEED = 50
        self.WALK_ACCELERATION = 50
        self.RUN_ACCELERATION = 100
        self.JUMP_POWER = -60
        self.TRACTION = 50 
        # Set Player Entity Constants
        self.owner.target_x_speed = self.MAX_RUN_SPEED
        # Create Buttons list (!) should be set before update is called
        self.buttons = [] 

    def update(self, delta):
        # Update with player keypresses
        # Movement
        if self.buttons[Buttons.MOVE_LEFT.value]:
            if self.buttons[Buttons.RUN.value]:
                self.move(True, run=True)
            else:
                self.move(True, run=False)
        if self.buttons[Buttons.MOVE_RIGHT.value]:
            if self.buttons[Buttons.RUN.value]:
                self.move(False, run=True)
            else:
                self.move(False, run=False)
        # Apply Traction if player is not moving to kill acceleration
        if not (self.buttons[Buttons.MOVE_LEFT.value] or self.buttons[Buttons.MOVE_RIGHT.value]):
            if self.owner.components[GravityComponent].state == GravityCompState.GROUND:
                self.apply_traction()
        # Crouch
        if self.buttons[Buttons.CROUCH.value]:
            print('crouch')
            self.crouch()
        # Jumps
        if self.buttons[Buttons.JUMP.value]:
            self.jump(spin=False)
        if self.buttons[Buttons.SPIN.value]:
            self.jump(spin=True)
            
    def jump(self, spin=False):
        """
        Makes the player jump.
        :param spin: whether the player will do a spin jump
        """
        self.owner.velocity.y = self.JUMP_POWER
        self.owner.components[GravityComponent.id_class].left_ground()
        self.player_state = PlayerState.JUMP

    def move(self, left, run=False):
        """
        Makes the player move
        :param left: True if the player will move left. False otherwise 
        :param run: Boolean for whether the player will run instead of walk
        """
        self.owner.target_x_speed = self.MAX_RUN_SPEED if run else self.MAX_WALK_SPEED
        if left:
            self.owner.acceleration.x = -self.RUN_ACCELERATION if run else -self.WALK_ACCELERATION
        else:
            self.owner.acceleration.x = self.RUN_ACCELERATION if run else self.WALK_ACCELERATION               

    def apply_traction(self):
        """
        Makes the player slow to a stop when not moving
        """
        # self.owner.target_x_speed = 0
        tolerance = 0.5
        if self.owner.velocity.x < -tolerance:
            self.owner.acceleration.x = self.TRACTION
        elif self.owner.velocity.x > tolerance:
            self.owner.acceleration.x = -self.TRACTION
        else:
            self.owner.acceleration.x = 0
    
    def crouch(self):
        pass

class PlayerState(Enum):
    """ What the player is doing"""
    STAND = 0
    WALK = 1
    RUN = 2
    JUMP = 3
    SPIN = 4

class PowerUp(Enum):
    """ Power Up player has"""
    SMALL = 0
    NORMAL = 1
    LASER = 2
