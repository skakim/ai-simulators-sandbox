# -*- coding: utf-8 -*-
import math, random, sys, signal, time, datetime, numpy

import AI_controller
import pyglet
from pyglet import font
from pyglet.gl import *

import pymunk
from pymunk import Vec2d
from .sprites import Cloud, Floor, GameObject, Rod, Randomizer
from . import constants

G_VECTOR = (0.0, -900.0)
SKY_COLOR = (40.0/255, 185.0/255, 255/255)


def signal_handler(signal, frame):
        print(' Finalizando...')
        sys.exit(0)


#Classe que define a captação e as ações tomadas em eventos de mouse/teclado
class GameEventHandler(object):
    def __init__(self, window):
        self.window = window
    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.D or symbol == pyglet.window.key.RIGHT:
            if self.window.mode == "single" or self.window.state == "active":
                self.window.smiley.obj_space.body.apply_impulse(j = (15000, 0))
        if symbol == pyglet.window.key.A or symbol == pyglet.window.key.LEFT:
            if self.window.mode == "single" or self.window.state == "active":
                self.window.smiley.obj_space.body.apply_impulse(j = (-15000, 0))
        if symbol == pyglet.window.key.W:
            self.window.toggle_wind()
        if symbol == pyglet.window.key.ESCAPE:
            exit()
        return True

