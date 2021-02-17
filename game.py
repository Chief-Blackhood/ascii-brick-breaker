import time
import os
import random
from math import floor, ceil

import numpy as np
from colorama import init as coloramaInit, Fore, Style, Back

import config
from ball import Ball
from brick import Brick
from config import FRAME_RATE
from kbhit import KBHit
from paddle import Paddle
from powerup import ExtendPaddle
from utils import clear_terminal_screen, reposition_cursor, get_key_pressed, clear_buffer


class Game:
    _refresh_time = 1 / FRAME_RATE
    brick_string = [
                    # "1",
                    # "111",

                    # "00000010000000000000",
                    # "00000001000000000000",
                    # "00001100000000110000",
                    # "00110010000001001100",
                    # "01111101000010111110",
                    # "11111110111101111111",
                    # "11111111000011111111",
                    # "11111111111111111111",
                    # "11111111111111111111",
                    # "11111111111111111111",
                    # "11111111111111111111",
                    # "01111111111111111110",
                    # "00111111111111111100",
                    # "00011111111111111000",
                    # "00001111111111110000",
                    # "00000111111111100000",
                    # "00000011111111000000",
                    # "00000001111110000000",
                    # "00000000111100000000",
                    # "00000000011000000000",
                    "00000111111111100000",
                    "00000111111111100000",
                    "00000111111111100000",
                    "00000111111111100000",
                    "00000111111111100000",
                    "00000111111111100000",
                    "00000111111111100000",
                    ]

    def _draw_in_range(self, info, obj):
        row = round(info["size"][1])
        col = round(info["size"][0])
        x = int(round(info["coord"][1]))
        y = int(round(info["coord"][0]))
        for i in range(row):
            for j in range(2*col):
                self.__grid[y + i][x + j] = obj if j % 2 else ""

    def __init__(self):
        coloramaInit(autoreset=True)
        self.__grid = [[]]
        self.__game_status = 0
        self.__keys = KBHit()
        self.__paddle = Paddle()
        self.__ball = Ball()
        clear_terminal_screen()
        self.__bricks = []
        self.__powerup_shown = []
        self.__active_powerup = []
        self._initialize_bricks()
        self._loop()

    def _initialize_bricks(self):
        for row in range(len(self.brick_string)):
            for col in range(len(self.brick_string[0])):
                if self.brick_string[row][col] != '0':
                    brick = Brick()
                    brick._variety = random.randint(1, 3)
                    brick._x = 5 + 2*brick.get_shape[0]*col
                    brick._y = 10 + brick.get_shape[1]*row
                    self.__bricks.append(brick)

    def _initialize_ball(self):
        ball = self.__ball
        paddle = self.__paddle
        if ball.get_velocity == [0, 0] and ball.get_y >= config.FRAME_HEIGHT - 1:
            ball._x = paddle.get_x + random.randint(0, 2 * floor(paddle.get_shape[0]) - 1)
            ball._y = paddle.get_y - 1

    def _draw_bricks(self):
        for obj in self.__bricks:
            self._draw_in_range(obj.draw(), obj.get_element)
            
    def _draw_powerups(self):
        for obj in self.__powerup_shown:
            if obj.get_y < config.FRAME_HEIGHT - 2:
                self._draw_in_range(obj.draw(), obj.get_element)
            else:
                self.__powerup_shown.remove(obj)

    def _update_powerups(self):
        for obj in self.__powerup_shown:
            obj.set_y(obj.get_y + 0.5)

    def _draw(self):
        self.__grid = np.array([[Fore.WHITE + config.BACK_COLOR + " "
                                 for _ in range(config.FRAME_WIDTH)]
                                for _ in range(config.FRAME_HEIGHT)])

        self._draw_in_range(self.__paddle.draw(), self.__paddle.get_element)
        self._draw_bricks()
        self._draw_in_range(self.__ball.draw(), self.__ball.get_element)
        self._draw_powerups()

        sra = str(Style.RESET_ALL)
        grid_str = "\n".join(
            [sra.join(row[:]) for row in self.get_grid()])

        # only a single print at the end makes rendering efficient
        os.write(1, str.encode(grid_str))

    def _terminate(self, we_won):
        self.__game_status = -1
        os.system('setterm -cursor on')

    def _handle_input(self):
        inputted = ""

        if self.__keys.kbhit():
            inputted = self.__keys.getch()

        cin = get_key_pressed(inputted)
        if cin == -1:
            self._terminate(-1)
        elif cin == 'a':
            self.__paddle.update_paddle(-2, self.__ball)
        elif cin == 'd':
            self.__paddle.update_paddle(2, self.__ball)
        elif cin == ' ':
            self.__ball.give_velocity()

        clear_buffer()
        return cin

    def _info_print(self, count):
        pass
        # for obj in self.__bricks:
        #     print(obj.draw())
        # print(self.__paddle.draw())
        # info = self.__ball.draw()
        # x = int(floor(info["coord"][1])) if info["velocity"][0] > 0 else int(ceil(info["coord"][1]))
        # y = int(floor(info["coord"][0])) if info["velocity"][1] < 0 else int(ceil(info["coord"][0]))
        # print(count)
        # print(x,y)
        # # print(self.__paddle.get_x, self.__paddle.get_y)
        print(self.__ball.draw())
        # print(self.__ball.get_velocity)

    def _loop(self):
        self.__game_status = 1

        last_key_pressed = ""
        clear_terminal_screen()
        count = 0

        while self.__game_status == 1:
            reposition_cursor()
            count += 1
            self._detect_brick_ball_collision()
            self.__ball.update_ball()
            self._update_powerups()
            self._initialize_ball()
            self._detect_ball_paddle_collision()
            self._info_print(count)
            self._draw()

            last_time = time.perf_counter()
            last_key_pressed = self._handle_input()

            while time.perf_counter() - last_time < self._refresh_time:
                pass

    def get_grid(self):
        """getter"""
        return self.__grid

    def _detect_ball_paddle_collision(self):
        if self.__paddle.get_x - 1 <= self.__ball.get_x <= self.__paddle.get_x + self.__paddle.get_shape[0]*2\
                and self.__ball.get_y == self.__paddle.get_y - 1:
            self.__ball.get_velocity[1] = -self.__ball.get_velocity[1]
            if self.__ball.get_velocity[1] != 0:
                center = round(self.__paddle.get_x + self.__paddle.get_shape[0])
                distance = self.__ball.get_x - center
                self.__ball.get_velocity[0] = self.__ball.get_velocity[0] + round(distance/self.__paddle.get_shape[0]*2)

    def _detect_brick_ball_collision(self):
        iterations = 20
        ball = self.__ball
        brick_hit = None
        step = 0
        index = -1
        got = False
        for i in range(1, iterations+1):
            if ball.get_velocity[0] == 1:
                x_f = ball.get_x + 1.5*i*ball.get_velocity[0]/iterations + 0.5 #(1 1)
            else:
                x_f = ball.get_x + i*ball.get_velocity[0]/iterations + 0.5 #(1 1)
            y_f = ball.get_y - i*ball.get_velocity[1]/iterations
            for j, brick in enumerate(self.__bricks):
                # print(x_f, y_f)
                if brick.get_x <= x_f < brick.get_x + brick.get_shape[0]*2 and brick.get_y <= y_f <= brick.get_y + brick.get_shape[1] - 1:
                    brick_hit = brick
                    step = i
                    index = j
                    got = True
                    # print(x_f, y_f)
                    break
            if got:
                # print("got hello")
                break

        if not got:
            return
        x_previous = ball.get_x + (step - 1)*ball.get_velocity[0]/iterations + 0.5
        y_previous = ball.get_y - (step - 1)*ball.get_velocity[1]/iterations

        # print(x_previous, y_previous)
        # print(brick_hit.get_shape[1]+ brick_hit.get_y - 1)
        # print(brick_hit.get_y + brick_hit.get_shape[1])
        # print(brick_hit.get_x, brick_hit.get_y)#brick_hit.get_x + brick_hit.get_shape[0]*2)

        if brick_hit.get_x - 1 <= x_previous <= brick_hit.get_x + brick_hit.get_shape[0]*2 + 1 \
                and (y_previous < brick_hit.get_y or y_previous >= brick_hit.get_y + brick_hit.get_shape[1] - 1):
            # print("hello")
            ball._x = floor(x_previous)
            if y_previous < brick_hit.get_y:
                ball._y = brick_hit.get_y - 1
            else:
                ball._y = brick_hit.get_y + brick_hit.get_shape[1]
            ball._velocity[1] *= -1


        elif brick_hit.get_x >= x_previous or x_previous >= brick_hit.get_x + brick_hit.get_shape[0] * 2 \
                and (brick_hit.get_y <= y_previous < brick_hit.get_y + brick_hit.get_shape[1]):
            # print("hello")
            if brick_hit.get_x >= x_previous:
                ball._x = brick_hit.get_x - 2
            else:
                ball._x = brick_hit.get_x + brick_hit.get_shape[0] * 2 - 1
            ball._y = int(y_previous)
            ball._velocity[0] *= -1

        else:
            ball._velocity[0] *= -1
            ball._velocity[1] *= -1
            ball._y = round(y_previous)
            ball._x = round(x_previous)

        if brick_hit._variety == 1:
            del self.__bricks[index]
            powerup = ExtendPaddle()
            powerup.set_x(brick_hit.get_x + 2)
            powerup.set_y(brick_hit.get_y)
            self.__powerup_shown.append(powerup)
        else:
            brick_hit._variety -= 1

    # def _detect_brick_ball_collision(self):
    #     iterations = 20
    #     ball = self.__ball
    #     brick_hit = None
    #     index = []
    #     step = 0
    #     got = []
    #     for i in range(1, iterations+1):
    #         x_f = ball.get_x + i*ball.get_velocity[0]/iterations + 0.5
    #         y_f = ball.get_y - i*ball.get_velocity[1]/iterations
    #         for j, brick in enumerate(self.__bricks):
    #             if (brick.get_x <= x_f < brick.get_x + brick.get_shape[0]*2
    #                 or brick.get_x <= x_f + 1 < brick.get_x + brick.get_shape[0]*2
    #                 or brick.get_x <= x_f - 1 < brick.get_x + brick.get_shape[0]*2) \
    #                     and brick.get_y <= y_f <= brick.get_y + brick.get_shape[1] - 1:
    #                 brick_hit = brick
    #                 step = i
    #                 got.append(brick_hit)
    #                 index.append(j)
    #             if brick.get_x <= x_f < brick.get_x + brick.get_shape[0]*2\
    #                     and (brick.get_y <= y_f <= brick.get_y + brick.get_shape[1] - 1
    #                          or brick.get_y <= y_f + 0.5 <= brick.get_y + brick.get_shape[1] - 1
    #                          or brick.get_y <= y_f - 0.5 <= brick.get_y + brick.get_shape[1] - 1):
    #                 brick_hit = brick
    #                 step = i
    #                 got.append(brick_hit)
    #                 index.append(j)
    #         if len(got):
    #             x_previous = ball.get_x + (step - 1)*ball.get_velocity[0]/iterations + 0.5
    #             y_previous = ball.get_y - (step - 1)*ball.get_velocity[1]/iterations
    #             for obj in got:
    #                 if obj.get_x <= x_previous <= obj.get_x + obj.get_shape[0]*2 \
    #                         and (y_previous < obj.get_y or y_previous >= obj.get_y + obj.get_shape[1] - 1):
    #                     ball._x = floor(x_previous)
    #                     if y_previous < obj.get_y:
    #                         ball._y = obj.get_y - 1
    #                     else:
    #                         ball._y = obj.get_y + obj.get_shape[1]
    #                     ball._velocity[1] *= -1
    #
    #                 elif obj.get_x >= x_previous or x_previous >= obj.get_x + obj.get_shape[0] * 2 \
    #                         and (obj.get_y <= y_previous < obj.get_y + obj.get_shape[1]):
    #                     if obj.get_x >= x_previous:
    #                         ball._x = obj.get_x - 2
    #                     else:
    #                         ball._x = obj.get_x + obj.get_shape[0] * 2 - 1
    #                     ball._y = int(y_previous)
    #                     ball._velocity[0] *= -1
    #
    #                 else:
    #                     ball._velocity[0] *= -1
    #                     ball._velocity[1] *= -1
    #                     ball._y = round(y_previous)
    #                     ball._x = round(x_previous)
    #
    #                 if brick_hit._variety == 1:
    #                     del self.__bricks[index]
    #                 else:
    #                     brick_hit._variety -= 1

