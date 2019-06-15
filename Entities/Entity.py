import pygame
from pygame.locals import *
from pygame.math import Vector2
from abc import ABC, abstractmethod
from enum import Enum

class Entity(ABC, pygame.sprite.Sprite):
    """
    Base model for all objects in the game
    """

    # Constants 
    MAX_Y_SPEED = 1000 # Terminal Velocity
    MAX_X_SPEED = 1000

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        # Movement
        self.position = Vector2()
        self.velocity = Vector2()
        self.acceleration = Vector2()
        # Should be zero if player doesn't touch controls
        self.target_x_speed = 0
        self.target_y_speed = 0
        # Components
        self.components = {}

    def add_component(self, component):
        self.components[type(component)] = component

    @abstractmethod
    def update(self, deltatime):
        self.position += deltatime * self.velocity
        self.velocity += deltatime * self.acceleration
        # Update all components
        for component in self.components.values():
            component.update(deltatime)

         



class EntityState(Enum):
    AIR = 'air'
    GROUND = 'ground'
