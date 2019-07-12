import time

import pygame
from pygame.math import Vector2
from enum import Enum

from Map.GameMap import *
from Input.Buttons import Buttons
import Util

from Entities.Components.BaseComponents import Component


"""
Components for Entities. Components define the traits of all entities in the game, based on what is stored in an Entity's componenet list
"""

class CollisionComponent(Component):
    """ Allows Entities to collide with other entities with Collision Components"""

    def __init__(self, owner):
        super().__init__(owner)

    def update(self, delta):
        return

        # Check collision with world
        # Check collision with other entities 
        map_data = GameMap.map_data 
        owner_body = self.owner.rect
        TILE_SIZE = map_data.tilewidth

        bboxes = []
        tile_origin_x = int(owner_body.topleft[0] / TILE_SIZE) - 1
        tile_origin_y = int(owner_body.topleft[1] / TILE_SIZE) - 1
        tile_origin_end_x = int(owner_body.topright[0] / TILE_SIZE) + 1 
        tile_origin_end_y = int(owner_body.bottomleft[1] / TILE_SIZE) + 1

        # Used to create total collision fix vector
        positive_y = 0
        negative_y = 0
        positive_x = 0
        negative_x = 0

        for i in range(tile_origin_x, tile_origin_end_x):
            for j in range(tile_origin_y, tile_origin_end_y):
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
                    bboxes.append(bbox)

                    if bbox.colliderect(owner_body):
                        fix_velocity = self.handle_collision(bbox)
                        negative_x = max(negative_x, fix_velocity.x)
                        positive_x = min(positive_x, fix_velocity.x)
                        negative_y = max(negative_y, fix_velocity.y)
                        positive_y = min(positive_y, fix_velocity.y)

                # Semisolids 
                elif properties.get(MapInfo.SEMISOLID.value):
                    print('Near: SEMISOLID')

        
        # Create collision fix vector
        net_fix_vector =  Vector2(positive_x, positive_y) + Vector2(negative_x, negative_y)

        tolerance =  0.3
        if net_fix_vector.length() > tolerance:
            # if net_fix_vector.length() > 30:
            #     print('Was big: Net Fix Vector Was...')
            #     print(net_fix_vector)
            #     print('')
            # Apply net fix vector (and stop velocities)
            # Old Way
            # owner_body.top += net_fix_vector.y
            # owner_body.left += net_fix_vector.x
            # self.owner.velocity.x = 0
            # self.owner.velocity.y = 0

            # Experim Way
            # print(net_fix_vector)
            horiz_larger = net_fix_vector.x >= net_fix_vector.y
            if horiz_larger and self.owner.velocity.x > tolerance or self.owner.velocity.x < -tolerance:
                owner_body.top += net_fix_vector.y
                if net_fix_vector.y > 0:
                    self.owner.velocity.y = 0
                if bbox and owner_body.collidelistall(bboxes): # If still colliding, do x
                    owner_body.left += net_fix_vector.x
                    self.owner.velocity.x = 0
            elif self.owner.velocity.y > tolerance or self.owner.velocity.y < -tolerance:
                owner_body.left += net_fix_vector.x
                if net_fix_vector.x > 0:
                    self.owner.velocity.x = 0
                if bbox and owner_body.collidelistall(bboxes): # If still colliding, do x
                    owner_body.top += net_fix_vector.y
                    self.owner.velocity.y = 0

            
            if bbox and owner_body.collidelistall(bboxes):
                print('| | | | |')
                print('... But a collision persists')
                print('| | | | |')

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
        # Dont do vertical collision if it has gravity and is standing on ground
        grav_comp = self.owner.components.get(GravityComponent.id_class) 
        on_ground = grav_comp and grav_comp.state == GravityCompState.GROUND

        # TODO put in vert collision with on_ground!!!!!

        # if either are negative, a collision may of happened
        # If either's abs is larger than the height, its NOT a collision 
        # print('owner size: ' + str(owner_body.size))
        owner_top_bbox_bottom = owner_body.top - bbox.bottom  
        owner_bottom_bbox_top = bbox.top - owner_body.bottom
        # print('owner top - bbox bottom: ' + str(owner_top_bbox_bottom))
        # print('owner bottom- bbox top: ' + str(owner_bottom_bbox_top))
        # Top Collision
        # if owner_top_bbox_bottom < 0 and -owner_top_bbox_bottom < bbox.height and self.owner.velocity.y < 0:
        if owner_top_bbox_bottom < 0 and self.owner.velocity.y < 0:
            # print('TOP COLLISION') 
            fix_vector.y = -owner_top_bbox_bottom

        # Bottom Collision
        # elif owner_bottom_bbox_top < 0 and -owner_bottom_bbox_top < bbox.height and self.owner.velocity.y > 0:
        elif owner_bottom_bbox_top < 0 and self.owner.velocity.y > 0:
            # print('BOTTOM COLLISION') 
            fix_vector.y = owner_bottom_bbox_top

        # X-componenet
        owner_left_bbox_right = owner_body.left - bbox.right
        owner_right_bbox_left = bbox.left - owner_body.right
        # Left Collision
        if owner_left_bbox_right < 0 and self.owner.velocity.x < 0:
            # print('LEFT COLLISION')
            fix_vector.x = -owner_left_bbox_right
        # Right Collision
        elif owner_right_bbox_left < 0 and self.owner.velocity.x > 0:
            # print('RIGHT COLLISION')
            fix_vector.x = owner_right_bbox_left 

        return fix_vector

    def move_without_collision(self, deltatime):
        """
        Makes movement steps move without intersecting nearby objects
        """
        map_data = GameMap.map_data 
        TILE_SIZE = map_data.tilewidth
        owner_rect = self.owner.rect
        delta_movement = self.owner.velocity * deltatime
        final_movement_veloc = Vector2(delta_movement.x, delta_movement.y) 
        tolerance = 0.

        direction = 0
        start_tile  = -999 
        target_tile = -999
        debug_fixed = False

        # X
        if self.owner.velocity.x > tolerance: # Right
            start_tile = int(owner_rect.right / TILE_SIZE)
            target_tile = int((owner_rect.right + delta_movement.x) / TILE_SIZE)
            direction = 1 # Right
        elif self.owner.velocity.x < -tolerance: # Left
            start_tile = int(owner_rect.left / TILE_SIZE)
            target_tile = int((owner_rect.left + delta_movement.x) / TILE_SIZE)
            direction = -1 # Left
        start_height = int(owner_rect.top / TILE_SIZE)
        end_height = int(owner_rect.bottom / TILE_SIZE)

        if direction != 0:
            x_range = range(start_tile, target_tile + 1, direction) if direction == 1 else range(target_tile , start_tile- 1 , direction)
            for j in range(start_height, end_height): # Height
                for i in x_range: # Width
                    # Get tile, skip if not existent/has no property
                    try: 
                        properties = GameMap.get_tile_properties(i, j)
                        if not properties: continue
                    except:
                        continue

                    if properties and properties.get(MapInfo.SOLID.value):
                        self.owner.velocity.x = 0
                        bbox = pygame.Rect((i * TILE_SIZE, j * TILE_SIZE), (TILE_SIZE, TILE_SIZE))
                        if direction == 1: # Right
                            smallest_dist = min(bbox.left - owner_rect.right, delta_movement.x)
                            final_movement_veloc.x = min(smallest_dist, final_movement_veloc.x)
                            print('fixing: RIGHT')
                        else: # Left
                            smallest_dist = max(bbox.right - owner_rect.left, delta_movement.x)
                            final_movement_veloc.x = max(smallest_dist, final_movement_veloc.x)
                            print('fixing: LEFT')
                        debug_fixed = True
                        break
        else:
            final_movement_veloc.x = delta_movement.x

        self.owner.rect.move_ip(final_movement_veloc.x, 0)


        # Y
        owner_rect = self.owner.rect
        direction = 0
        start_tile = -999
        target_tile = -999

        # if debug_fixed:
        #     time.sleep(0.3)

        if self.owner.velocity.y > tolerance: # Down 
            start_tile = int(owner_rect.bottom / TILE_SIZE)
            target_tile = int((owner_rect.bottom + delta_movement.y) / TILE_SIZE)
            direction = 1 # Down 
        elif self.owner.velocity.y < -tolerance: # Up 
            start_tile = int(owner_rect.top / TILE_SIZE)
            target_tile = int((owner_rect.top + delta_movement.y) / TILE_SIZE)
            direction = -1 # Up 
        start_width = int((owner_rect.left + 5) / TILE_SIZE)
        end_width = int((owner_rect.right - 5) / TILE_SIZE)

        if direction != 0:
            y_range = range(start_tile - 1, target_tile + 1, direction) if direction == 1 else range(target_tile + 1, start_height - 1, direction)
            for i in range(start_width, end_width + 1):
                for j in y_range:
                    # Get tile, skip if not existent/has no property
                    try: 
                        properties = GameMap.get_tile_properties(i, j)
                        if not properties: continue
                    except:
                        continue

                    if properties and properties.get(MapInfo.SOLID.value) or properties.get(MapInfo.SEMISOLID.value):
                        bbox = pygame.Rect((i * TILE_SIZE, j * TILE_SIZE), (TILE_SIZE, TILE_SIZE))
                        self.owner.velocity.y = 0
                        if direction == 1: # Down 
                            smallest_dist = min(bbox.top - owner_rect.bottom, delta_movement.y)
                            final_movement_veloc.y = min(smallest_dist, final_movement_veloc.y)
                            print('fixing: DOWN')
                        else: # Up 
                            smallest_dist = max(bbox.bottom - owner_rect.top, delta_movement.y)
                            final_movement_veloc.y = max(smallest_dist, final_movement_veloc.y)
                            print('fixing: UP')
                        break
        else:
            final_movement_veloc.y = delta_movement.y

        self.owner.rect.move_ip(0, final_movement_veloc.y)


                 
