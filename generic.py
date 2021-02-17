import numpy as np

import config

class GenericObject:
    currently_active = 0
    DEAD_FLAG = 1
    TYPE = "generic"

    def __init__(self, shape, element):
        self.__class__.currently_active += 1
        self._shape = shape
        self._element = element

    def draw(self):
        """
        Returns a dictionary containing co-ordinates and size of an object
        """
        if self.TYPE == "ball":
            return {
                "coord": [self._y, self._x],
                "size": self._shape,
                "velocity": self._velocity,
            }

        else:
            return {
            "coord": [self._y, self._x],
            "size": self._shape,
        }

    @property
    def get_element(self):
        return self._element

    @property
    def get_x(self):
        return self._x

    @property
    def get_y(self):
        return self._y

    def set_x(self, value):
        self._x = value

    def set_y(self, value):
        self._y = value

    @property
    def get_shape(self):
        return self._shape

    def set_shape(self, value):
        self._shape = value

    def set_element(self, value):
        self._element = value
