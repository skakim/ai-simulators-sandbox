# -*- coding: utf-8 -*-
import math, random, sys, signal, time, datetime

import AI_controller
import pyglet
from pyglet import font
from pyglet.gl import *

import pymunk
from .sprites import Cloud, Floor, GameObject, Rod, Randomizer
from .window  import Game
from . import constants


class Versus:
    def __init__(self, space, load_p1 = None, load_p2 = None):
        self.randomizer = Randomizer()
        windows = [Game(space = space,
                        run_pyglet = True,
                        load = load_p1,
                        randomizer = self.randomizer,
                        mode = "versus",
                        player = 1),
                   Game(space = pymunk.Space(),
                        run_pyglet = True,
                        load = load_p2,
                        randomizer = self.randomizer,
                        mode = "versus",
                        player = 2)]
        for i in range(0,2):
            windows[i].opponent = windows[1-i]
