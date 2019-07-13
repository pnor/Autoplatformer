from abc import ABC, abstractmethod
import pygame
from pygame.locals import *
from pygame.math import Vector2
from abc import ABC, abstractmethod
from enum import Enum

class Component(ABC):
    """ Abstraction of the basic component. All components have an owner and an update method"""

    
    def __init__(self, owner):
        """
        Constructs the base Component
        :param owner: should be of type Entity
        """
        self.owner = owner
        # Set id type of subclass so it can be used key for Entity's map
        print('!')
        self.__set_id_class()

    @abstractmethod
    def update(self, delta):
        """ Update entity using information stored in component"""
        pass

    def was_added(self):
        """ Called right after when an Entity adds this component to its dictionary"""
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