#classe que define o jogo
class Game(pyglet.window.Window):
    def __init__(self, space, run_pyglet, load, randomizer = None, mode = "single", player = 0):
        space.gravity = (G_VECTOR[0], G_VECTOR[1])
        self.space = space
        self.epoch = 0

        if(run_pyglet):
            pyglet.window.Window.__init__(self, width = constants.W_WIDTH, height = constants.W_HEIGHT)
            self.wind = 0

        self.run_pyglet = run_pyglet
        if randomizer == None:
            self.randomizer = Randomizer()
        else:
            self.randomizer = randomizer
        self.mode = mode
        self.opponent = None
        self.player   = player
        self.state    = "active"
        self.performances = []
        self.round    = 1

        self.push_handlers(GameEventHandler(self))
        self.batch_draw = pyglet.graphics.Batch()
        font.add_file('./resources/neon_pixel.ttf')
        neon_pixel = font.load('Neon Pixel-7')
        self.define_scenario()

        self.define_game_objects()
        signal.signal(signal.SIGINT, signal_handler)

        self.wind     = random.randint(-500, 500)
        self.friction = random.uniform(0.970, 0.999)


        self.pole_angle = self.get_pole_angle()
        self.angular_velocity = 0
        if self.mode == "single" or self.player == 1:
            self.learner = AI_controller.Learner(self, load)
        else:
            try:
                import Opponent
            except ImportError:
                print "Erro ao importar o pacote oponente"
                exit()
            self.learner = Opponent.Learner(self, load)
        self.current_iteration = 0

        if run_pyglet and self.mode == "single":
            filename =  datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
            print "Gerando arquivo para listagem das performances (%s.txt)" % filename
            self.performances_file = open(("./performance/%s.txt" % filename), "w+")

        pyglet.clock.schedule(self.update)


    def define_scenario(self):
        background = pyglet.graphics.OrderedGroup(0)
        pyglet.gl.glClearColor(SKY_COLOR[0], SKY_COLOR[1], SKY_COLOR[2],1)
        self.clouds = (Cloud(batch = self.batch_draw,
                             x = constants.W_WIDTH * 0.2,
                             y = constants.W_HEIGHT * 0.8,
                             group = background),
                    Cloud(batch = self.batch_draw,
                          x = constants.W_WIDTH * 0.8,
                          y = constants.W_HEIGHT * 0.72,
                          group = background))
        self.floor = Floor(batch = self.batch_draw, space = self.space)
        static_lines = [pymunk.Segment(self.space.static_body, Vec2d(0, constants.F_HEIGHT),
                                                               Vec2d(constants.W_WIDTH/2, constants.F_HEIGHT + 110), 1.0),
                        pymunk.Segment(self.space.static_body, Vec2d(constants.W_WIDTH/2, constants.F_HEIGHT + 110),
                                                                Vec2d(constants.W_WIDTH, constants.F_HEIGHT), 1.0)
                    ]
        self.space.add(static_lines)



    def define_game_objects(self):
        self.lone_wheel = GameObject("wheel", batch = self.batch_draw,
                    space = self.space,
                    group = pyglet.graphics.OrderedGroup(1))

        self.smiley = GameObject("smiley", batch = self.batch_draw,
                             space = self.space,
                             group = pyglet.graphics.OrderedGroup(3))

        if self.mode == "single" or self.player == 1:
            self.lone_wheel.randomize(self.randomizer, new = True)
        else:
            self.lone_wheel.randomize(self.randomizer, new = False)
        self.smiley.randomize(self.randomizer, new = False)
        self.smiley.apply_impulse(self.randomizer, new = True)
        rod = pymunk.PinJoint(self.lone_wheel.obj_space.body,
                              self.smiley.obj_space.body)
        self.space.add(rod)
        self.rod = Rod(batch = self.batch_draw, group = pyglet.graphics.OrderedGroup(2))
        if self.mode == "versus" and self.player == 1:
            print "===========   ROUND %d: FIGHT!  ===============" % self.round


    def on_draw(self):
        self.clear()
        self.lone_wheel.rotation = self.lone_wheel.x - constants.W_WIDTH/2
        if self.mode == "single":
            pyglet.text.Label('Epoch: %.2d' % self.epoch,
                              font_name='Neon Pixel-7',
                              font_size=140,
                              x=self.width//2, y=self.height//2,
                              anchor_x='center', anchor_y='center').draw()
        else:
            pyglet.text.Label('Player %d' % self.player,
                              font_name='Neon Pixel-7',
                              font_size=140,
                              x=self.width//2, y=self.height//2,
                              anchor_x='center', anchor_y='center').draw()
        if self.run_pyglet:
            self.batch_draw.draw()
            for i in range(0, int(math.ceil(constants.W_WIDTH / self.floor.img.width))):
                self.floor.img.blit(i * self.floor.img.width,0)
        glBegin(GL_TRIANGLES)
        glVertex2d(0,constants.F_HEIGHT - 5)
        glVertex2d(constants.W_WIDTH,constants.F_HEIGHT - 5)
        glVertex2d(constants.W_WIDTH/2, constants.F_HEIGHT + 110 - 5)
        glEnd()


    def out_of_screen(self):
        if (abs(self.get_pole_angle()) >= 60.0 or
           self.lone_wheel.obj_space.body.position.x <= 0 or self.lone_wheel.obj_space.body.position.x  >= constants.W_WIDTH):
            return True
        else:
            return False


    def reset(self, performance):
        self.lone_wheel.reset()
        self.smiley.reset()
        if self.mode == "single" or self.player == 1:
            self.lone_wheel.randomize(self.randomizer, new = True)
        else:
            self.lone_wheel.randomize(self.randomizer, new = False)
        self.smiley.randomize(self.randomizer, new = False)
        self.smiley.apply_impulse(self.randomizer, new = True)
        if self.run_pyglet and self.mode == "single":
            self.performances_file.write(str(performance) + "\n")
        self.epoch += 1
        self.current_iteration = 0
        self.wind = random.randint(-500, 500)
        self.friction = random.uniform(0.970, 0.999)

    def get_wheel_x(self):
        return self.lone_wheel.obj_space.body.position.x

    def get_smiley_y(self):
        return self.smiley.obj_space.body.position.y

    def get_pole_angle(self):
        if self.smiley.y == self.lone_wheel.y:
            if self.smiley.x > self.lone_wheel.x:
                arctan = 90
            else:
                arctan = -90
        else:
            if self.smiley.y > self.lone_wheel.y:
                 tan = (self.smiley.x - self.lone_wheel.x)/(self.smiley.y - self.lone_wheel.y)
                 arctan = (math.atan(tan)*180)/math.pi
            else:
                 tan = (self.smiley.x - self.lone_wheel.x)/(self.lone_wheel.y - self.smiley.y)
                 arctan = 180 - (math.atan(tan)*180)/math.pi
        return arctan

    def get_pole_angular_velocity(self):
        return (self.get_pole_angle() - self.pole_angle)*60

    def wheel_impulse(self, impulse):
        self.lone_wheel.obj_space.body.apply_impulse((impulse*5000, 0))

    def toggle_wind(self):
        if self.wind == 0:
            self.wind = random.randint(-500, 500)
        else:
            self.wind = 0

    def update_objects(self):
        self.lone_wheel.update()
        self.smiley.update()
        self.rod.update(self)
        self.smiley.obj_space.body.velocity *= 0.98
        self.lone_wheel.obj_space.body.velocity *= self.friction
        self.angular_velocity = self.get_pole_angular_velocity()

    def update(self, dt):
        self.update_objects()
        if self.mode == "single" and (self.current_iteration == constants.MAX_STEPS or self.out_of_screen()):
                perf = self.learner.get_performance(self.current_iteration, constants.MAX_STEPS)
                self.learner.controller.output(self.epoch,perf)
                if not self.run_pyglet:
                    self.learner.controller.update(self.epoch,perf)
                self.reset(perf)
                self.learner.last_performance = perf
                self.current_iteration = 0

        elif self.mode == "versus" and (self.current_iteration == constants.VS_MAX_STEPS or self.out_of_screen()):
                perf = self.learner.get_performance(self.current_iteration, constants.MAX_STEPS)
                if self.state == "active":
                    self.performances.append(perf)
                    print "Performance player %d: %d" % (self.player, perf)
                    self.state = "inactive"
                elif self.state == "inactive" and self.opponent.state == "inactive":
                        if self.player == 1:
                            self.round += 1
                            self.reset(perf)
                            self.opponent.reset(self.opponent.performances[-1])
                            self.state = "active"
                            self.opponent.state = "active"
                            if self.round > constants.VS_ROUNDS:
                                self.exit()
                            else:
                                print "\n\n===========   ROUND %d: FIGHT!  ===============" % self.round

        else:
                self.current_iteration += 1
                if self.mode == "single" or self.player == 1:
                    self.wheel_impulse(self.learner.controller.take_action(
                        AI_controller.State(
                            self.get_pole_angle(),
                            self.angular_velocity,
                            self.lone_wheel.x,
                            self.wind,
                            self.friction,
                            self.lone_wheel.obj_space.body.velocity[0],
                            self.lone_wheel.obj_space.body.velocity[1])))
                    if self.player == 1:
                        if random.randint(0, constants.IMPULSE_PROB) == 1:
                            impulse = random.randint(-25000, 25000)
                            self.smiley.obj_space.body.apply_impulse((impulse, 0))
                            self.opponent.smiley.obj_space.body.apply_impulse((impulse, 0))
                else:
                    import Opponent
                    self.wheel_impulse(self.learner.controller.take_action(
                        Opponent.State(
                            self.get_pole_angle(),
                            self.angular_velocity,
                            self.lone_wheel.x,
                            self.wind,
                            self.friction,
                            self.lone_wheel.obj_space.body.velocity[0],
                            self.lone_wheel.obj_space.body.velocity[1])))

        if self.run_pyglet:
            self.smiley.obj_space.body.apply_impulse((self.wind, 0))
        self.space.step(dt)


    def exit(self):
        if self.player == 1:
            means  = [numpy.mean(self.performances), numpy.mean(self.opponent.performances)]
            stdevs = [numpy.std(self.performances),  numpy.std(self.opponent.performances)]
            print "\n\n\n================= FIM DE JOGO ====================="
            print "Performances do jogador #1: ", self.performances
            print "Média do jogador #1: %.3f" % means[0]
            print "Desvio padrão do jogador #1: %.3f" % stdevs[0]
            print "Performances do jogador #2: ", self.opponent.performances
            print "Média do jogador #2: %.3f" % means[1]
            print "Desvio padrão do jogador #2: %.3f" % stdevs[1]

            if means[0] > means[1]:
                print "\n\n================== VENCEDOR: JOGADOR #1 ======================="
            elif means[1] > means[0]:
                print "\n\n================== VENCEDOR: JOGADOR #2 ======================="
            else:
                if stdevs[0] > stdevs[1]:
                    "\n\n================== VENCEDOR: JOGADOR #1 ======================="
                elif stdevs[1] > stdevs[1]:
                    "\n\n================== VENCEDOR: JOGADOR #2 ======================="
                else:
                    "\n\n================== EMPATE ======================="
            exit()
