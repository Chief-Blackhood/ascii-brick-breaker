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
from utils import clear_terminal_screen, reposition_cursor, get_key_pressed, clear_buffer


class Game:
    _refresh_time = 1 / FRAME_RATE
    brick_string = [
                    "111"
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
                    # "00000000011000000000",
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
        self._initialize_bricks()
        self._loop()

    def _initialize_bricks(self):
        for row in range(len(self.brick_string)):
            for col in range(len(self.brick_string[0])):
                if self.brick_string[row][col] != '0':
                    brick = Brick()
                    brick._variety = random.randint(1, 3)
                    brick._x = 48 + 2*brick.get_shape[0]*col
                    brick._y = 5 + row
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

    def _draw(self):
        self.__grid = np.array([[Fore.WHITE + config.BACK_COLOR + " "
                                 for _ in range(config.FRAME_WIDTH)]
                                for _ in range(config.FRAME_HEIGHT)])

        self._draw_in_range(self.__paddle.draw(), self.__paddle.get_element)
        self._draw_bricks()
        self._draw_in_range(self.__ball.draw(), self.__ball.get_element)

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
        for obj in self.__bricks:
            print(obj.draw())
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
            self._info_print(count)
            self._initialize_ball()
            self.__ball.update_ball()
            self._detect_ball_paddle_collision()

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
