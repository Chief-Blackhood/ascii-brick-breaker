import config
from generic import GenericObject


class Boss(GenericObject):
    TYPE = "boss"

    def __init__(self):
        super().__init__([1, 1], config.BACK_COLOR + "🛸")
        self._variety = 1

    @property
    def get_variety(self):
        """getter"""
        return self._variety

    def set_variety(self, value):
        """setter"""
        self._variety = value

    @property
    def get_element(self):
        """getter"""
        if self._variety == 1:
            return config.BACK_COLOR + "🛸"
        if self._variety == 2:
            return config.BACK_COLOR + "👽"
        if self._variety == 3:
            return config.BACK_COLOR + "💠"
        if self._variety == 4:
            return config.BACK_COLOR + "🚀"


class Bomb(GenericObject):
    TYPE = "bomb"

    def __init__(self):
        super().__init__([1, 1], config.BOMB_BACKGROUND + "💣")

    def update_bomb(self):
        self.set_y(self.get_y + 0.5)
