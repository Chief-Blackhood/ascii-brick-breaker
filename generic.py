class GenericObject:
    TYPE = "generic"

    def __init__(self, shape, element):
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
        """getter"""
        return self._element

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

    @property
    def get_shape(self):
        """getter"""
        return self._shape

    def set_shape(self, value):
        """setter"""
        self._shape = value

    def set_element(self, value):
        """setter"""
        self._element = value
