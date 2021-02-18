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
from powerup import ShrinkPaddle, ExpandPaddle, SpeedUpBall, StickyPaddle, ThroughBall, BallMultiplier
from utils import clear_terminal_screen, reposition_cursor, get_key_pressed, clear_buffer


class Game:
    _refresh_time = 1 / FRAME_RATE
    brick_string = [
        "00000111111111100000",
        "00000111111111100000",
        "00000111111111100000",
        "00000111111111100000",
        "00000111111111100000",
        "00000111111111100000",
        "00000111111111100000",
        # "00020211111111202000",
        # "00010111111111101000",
        # "00020111111111102000",
        # "00010111111111101000",
        # "00010111111111101000",
        # "00020111111111102000",
        # "00010211111111201000",
        # "00010000000000001000",
        # "00021112111121112000",
    ]

    def _draw_in_range(self, info, obj):
        row = round(info["size"][1])
        col = round(info["size"][0])
        x = int(round(info["coord"][1]))
        y = int(round(info["coord"][0]))
        for i in range(row):
            for j in range(2 * col):
                self.__grid[y + i][x + j] = obj if j % 2 else ""

    def __init__(self):
        coloramaInit(autoreset=True)
        self.__grid = [[]]
        self._count = 0
        self.__game_status = 0
        self.__keys = KBHit()
        self.__paddle = Paddle()
        self.__ball = Ball()
        self.__balls = []
        self.__balls.append(self.__ball)
        clear_terminal_screen()
        self.__bricks = []
        self.__powerup_shown = []
        self.__lives = 8
        self.__score = 0
        self.__time = 0
        self.__active_powerup = [[False, 0], [False, 0], [False, 0], [False, 0], [False, 0], [False, 0]]
        self._initialize_bricks()
        self._loop()

    def _initialize_bricks(self):
        for row in range(len(self.brick_string)):
            for col in range(len(self.brick_string[0])):
                if self.brick_string[row][col] != '0':
                    brick = Brick()
                    # if self.brick_string[row][col] == '2':
                    #     brick.set_variety(4)
                    # else:
                    #     brick.set_variety(random.randint(1, 3))
                    brick.set_variety(1)
                    brick.set_x(5 + 2 * brick.get_shape[0] * col)
                    brick.set_y(10 + brick.get_shape[1] * row)
                    self.__bricks.append(brick)

    def _initialize_ball(self):
        if len(self.__balls) == 1:
            ball = self.__balls[0]
            paddle = self.__paddle
            if ball.get_velocity == [0, 0] and ball.get_y >= config.FRAME_HEIGHT - 1:
                ball.set_x(paddle.get_x + random.randint(0, 2 * floor(paddle.get_shape[0]) - 1))
                ball.set_y(paddle.get_y - 1)
                self.__lives -= 1
        else:
            for ball in self.__balls:
                if ball.get_velocity == [0, 0] and ball.get_y >= config.FRAME_HEIGHT - 1:
                    self.__balls.remove(ball)

    def _draw_bricks(self):
        for obj in self.__bricks:
            self._draw_in_range(obj.draw(), obj.get_element)

    def _draw_powerups(self):
        for obj in self.__powerup_shown:
            if obj.get_y < config.FRAME_HEIGHT - 2:
                self._draw_in_range(obj.draw(), obj.get_element)
            else:
                if self.__paddle.get_x <= obj.get_x <= self.__paddle.get_x + self.__paddle.get_shape[0] * 2:
                    self.__active_powerup[obj.get_variety - 1][0] = True
                    self.__active_powerup[obj.get_variety - 1][1] = self._count
                    if obj.get_variety == 1 or obj.get_variety == 2 or obj.get_variety == 4:
                        obj.activate_power_up(self.__paddle)
                    elif obj.get_variety == 3 or obj.get_variety == 5:
                        for ball in self.__balls:
                            obj.activate_power_up(ball)
                    elif obj.get_variety == 6:
                        if len(self.__balls) <= 10:
                            self.__balls = obj.activate_power_up(self.__balls)

                self.__powerup_shown.remove(obj)

    def _update_powerups(self):
        for obj in self.__powerup_shown:
            obj.set_y(obj.get_y + 0.5)
        for i, obj in enumerate(self.__active_powerup):
            if obj[0] and self._count - obj[1] > 300:
                obj[0] = False
                if i == 0 and not self.__active_powerup[1][0]:
                    self.__paddle.set_x(self.__paddle.get_x + 4)
                    self.__paddle.set_shape([11, 2])
                    self.__paddle.set_element(config.BACK_COLOR + "🧱")
                elif i == 1 and not self.__active_powerup[0][0]:
                    if self.__paddle.get_x >= config.FRAME_WIDTH - self.__paddle.get_shape[0]*2 - 3:
                        self.__paddle.set_x(self.__paddle.get_x - 8)
                    elif self.__paddle.get_x > 4:
                        self.__paddle.set_x(self.__paddle.get_x - 4)
                    self.__paddle.set_shape([11, 2])
                    self.__paddle.set_element(config.BACK_COLOR + "🧱")
                elif i == 2:
                    self.__ball.set_element(config.BACK_COLOR + "🌎")
                    config.FRAME_RATE = 20
                elif i == 3:
                    self.__paddle.set_sticky(False)
                elif i == 4:
                    self.__ball.set_through_ball(False)
                    self.__ball.set_element(config.BACK_COLOR + "🌎")

    def _draw(self):
        self.__grid = np.array([[Fore.WHITE + config.BACK_COLOR + " "
                                 for _ in range(config.FRAME_WIDTH)]
                                for _ in range(config.FRAME_HEIGHT)])

        self._draw_in_range(self.__paddle.draw(), self.__paddle.get_element)
        self._draw_bricks()
        for ball in self.__balls:
            self._draw_in_range(ball.draw(), self.__ball.get_element)
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
            for ball in self.__balls:
                self.__paddle.update_paddle(-2, ball)
        elif cin == 'd':
            for ball in self.__balls:
                self.__paddle.update_paddle(2, ball)
        elif cin == ' ':
            for ball in self.__balls:
                ball.give_velocity(self.__paddle.get_sticky)

        clear_buffer()
        return cin

    def _info_print(self):
        pass
        print("⏱ Time: ", self.__time)
        print("💓 Lives: ", self.__lives)
        print("Score: ", self.__score)
        # for obj in self.__bricks:
        #     print(obj.draw())
        # print(self.__paddle.draw())
        # info = self.__ball.draw()
        # x = int(floor(info["coord"][1])) if info["velocity"][0] > 0 else int(ceil(info["coord"][1]))
        # y = int(floor(info["coord"][0])) if info["velocity"][1] < 0 else int(ceil(info["coord"][0]))
        # print(self._count)
        # print(x,y)
        # # print(self.__paddle.get_x, self.__paddle.get_y)
        # for ball in self.__balls:
        #     print(ball.draw())
        # print(self.__ball.get_velocity)

    def _loop(self):
        self.__game_status = 1
        frames_looped = 0

        last_key_pressed = ""
        clear_terminal_screen()

        while self.__game_status == 1:
            frames_looped += 1
            if frames_looped >= config.FRAME_RATE:
                frames_looped = 0
                self.__time += 1
            start = time.time()
            reposition_cursor()
            self._count += 1
            self._detect_brick_ball_collision()
            for ball in self.__balls:
                ball.update_ball()
            self._update_powerups()
            self._initialize_ball()
            self._detect_ball_paddle_collision()
            self._info_print()
            self._draw()

            last_time = time.perf_counter()
            self._handle_input()
            # print(time.time() - start)

            while time.perf_counter() - last_time < self._refresh_time:
                pass

    def get_grid(self):
        """getter"""
        return self.__grid

    def _detect_ball_paddle_collision(self):
        for ball in self.__balls:
            if self.__paddle.get_x - 1 <= ball.get_x <= self.__paddle.get_x + self.__paddle.get_shape[0] * 2 \
                    and ball.get_y == self.__paddle.get_y - 1:
                ball.set_velocity([ball.get_velocity[0], -ball.get_velocity[1]])
                if ball.get_velocity[1] != 0:
                    center = round(self.__paddle.get_x + self.__paddle.get_shape[0])
                    distance = ball.get_x - center
                    ball.set_velocity([ball.get_velocity[0] + round(
                        distance / self.__paddle.get_shape[0] * 2), ball.get_velocity[1]])
                if self.__paddle.get_sticky:
                    if ball.get_velocity != [0, 0]:
                        ball.set_temp_velocity(self.__ball.get_velocity)
                    ball.set_velocity([0, 0])

    def _detect_brick_ball_collision(self):
        for ball in self.__balls:
            iterations = 10
            brick_hit = None
            step = 0
            index = -1
            got = False
            for i in range(1, iterations + 1):
                if ball.get_velocity[0] == 1:
                    x_f = ball.get_x + 1.5 * i * ball.get_velocity[0] / iterations + 0.5  # (1 1)
                else:
                    x_f = ball.get_x + i * ball.get_velocity[0] / iterations + 0.5  # (1 1)
                y_f = ball.get_y - i * ball.get_velocity[1] / iterations
                for j, brick in enumerate(self.__bricks):
                    if brick.get_x <= x_f < brick.get_x + brick.get_shape[0] * 2 and brick.get_y <= y_f <= brick.get_y + \
                            brick.get_shape[1] - 1:
                        brick_hit = brick
                        step = i
                        index = j
                        got = True
                        break
                if got:
                    break

            if not got:
                continue
            x_previous = ball.get_x + (step - 1) * ball.get_velocity[0] / iterations + 0.5
            y_previous = ball.get_y - (step - 1) * ball.get_velocity[1] / iterations

            if not self.__ball.get_through_ball:
                if brick_hit.get_x - 1 <= x_previous <= brick_hit.get_x + brick_hit.get_shape[0] * 2 + 1 \
                        and (y_previous < brick_hit.get_y or y_previous >= brick_hit.get_y + brick_hit.get_shape[1] - 1):
                    ball.set_x(floor(x_previous))
                    if y_previous < brick_hit.get_y:
                        ball.set_y(brick_hit.get_y - 1)
                    else:
                        ball.set_y(brick_hit.get_y + brick_hit.get_shape[1])
                    ball.set_velocity([ball.get_velocity[0], -1*ball.get_velocity[1]])

                elif brick_hit.get_x >= x_previous or x_previous >= brick_hit.get_x + brick_hit.get_shape[0] * 2 \
                        and (brick_hit.get_y <= y_previous < brick_hit.get_y + brick_hit.get_shape[1]):
                    # print("hello")
                    if brick_hit.get_x >= x_previous:
                        ball.set_x(brick_hit.get_x - 2)
                    else:
                        ball.set_x(brick_hit.get_x + brick_hit.get_shape[0] * 2 - 1)
                    ball.set_y(int(y_previous))
                    ball.set_velocity([-1*ball.get_velocity[0], ball.get_velocity[1]])

                else:
                    ball.set_velocity([-1*ball.get_velocity[0], -1*ball.get_velocity[1]])
                    ball.set_y(round(y_previous))
                    ball.set_x(round(x_previous))

            if brick_hit.get_variety == 1 or self.__ball.get_through_ball:
                del self.__bricks[index]
                self.__score += 100
                probability_of_powerup = random.random()
                if probability_of_powerup >= 0.85:
                    variety = random.randint(1, 6)
                    switcher = {
                        1: ExpandPaddle(),
                        2: ShrinkPaddle(),
                        3: SpeedUpBall(),
                        4: StickyPaddle(),
                        5: ThroughBall(),
                        6: BallMultiplier()
                    }
                    powerup = switcher[variety]
                    powerup.set_x(brick_hit.get_x + 2)
                    powerup.set_y(brick_hit.get_y)
                    self.__powerup_shown.append(powerup)
            else:
                if brick_hit.get_variety != 4:
                    brick_hit.set_variety(brick_hit.get_variety - 1)

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
