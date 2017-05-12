class State:
    def __init__(self, rod_angle, angular_velocity, wheel_x, wind = 0, friction = 0.99, velocity_x = 0, velocity_y = 0):
        self.rod_angle        = rod_angle
        self.angular_velocity = angular_velocity
        self.wheel_x          = wheel_x
        self.wind             = wind
        self.friction         = friction
        self.velocity_x       = velocity_x
        self.velocity_y       = velocity_y
