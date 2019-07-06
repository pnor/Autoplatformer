from enum import Enum
import Input.Buttons
import constants
import pygame
from Entities.Entity import Entity
from pygame.locals import *
from Entities.Components.Components import CollisionComponent
from Entities.Components.Components import GravityComponent
from Entities.Components.Components import PlayerComponent

class Player(Entity):

    def __init__(self, position=None):
        """
        Initializes player
        :param position: starting position of player. 0, 0 by default
        """
        super().__init__()

        self.image = pygame.image.load(constants.DEBUG_IMG).convert_alpha()
        if position:
            self.rect = self.image.get_rect(center=position)
        else:
            self.rect = self.image.get_rect()

        # Components
        self.add_component(CollisionComponent(self))
        self.add_component(GravityComponent(self))
        self.add_component(PlayerComponent(self))

    def update(self, deltatime):
        super().update(deltatime)

