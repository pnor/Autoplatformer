from enum import Enum
import Input.Buttons
import constants
import pygame
from Entities.Entity import Entity
from pygame.locals import *
from Entities.Components.Components import CollisionComponent
from Entities.Components.Components import GravityComponent

class Player(Entity):

    def __init__(self, position=None):
        """
        Initializes player
        :param position: starting position of player. 0, 0 by default
        """
        super().__init__()

        self.image = pygame.image.load(constants.DEBUG_IMG).convert_alpha()
        self.state = PlayerState.STAND
        self.power = PowerUp.NORMAL
        if position:
            self.rect = self.image.get_rect(center=position)
        else:
            self.rect = self.image.get_rect()

        # self.image = pygame.transform.scale(self.image, self.rect.size)

        # Components
        self.add_component(CollisionComponent(self))
        self.add_component(GravityComponent(self))

    def update(self, deltatime):
        super().update(deltatime)

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