class GravityComponent(Component):
    """ Allows Entities to experience the effects of gravity."""

    GRAVITY = 9.8 * 50 

    def __init__(self, owner):
        super().__init__(owner)
        # Whether the player is on solid ground or in freefall
        self.state = GravityCompState.AIR
        # Used to make sure gravity is only applied once when leaving the ground 
        self.should_apply_gravity = True 

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
                # print('ON GROUND!')
                self.entered_ground()
                 
        # Ground -> Air
        elif self.state == GravityCompState.GROUND:
            if not properties:
                # print('Midair now') 
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
        self.state = PlayerState.STAND
        self.power_up = PowerUp.NORMAL
        # Player Constants
        self.MAX_RUN_SPEED = 200 
        self.MAX_WALK_SPEED = 90
        self.WALK_ACCELERATION = 100
        self.RUN_ACCELERATION = 150
        self.JUMP_POWER = -300
        self.TRACTION = 180 
        self.AIR_TRACTION = 80 
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
        self.state = PlayerState.JUMP

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
        if self.owner.components[GravityComponent].state == GravityCompState.GROUND:
            traction = self.TRACTION
        else:
            traction = self.AIR_TRACTION
        tolerance = 0.5
        if self.owner.velocity.x < -tolerance:
            self.owner.acceleration.x = traction
        elif self.owner.velocity.x > tolerance:
            self.owner.acceleration.x = -traction
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
