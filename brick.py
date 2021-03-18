import config
from generic import GenericObject


class Brick(GenericObject):
    TYPE = "brick"

    def __init__(self):
        super().__init__([4, 2], config.BACK_COLOR + "🟥")
        self._variety = 3
        self._explode = -1
        self._rainbow = False

    @property
    def get_variety(self):
        """getter"""
        return self._variety

    def set_variety(self, value):
        """setter"""
        self._variety = value

    @property
    def get_explode(self):
        """getter"""
        return self._explode

    def set_explode(self, value):
        """setter"""
        self._explode = value

    @property
    def get_rainbow(self):
        """getter"""
        return self._rainbow

    def set_rainbow(self, value):
        """setter"""
        self._rainbow = value

    @property
    def get_element(self):
        """getter"""
        if self._variety == 1:
            return config.BACK_COLOR + "🟩"
        if self._variety == 2:
            return config.BACK_COLOR + "🟧"
        if self._variety == 3:
            return config.BACK_COLOR + "🟥"
        if self._variety == 4:
            return config.BACK_COLOR + "⬛"
        if self._variety == 5:
            return config.BACK_COLOR + "🟨"
