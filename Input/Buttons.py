from enum import Enum
import pygame
from pygame.locals import *

class Buttons(Enum):
    """ Button inputs for all game actions (Value is the key to use it) """
    # Movement
    MOVE_RIGHT = K_d
    MOVE_LEFT = K_a
    MOVE_UP = K_w
    # Jumping
    JUMP = K_SPACE
    # Crouch
    CROUCH = K_s
    # Spin Jump
    SPIN = K_j 
    # Shoot laser if has powerup/Use with MOVE to run
    RUN = K_LSHIFT 
