from .controller import Controller
from .state      import State

class Learner:
    def __init__(self, game, load):
        self.current_iteration = 0
        self.last_performance = 0
        self.controller = Controller(game, load, State(game.get_pole_angle(),
                                                    game.angular_velocity,
                                                    game.lone_wheel.x,
                                                    game.wind,
                                                    game.friction,
                                                    game.lone_wheel.obj_space.body.velocity[0],
                                                    game.lone_wheel.obj_space.body.velocity[1]))

    def get_performance(self, iteration, max_steps):
        performance = 2*max_steps + 2*(iteration - max_steps)
        return performance
