import config
from ball import Ball
from generic import GenericObject


class GenericPowerUp(GenericObject):
    TYPE = "power_up"

    def __init__(self):
        super().__init__([1, 1], config.BACK_COLOR + "💪")
        self._x = 0
        self._y = 0
        self._variety = 0

    def activate_power_up(self, obj):
        pass

    @property
    def get_variety(self):
        """getter"""
        return self._variety


class ExpandPaddle(GenericPowerUp):
    """power up to expand paddle"""
    def __init__(self):
        super().__init__()
        self._variety = 1

    def activate_power_up(self, obj):
        """To update the size and emoji of the paddle"""
        obj.set_x(obj.get_x - 4)
        obj.set_shape([15, 2])
        obj.set_element(config.BACK_COLOR + "🌀")

    @property
    def get_element(self):
        """getter Overridden"""
        return config.BACK_COLOR + "💪"


class ShrinkPaddle(GenericPowerUp):
    """Power up to shrink the paddle"""
    def __init__(self):
        super().__init__()
        self._variety = 2

    def activate_power_up(self, obj):
        """To update the size and emoji of the paddle"""
        obj.set_x(obj.get_x + 4)
        obj.set_shape([7, 2])
        obj.set_element(config.BACK_COLOR + "💀")

    @property
    def get_element(self):
        """getter Overridden"""
        return config.BACK_COLOR + "🍼"


class SpeedUpBall(GenericPowerUp):
    """To increase the speed of the ball"""
    def __init__(self):
        super().__init__()
        self._variety = 3

    def activate_power_up(self, obj):
        """To update the frame rate so as to give a sense of speed increment"""
        config.FRAME_RATE = min(25, config.FRAME_RATE + 5)

    @property
    def get_element(self):
        """getter Overridden"""
        return config.BACK_COLOR + "🌠"


class StickyPaddle(GenericPowerUp):
    """Power up so that ball sticks to the paddle"""
    def __init__(self):
        super().__init__()
        self._variety = 4

    def activate_power_up(self, obj):
        """To make the paddle sticky"""
        obj.set_sticky(True)

    @property
    def get_element(self):
        """getter Overridden"""
        return config.BACK_COLOR + "🍭"


class ThroughBall(GenericPowerUp):
    """Power up that makes the ball got through everything"""
    def __init__(self):
        super().__init__()
        self._variety = 5

    def activate_power_up(self, obj):
        """Change the emoji and attribute of the ball"""
        obj.set_through_ball(True)
        obj.set_element(config.BACK_COLOR + "🔥")

    @property
    def get_element(self):
        """getter Overridden"""
        return config.BACK_COLOR + "🧿"


class BallMultiplier(GenericPowerUp):
    """To multiply the balls present on the screen by two"""
    def __init__(self):
        super().__init__()
        self._variety = 6

    def activate_power_up(self, obj):
        """To iterate over all the present balls and make copies of them with velocity in the opposite direction"""
        temp_balls = []
        for ball in obj:
            if ball.get_velocity != [0, 0]:
                new_ball = Ball()
                velocity = ball.get_velocity
                new_ball.set_velocity([-velocity[0], -velocity[1]])
                new_ball.set_x(ball.get_x)
                new_ball.set_y(ball.get_y)
                new_ball.set_through_ball(ball.get_through_ball)
                temp_balls.append(ball)
                temp_balls.append(new_ball)
            else:
                temp_balls.append(ball)

        return temp_balls

    @property
    def get_element(self):
        """getter Overridden"""
        return config.BACK_COLOR + "🍒"

class ShootingPaddle(GenericPowerUp):
    def __init__(self):
        super().__init__()
        self._variety = 7

    @property
    def get_element(self):
        """getter Overridden"""
        return config.BACK_COLOR + "🥢"
