# -*- coding: utf-8 -*-
import pyglet

import pymunk
from . import constants

import random

class Randomizer():
    last_x       = 0
    last_impulse = 0

    def __initialize__(self):
        self.last_x       = 0
        self.last_impulse = 0

    def random_x(self, new = True):
        if new:
            result =  random.randint(-constants.W_WIDTH/2 + 30, constants.W_WIDTH/2 - 30)
            self.last_x = result
        return self.last_x

    def random_impulse(self, new = True):
        if new:
            result = random.randint(-10000, 10000)
            self.last_impulse = result
        return self.last_impulse


#classe que define o espaço de objeto. Usada para objetos que se movem
#(roda, smiley). define algumas propriedades fisicas como o formato do corpo
#a massa e a inércia
class PymunkSpace(object):
    def body_space(self, space, position, mass, radius):
        self.space    = space
        self.mass     = mass
        self.radius   = radius
        self.inertia  = pymunk.moment_for_circle(self.mass, 0, self.radius)
        self.body     = pymunk.Body(self.mass, self.inertia)
        self.body.position = position
        self.shape  = pymunk.Circle(self.body, self.radius)
        self.space.add(self.body, self.shape)
        return self.shape

#classe abstrata básica para todos os sprites. Responsável por carregar a textura, basicamente
class BaseSprite(pyglet.sprite.Sprite):
    def __init__(self, image, anchor,x, y, batch, group):
        image =  pyglet.image.load(image)
        if anchor == True:
              image.anchor_x = image.width/2
              image.anchor_y = image.height/2
        else:
              image.anchor_x = image.width/2
        pyglet.sprite.Sprite.__init__(self, image, x, y, batch = batch, group = group)

#Aqui, por "objeto de jogo", quis me referir a tudo aquilo com o qual o jogador
#pode interagir (ou seja, nada que faça parte do cenário, que é fixo)
#classe que define o smiley e a roda, basicamente.
class GameObject(BaseSprite):
    def __init__(self, type, batch, space, group):
        if type == "wheel":
            image = './resources/wheel.png'
            self.type = "wheel"
            self.obj_space = PymunkSpace().body_space(space, (constants.X_START,constants.Y_START), 41, 70)
        else:
            image = './resources/smiley.png'
            self.type = "smiley"
            self.obj_space = PymunkSpace().body_space(space,(constants.X_START,constants.Y_START + constants.ROD_LENGTH), 60, 35)


        BaseSprite.__init__(self, image, True,
                    self.obj_space.body.position.x,
                    self.obj_space.body.position.y, batch,
                    group)

    #funcao que atualiza a posiçao do sprite de acordo com a posiçao do objeto no espaço físico
    #chamada a cada ciclo de clock (60x/s)
    def update(self):
        self.x = self.obj_space.body.position.x
        self.y = self.obj_space.body.position.y

    #funçao que reseta a posiçao da roda e do smiley
    #chamada cada vez que uma época termina (smiley cai ou roda sai da tela)
    def reset(self):
        self.obj_space.body.velocity *= 0
        self.obj_space.body.position.x = constants.X_START
        if self.type == "wheel":
            self.obj_space.body.position.y = constants.Y_START
        else:
            self.obj_space.body.position.y = constants.Y_START + constants.ROD_LENGTH
            self.obj_space.body.apply_impulse(j = (random.randint(-10000, 10000), 0))

    def randomize(self, randomizer, new):
        offset = randomizer.random_x(new)
        self.obj_space.body.position.x += offset

    def apply_impulse(self, randomizer, new):
        self.obj_space.body.apply_impulse(j = (randomizer.random_impulse(new),0))

#classe para a nuvem
class Cloud(BaseSprite):
    def __init__(self, batch, x, y, group):
        BaseSprite.__init__(self, './resources/cloud.png', True, x, y, batch, group)

class Rod(BaseSprite):
    def __init__(self, batch, group):
        BaseSprite.__init__(self, './resources/rod.png', False, 100, 100, batch, group)

    def update(self, window):
        self.x = window.lone_wheel.x
        self.y = window.lone_wheel.y
        self.rotation = window.get_pole_angle()

#classe para o chão
class Floor(BaseSprite):
    def __init__(self, batch, space):
        body = pymunk.Body()
        self.segment = pymunk.Segment(body, (0, constants.F_HEIGHT), (constants.W_WIDTH, constants.F_HEIGHT), 0)
        space.add(self.segment)
        self.img = pyglet.image.load('./resources/mario_brick.png')
