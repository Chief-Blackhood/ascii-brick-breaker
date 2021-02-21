import config
from generic import GenericObject


class Paddle(GenericObject):
    TYPE = "paddle"

    def __init__(self):
        if config.DEBUG:
            super().__init__([86, 2], config.BACK_COLOR + "🧱")
            self._x = 0
        else:
            super().__init__([11, 2], config.BACK_COLOR + "🧱")
            self._x = round(config.FRAME_WIDTH / 2 - round(self._shape[0] / 2)) - 2
        self._y = round(config.FRAME_HEIGHT - 2)
        self._sticky = False

    @property
    def get_sticky(self):
        """getter"""
        return self._sticky

    def set_sticky(self, value):
        """setter"""
        self._sticky = value

    def update_paddle(self, value, ball):
        """To update the position of the paddle and the ball which is on it"""
        obj = self
        if config.FRAME_WIDTH - 2*obj.get_shape[0] >= obj.get_x + value >= 0:
            obj.set_x(obj.get_x + value)
            if ball.get_velocity == [0, 0]:
                ball.set_x(ball.get_x + value)
