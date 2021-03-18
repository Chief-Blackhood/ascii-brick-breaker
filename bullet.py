import config
from generic import GenericObject


class Bullet(GenericObject):
    TYPE = "bullet"

    def __init__(self):
        super().__init__([1, 1], config.BACK_COLOR + "💈")
        self._x = 0
        self._y = config.FRAME_HEIGHT

    @property
    def get_x(self):
        """getter"""
        return self._x

    @property
    def get_y(self):
        """getter"""
        return self._y

    def set_x(self, value):
        """setter"""
        self._x = value

    def set_y(self, value):
        """setter"""
        self._y = value

    def update_bullet(self):
        """update position of the ball and keep it inside the walls"""
        bullet = self
        bullet._y = bullet.get_y - 1
