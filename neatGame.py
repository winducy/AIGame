__author__ = 'user'

import pygame
import sys
from pygame.locals import *
import os
import random
import math
import ga
from neat.nn import nn_pure as nn


REDDISH = (102, 0, 0)
UP = 1
DOWN = 0
MONSTERDISTANCE = 30
MONSTERMIN = 50
MONSTERMAX = 100


class Game:
    """The Game - This class handles the main
    initialization and creating of the Game."""

    def __init__(self, width=640, height=480):
        pygame.init()
        # Set window size
        self.width = width
        self.height = height
        # Create screen
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.background_image = pygame.image.load("layer-1-sky.png").convert()
        self.bgx = 0
        self.bgy = 0
        # Set initial values
        self.score = 0
        self.block_list = pygame.sprite.Group()
        self.all_sprites_list = pygame.sprite.Group()
        self.player = Bird()
        self.ground = Ground()
        self.block_list.add(Monster())
        self.all_sprites_list.add(self.player)
        self.all_sprites_list.add(self.ground)
        self.clock = None
        self.font = pygame.font.Font(None, 36)
        self.text = self.font.render(str(self.score), 1, (20, 20, 20))
        self.textpos = self.text.get_rect()
        self.textpos.centerx = self.screen.get_rect().centerx
        self.screen.blit(self.text, self.textpos)

    def main_loop(self, display, neuron):
        if display:
            self.clock = pygame.time.Clock()
        """This is the Main Loop of the Game"""
        change = True
        counter = MONSTERDISTANCE
        not_dead = True
        inputs = []
        if neuron is not None:
            inputs = [1]

        while 1:
            if not_dead:
                up = True in pygame.key.get_pressed()
                counter = self.add_monsters(counter)
                if neuron is not None:
                    inputs.extend(self.find_next_block(self.block_list.sprites()))
                    up = neuron.sactivate(inputs)[0] > 0.5
                    inputs = [1]
                change = self.move_player(up, change)

                self.all_sprites_list.update()

                # checks collisions
                blocks_hit_list = pygame.sprite.spritecollide(self.player, self.block_list, False)
                not_dead = self.check_collisions(blocks_hit_list)

                if display:
                    self.display()
                self.score += 1

                if self.score > 10000:
                    not_dead = False

            elif display:
                self.all_sprites_list.draw(self.screen)
                lose = pygame.font.Font(None, 100).render("You Lose!", 1, (20, 20, 20))
                restart = pygame.font.Font(None, 40).render("Press any key to restart!", 1, (20, 20, 20))
                self.screen.blit(lose, (100, 200))
                self.screen.blit(restart, (200, 300))
                pygame.display.flip()
                self.clock.tick(30)

                if neuron is None:
                    keys = pygame.key.get_pressed()
                    if True in keys:
                        self.restart(None)
                elif display:
                    self.restart(neuron)
                else:
                    return self.score
            else:
                return self.score

            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit()
        return self.score

    def find_next_block(self, blocklist):
        block_index = 0
        temp_block_rect = blocklist[block_index]
        minx = temp_block_rect.px
        miny = temp_block_rect.py
        while minx <= (self.player.px - 56) and block_index < len(blocklist) - 1:
            block_index += 1
            temp_block_rect = blocklist[block_index]
            minx = temp_block_rect.px
            miny = temp_block_rect.py
        return [minx - self.player.px, (miny - self.player.py + 44), miny + 235 - self.player.py, self.player.py, 480 - self.player.py]


    @staticmethod
    def restart(neuron):
        Game().main_loop(True, neuron)

    def display(self):
        self.all_sprites_list.draw(self.screen)
        pygame.display.flip()
        self.scroll_background()
        self.update_score()


    def check_collisions(self, collisions):
        return not (collisions or self.player.py < -5 or self.player.py > 400)

    def add_monsters(self, counter):
        if counter == 0:
            counter = random.randint(MONSTERMIN, MONSTERMAX)
            monster = Monster()
            self.block_list.add(monster)
            self.all_sprites_list.add(monster)
        return counter - 1

    def move_player(self, move_up, changeDirection):
        if move_up:
            if changeDirection:
                self.player.vy = 3
                changeDirection = not changeDirection
            self.player.move(UP)
        else:
            if not changeDirection:
                self.player.vy = 3
                changeDirection = not changeDirection
            self.player.move(DOWN)
        return changeDirection

    def scroll_background(self):
        if self.bgx < -960:
            self.bgx = 0
        self.bgx -= 3
        self.screen.blit(self.background_image, [self.bgx, self.bgy])

    def update_score(self):
        #self.clock.tick(30)
        text = self.font.render(str(self.score), 1, (20, 20, 20))
        self.screen.blit(text, self.textpos)



class Bird(pygame.sprite.Sprite):
    """The Bird - This class is a class for
    Bird spirte """

    def __init__(self):
        # Player initial position
        self.px=100
        self.py=480/2
        pygame.sprite.Sprite.__init__(self)

        self.images=[]
        self.images.append(pygame.image.load('frame-1.png').convert())
        self.images.append(pygame.image.load('frame-2.png').convert())
        self.images.append(pygame.image.load('frame-3.png').convert())
        self.images.append(pygame.image.load('frame-4.png').convert())

        self.index=0
        self.image=self.images[self.index]
        self.image.set_colorkey(REDDISH)
        self.rect=self.image.get_rect()
        self.rect.center=self.px, self.py
        # velocity
        self.vy=3
        # acceleration
        self.ay=1

    def update(self):
        """This method iterates through the elements inside self.images and
        displays the next one each tick. For a slower animation, you may want to
        consider using a timer of some sort so it updates slower."""
        self.index += 1
        if self.index >= len(self.images):
            self.index=0
        self.image=self.images[self.index]
        self.image.set_colorkey(REDDISH)

    def move(self, direction):
        if direction == UP:
            self.py-=self.vy
        else:
            self.py+=self.vy
        self.vy+=self.ay
        self.rect.center = self.px, self.py


class Monster(pygame.sprite.Sprite):
    """The Monster - This class is a class for
    Monster spirte """

    def __init__(self):
        self.px = 680
        self.py = random.randint(117, 323)
        pygame.sprite.Sprite.__init__(self)

        self.images = []
        self.images.append(pygame.image.load('frame-1-m.png').convert())
        self.images.append(pygame.image.load('frame-2-m.png').convert())

        self.index = 0
        self.image = self.images[self.index]
        self.image.set_colorkey(REDDISH)
        self.rect = self.image.get_rect()
        self.rect.center = self.px, self.py
        self.counter = 0
        #velocity
        self.vx = 5.0

    def update(self):
        '''This method iterates through the elements inside self.images and
        displays the next one each tick. For a slower animation, you may want to
        consider using a timer of some sort so it updates slower.'''

        if(self.counter == 8):
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images):
                self.index = 0
            self.image = self.images[self.index]
        self.counter += 1
        self.px -= math.floor(self.vx)
        self.rect.center = self.px, self.py
        self.image.set_colorkey(REDDISH)

        if(self.px < -13):
            self.kill()
            self.vx += 0.1


class Ground(pygame.sprite.Sprite):
    def __init__(self):
        self.px = 0
        self.py = 440
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('tile.png').convert()
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(self.px, self.py)

    def update(self):
        if self.rect.x < -160:
            self.rect.x = 0
        self.rect = self.rect.move(-5, 0)


if __name__ == "__main__":
    MainWindow = Game()
    MainWindow.main_loop(True, ga.Neuron(6))
    #MainWindow.main_loop(True, None)
