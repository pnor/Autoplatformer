
import sys

import pygame
import pyscroll
from pygame.locals import *
from pytmx.util_pygame import load_pygame

import constants
from Entities.Player import Player
from Map.GameMap import *

from pygame.math import Vector2


class MainGame(object):
    # Game Constants
    SCREENRECT = Rect(0, 0, 800, 480)

    # Game Variables 
    def main(self):
        self.init_pygame()
        self.set_up_display()
        self.set_up_map()
        self.spawn_player()

        self.running = True

        try:
            self.run()
        except KeyboardInterrupt:
            self.running = False
            print('done')
            pygame.exit()
        
    def init_pygame(self):
        """
        Initializes pygame
        """
        if pygame.get_sdl_version()[0] == 2:
            pygame.mixer.pre_init(44100, 32, 2, 1024)
        pygame.init()
        if pygame.mixer and not pygame.mixer.get_init():
            print('WARNING: No sound')
            pygame.mixer = None
        pygame.display.set_caption("Auto-platformer")

    def set_up_display(self):
        """
        Sets up the display
        """
        screen_size = self.SCREENRECT
        # TODO change this cuz prolly dont want this
        winstyle = 1
        self.screen = pygame.display.set_mode(screen_size.size, pygame.RESIZABLE)
        self.temp_surface = pygame.Surface((screen_size.width / 2, screen_size.height / 2)).convert()
        GameMap.temp_surface = self.temp_surface

    def set_up_map(self):
        """
        Sets up the map and the scrolling
        """
        GameMap.set_up_map()

        pyscroll_map_data = pyscroll.data.TiledMapData(GameMap.map_data)
        # Scrolling Layer
        w, h = self.screen.get_size()
        self.map_layer = pyscroll.orthographic.BufferedRenderer(pyscroll_map_data, (w / 2, h / 2), clamp_camera=True)
        # Make group with scrolling map
        self.group = pyscroll.PyscrollGroup(map_layer= self.map_layer)

        self.map_layer.zoom = 1.0 

    def spawn_player(self):
        """ Spawns player onto the map """
        # Add Sprites to group

        # Place player where spawn tile is, searching from bottom left first
        self.player = None
        spawned_player = False 

        for i in range(0, GameMap.map_data.width):
            for j in range(GameMap.map_data.height - 1, -1, -1):
                tile_property = GameMap.get_tile_properties(i, j)

                if tile_property and tile_property.get(MapInfo.SPAWN.value):
                    spawned_player = True
                    print('in: ' + str((i, j)))
                    spawn_point_x = i * GameMap.map_data.tilewidth + (GameMap.map_data.tilewidth / 2)
                    spawn_point_y = j * GameMap.map_data.tileheight
                    print('spawn: ' + str((spawn_point_x, spawn_point_y)))
                    self.player = Player(position=(spawn_point_x, spawn_point_y))
                    print('body: ' + str(self.player.rect))

                if spawned_player: break
            if spawned_player: break

        self.group.add(self.player)

    def handle_events(self):
        """
        Handle events that control the player
        """
        # pygame.event.get() 

        poll = pygame.event.poll
        clamp_func = lambda val, max_val, min_val: max(min(val, max_val), min_val)

        event = poll()
        keys = pygame.key.get_pressed()
        while event:
            if event.type == KEYDOWN:
                # Zoom
                if event.key == K_EQUALS:
                    self.map_layer.zoom = clamp_func(self.map_layer.zoom + 0.25, 999, 0.24)
                    print('zoom~')
                elif event.key == K_MINUS:
                    self.map_layer.zoom = clamp_func(self.map_layer.zoom - 0.25, 999, 0.24)
                    print('woom.')
                    # Movement

                if event.key == K_1: # All images 
                    for layer in map_data.layers:
                        for x, y, img in layer.tiles():
                            print('(' + str(x) + ', ' + str(y) + ') ' + str(img))

            event = poll()

        # Movement
        if keys[K_w]:
            self.player.velocity.y -= 10
            # self.player.velocity.move_ip((0, -10))
            print(self.player.velocity)
        if keys[K_a]:
            self.player.velocity.x -= 10
            # self.player.velocity.move_ip((-10, 0))
            print(self.player.velocity)
        if keys[K_s]:
            self.player.velocity.y += 10
            # self.player.velocity.move_ip((0, 10))
            print(self.player.velocity) 
        if keys[K_d]:
            self.player.velocity.x += 10
            # self.player.velocity.move_ip((10, 0))
            print(self.player.velocity)
        if keys[K_0]:
            self.player.velocity = Vector2(0, 0)
            print('zeroing velocity: ' + str(self.player.velocity))
        if keys[K_8]:
            print('Moving to top left')
            self.player.rect.topleft = (0, 0)
        if keys[K_9]:
            print('Rectangle Info')
            print(self.player.rect.size)
            print(self.player.rect.center)
            print(self.player.rect.topleft)
            print('Movement Info')
            print('Veloc: ' + str(self.player.velocity))
            print('Accel: ' + str(self.player.acceleration))

    def update_all(self, delta):
        """
        Update all game elements with the change in time from last render loop 
        """
        self.group.update(delta)


    def run(self):
        """ Render loop
        """
        clock = pygame.time.Clock()
        FPS = 60

        try:
            while self.running:
                delta = clock.tick(FPS) / 1000.
                # Handle Events
                self.handle_events()
                # Update Game Elements
                self.update_all(delta)
                # Draw
                self.screen.fill((0, 0, 0))
                self.draw(self.temp_surface)
        except KeyboardInterrupt:
            print('done')
            pygame.quit()
            sys.exit()

    def draw(self, surface):
        """
        Draws all game elements
        """
        self.group.center(self.player.rect.center)

        # draw the map and all sprites
        self.group.draw(surface)

        pygame.transform.scale(self.temp_surface, self.screen.get_size(), self.screen)

        pygame.display.flip()


if __name__ == '__main__' : 
    game = MainGame()
    game.main()
