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
        pass

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
                        else: # Left
                            smallest_dist = max(bbox.right - owner_rect.left, delta_movement.x)
                            final_movement_veloc.x = max(smallest_dist, final_movement_veloc.x)
                        break
        else:
            final_movement_veloc.x = delta_movement.x

        self.owner.rect.move_ip(final_movement_veloc.x, 0)


        # Y
        owner_rect = self.owner.rect
        direction = 0
        start_tile = -999
        target_tile = -999


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
                        else: # Up 
                            smallest_dist = max(bbox.bottom - owner_rect.top, delta_movement.y)
                            final_movement_veloc.y = max(smallest_dist, final_movement_veloc.y)
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
                self.entered_ground()
                 
        # Ground -> Air
        elif self.state == GravityCompState.GROUND:
            if not properties:
                self.left_ground()
                

        # If in the air, and needs to apply gravity
        if self.state == GravityCompState.AIR and self.should_apply_gravity:
            self.owner.acceleration.y = self.GRAVITY
            self.should_apply_gravity = False 
        # If on the ground
        elif self.state == GravityCompState.GROUND and self.owner.acceleration.y > 0:
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
        self.state = PlayerState.STAND # Describes what player is doing
        self.power_up = PowerUp.NORMAL # Power Up
        # Internal Player Variables
        self._jump_time = 0 # Counts how long the player has jumped in a single jump
        self._cur_jump = 0 # Describes how many jumps the player has left
        self._no_jump = False # Whether the player can jump
        self._hold_jump = False # Whether a jump button is being held
        # Player Constants
        self.MAX_RUN_SPEED = 200 
        self.MAX_WALK_SPEED = 90 
        self.WALK_ACCELERATION = 100  
        self.RUN_ACCELERATION = 150
        self.JUMP_POWER = -300
        self.TRACTION = 180 
        self.AIR_TRACTION = 80 
        self.NUMBER_JUMPS = 2
        self.JUMP_DURATION = 0.3
        # Set Player Entity Constants
        self.owner.target_x_speed = self.MAX_RUN_SPEED
        # Create Buttons list (!) should be set before update is called
        self.buttons = [] 

    # Override
    def was_added(self):
        """ 
        Checks to see if Entity has necessary Components (Gravity, Collision)
        """ 
        assert self.owner.components.get(GravityComponent.id_class), "Player missing Gravity Component"
        assert self.owner.components.get(CollisionComponent.id_class), "Player missing Collision Component"

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
        if not self._no_jump:
            if self.buttons[Buttons.JUMP.value]:
                self.jump(delta, spin=False)
            elif self.buttons[Buttons.SPIN.value]:
                self.jump(spin=True)
            elif self.state == PlayerState.JUMP or self.state == PlayerState.SPIN:
                if self._hold_jump:
                    self.increment_jump()
                self._hold_jump = False
                if self._cur_jump >= self.NUMBER_JUMPS:
                    self._no_jump = True

        # Update States
        if self.owner.components[GravityComponent.id_class].state == GravityCompState.GROUND:
            self.state = PlayerState.STAND
            self.reset_jumps()
        tolerance = 0.5
        if self.state != PlayerState.STAND and self.owner.velocity.length() < tolerance:
            self.state = PlayerState.WALK
        
            
    def jump(self, deltatime, spin=False):
        """
        Makes the player jump.
        :param deltatime: change in time (passed from update)
        :param spin: whether the player will do a spin jump
        """
        if self._no_jump: return 

        self._jump_time += deltatime
        self._hold_jump = True
        if self._jump_time <= self.JUMP_DURATION:
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
        self.state = PlayerState.RUN if run else PlayerState.WALK
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

    def reset_jumps(self):
        """ Resets the player's number of jumps"""
        self._no_jump = False
        self._jump_time = 0
        self._cur_jump = 0
        self._hold_jump = False

    def increment_jump(self):
        """ Increments the player's current jump"""
        self._cur_jump += 1
        self._jump_time = 0
        self._hold_jump = True

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
