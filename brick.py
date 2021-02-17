import config
from generic import GenericObject


class Brick(GenericObject):
    TYPE = "brick"

    def __init__(self):
        super().__init__([4, 2], config.BACK_COLOR + "🟥")
        self._variety = 3

    @property
    def get_element(self):
        if self._variety == 3:
            return config.BACK_COLOR + "🟥"
        if self._variety == 2:
            return config.BACK_COLOR + "🟧"
        if self._variety == 1:
            return config.BACK_COLOR + "🟩"