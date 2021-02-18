import config
from ball import Ball
from generic import GenericObject


class GenericPowerUp(GenericObject):
    TYPE = "power_up"

    def __init__(self):
        super().__init__([2, 1], config.BACK_COLOR + "💪")
        self._x = 0
        self._y = 0
        self._variety = 0

    def activate_power_up(self, obj):
        pass

    @property
    def get_variety(self):
        return self._variety


class ExpandPaddle(GenericPowerUp):
    def __init__(self):
        super().__init__()
        self._variety = 1

    def activate_power_up(self, obj):
        obj.set_x(obj.get_x - 4)
        obj.set_shape([15, 2])
        obj.set_element(config.BACK_COLOR + "🌀")

    @property
    def get_element(self):
        return config.BACK_COLOR + "💪"


class ShrinkPaddle(GenericPowerUp):
    def __init__(self):
        super().__init__()
        self._variety = 2

    def activate_power_up(self, obj):
        obj.set_x(obj.get_x + 4)
        obj.set_shape([7, 2])
        obj.set_element(config.BACK_COLOR + "💀")

    @property
    def get_element(self):
        return config.BACK_COLOR + "🍼"


class SpeedUpBall(GenericPowerUp):
    def __init__(self):
        super().__init__()
        self._variety = 3

    def activate_power_up(self, obj):
        config.FRAME_RATE = min(25, config.FRAME_RATE + 5)

    @property
    def get_element(self):
        return config.BACK_COLOR + "🌠"


class StickyPaddle(GenericPowerUp):
    def __init__(self):
        super().__init__()
        self._variety = 4

    def activate_power_up(self, obj):
        obj.set_sticky(True)

    @property
    def get_element(self):
        return config.BACK_COLOR + "🍭"


class ThroughBall(GenericPowerUp):
    def __init__(self):
        super().__init__()
        self._variety = 5

    def activate_power_up(self, obj):
        obj.set_through_ball(True)
        obj.set_element(config.BACK_COLOR + "🔥")

    @property
    def get_element(self):
        return config.BACK_COLOR + "🧿"


class BallMultiplier(GenericPowerUp):
    def __init__(self):
        super().__init__()
        self._variety = 6

    def activate_power_up(self, obj):
        temp_balls = []
        for ball in obj:
            if ball.get_velocity != [0, 0]:
                new_ball = Ball()
                velocity = ball.get_velocity
                new_ball.set_velocity([-velocity[0], -velocity[1]])
                new_ball.set_x(ball.get_x)
                new_ball.set_y(ball.get_y)
                temp_balls.append(ball)
                temp_balls.append(new_ball)

        return temp_balls

    @property
    def get_element(self):
        return config.BACK_COLOR + "🍒"
