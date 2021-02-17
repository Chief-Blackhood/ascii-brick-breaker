import config
from generic import GenericObject


class GenericPowerUp(GenericObject):
    TYPE = "power_up"

    def __init__(self):
        super().__init__([2, 1], config.BACK_COLOR + "💪")
        self._active_time = 300
        self._x = 0
        self._y = 0

    def activate_power_up(self, obj):
        pass


class ExtendPaddle(GenericPowerUp):
    def __init__(self):
        super().__init__()

    def activate_power_up(self, obj):
        obj.set_x(obj.get_x - 4)
        obj.set_shape([13, 2])

    @property
    def get_element(self):
        return config.BACK_COLOR + "💪"
