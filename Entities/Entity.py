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
        self.velocity = Vector2()
        self.acceleration = Vector2()
        # Should be zero if player doesn't touch controls
        self.target_x_speed = 100 
        self.target_y_speed = 100
        # Components
        self.components = {}

    def add_component(self, component):
        self.components[component.id_class] = component

    @abstractmethod
    def update(self, deltatime):
        clamp_func = lambda val, max_val, min_val: max(min(val, max_val), min_val)

        self.rect.move_ip(self.velocity.x * deltatime, self.velocity.y * deltatime)
        self.velocity += deltatime * self.acceleration

        # clamp
        if self.velocity.x > 0:
            self.velocity.x = clamp_func(self.velocity.x, self.target_x_speed, 0)
        else:
            self.velocity.x = clamp_func(self.velocity.x, 0, -self.target_x_speed)

        if self.velocity.y > 0:
            self.velocity.y = clamp_func(self.velocity.y, self.target_y_speed, 0) 
        else:
            self.velocity.y = clamp_func(self.velocity.y, 0, -self.target_y_speed)

        # Update all components
        for component in self.components.values():
            component.update(deltatime)

