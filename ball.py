import config
from generic import GenericObject


class Ball(GenericObject):
    TYPE = "ball"

    def __init__(self):
        super().__init__([1, 1], config.BACK_COLOR + "🌎")
        self._x = 0
        self._y = config.FRAME_HEIGHT
        self._through_ball = False
        self._velocity = [0, 0]
        self._temp_velocity = [1, 1]

    @property
    def get_velocity(self):
        return self._velocity

    @property
    def get_temp_velocity(self):
        return self._temp_velocity

    @property
    def get_through_ball(self):
        return self._through_ball

    def set_velocity(self, value):
        self._velocity = value

    def set_temp_velocity(self, value):
        self._temp_velocity = value

    def set_through_ball(self, value):
        self._through_ball = value

    @property
    def get_x(self):
        return self._x

    @property
    def get_y(self):
        return self._y

    def update_ball(self):
        ball = self
        velocity = ball.get_velocity
        ball._x = ball.get_x + velocity[0]
        ball._y = ball.get_y - velocity[1]

        if ball.get_x <= 0:
            ball._x = 0
            velocity[0] = -velocity[0]

        if ball.get_x >= config.FRAME_WIDTH - 1:
            ball._x = config.FRAME_WIDTH - 2
            velocity[0] = -velocity[0]

        if ball.get_y <= 0:
            ball._y = 0
            velocity[1] = -velocity[1]

        if ball.get_y >= config.FRAME_HEIGHT - 1:
            velocity[0] = velocity[1] = 0

    def give_velocity(self, sticky):
        if sticky and self._temp_velocity != [0, 0]:
            self._velocity = self._temp_velocity
        elif self._velocity == [0, 0]:
            self._velocity = [1, 1]
