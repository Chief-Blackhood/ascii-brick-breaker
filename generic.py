import numpy as np
from colorama import Fore

import config
from utils import filler


def connector(grid, hgt, wdt, color):
    assert  len(grid) == len(color)
    assert  len(grid[0]) == len(color[0])

    res = np.array([])

    for row in range(hgt):
        for col in range(wdt):
            curr_str = ""
            color_val = color[row][col]

            if color_val[0]:
                curr_str += color_val[0]
            else:
                curr_str += Fore.BLACK

            if color_val[1]:
                curr_str += color_val[1]
            else:
                curr_str += config.BACK_COLOR

            curr_str += grid[row][col]
            res = np.append(res, curr_str)

    res = res.reshape((hgt, wdt))
    return res

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

    def set_x(self, value):
        self._x = value

    @property
    def get_shape(self):
        return self._shape