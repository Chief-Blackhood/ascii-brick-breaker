import time
import os
import random
from math import floor

import numpy as np
from colorama import init as coloramaInit, Fore, Style

import config
from ball import Ball
from brick import Brick
from config import FRAME_RATE
from kbhit import KBHit
from paddle import Paddle
from powerup import ShrinkPaddle, ExpandPaddle, SpeedUpBall, StickyPaddle, ThroughBall, BallMultiplier
from utils import clear_terminal_screen, reposition_cursor, get_key_pressed, clear_buffer, format_time


class Game:
    brick_string = [
        "00000333333333000000",
        "00000111133111000000",
        "00000000033000000000",
        "02320211133111202320",
        "01310111133111101310",
        "02320111133111102320",
        "01310121111112101310",
        "01310113333331101310",
        "02320121100112102320",
        "01310211100111201310",
        "01310000000000001310",
        "01121112100121112110",
    ]
    _refresh_time = 1 / FRAME_RATE

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
        self.__power_up_shown = []
        self.__unbreakable_bricks = 0
        self.__lives = config.LIVES + 1
        self.__score = 0
        self.__time = 0
        self.__active_power_up = [[False, 0] for _ in range(6)]
        self._initialize_bricks()
        self._loop()

    def _initialize_bricks(self):
        for row in range(len(self.brick_string)):
            for col in range(len(self.brick_string[0])):
                if self.brick_string[row][col] != '0':
                    brick = Brick()
                    if self.brick_string[row][col] == '2':
                        brick.set_variety(4)
                        self.__unbreakable_bricks += 1
                    elif self.brick_string[row][col] == '3':
                        brick.set_variety(5)
                    else:
                        brick.set_variety(random.randint(1, 3))
                    brick.set_x(5 + 2 * brick.get_shape[0] * col)
                    brick.set_y(2 + brick.get_shape[1] * row)
                    self.__bricks.append(brick)

    def explode_each_brick(self, brick_hit):
        to_remove = []
        for nearby in self.__bricks:
            if brick_hit.get_x - brick_hit.get_shape[0] * 2 <= nearby.get_x <= brick_hit.get_x + \
                    brick_hit.get_shape[0] * 2:
                if brick_hit.get_y - brick_hit.get_shape[1] <= nearby.get_y <= brick_hit.get_y + \
                        brick_hit.get_shape[1]:

                    if nearby.get_variety == 5:
                        nearby.set_explode(self._count + 1)
                    else:
                        if nearby.get_variety == 4:
                            self.__unbreakable_bricks -= 1
                        to_remove.append(nearby)
                        self._drop_power_up(nearby)
        self.__bricks = [x for x in self.__bricks if x not in to_remove]

    def _explode_bricks(self):
        for brick in self.__bricks:
            if brick.get_variety == 5 and brick.get_explode == self._count:
                self.explode_each_brick(brick)
                self.__bricks.remove(brick)

    def _deactivate_power_up(self, obj, i):
        obj[0] = False
        if i == 0 and not self.__active_power_up[1][0]:
            self.__paddle.set_x(self.__paddle.get_x + 4)
            self.__paddle.set_shape([11, 2])
            self.__paddle.set_element(config.BACK_COLOR + "🧱")
        elif i == 1 and not self.__active_power_up[0][0]:
            if self.__paddle.get_x >= config.FRAME_WIDTH - self.__paddle.get_shape[0] * 2 - 3:
                self.__paddle.set_x(self.__paddle.get_x - 8)
            elif self.__paddle.get_x > 4:
                self.__paddle.set_x(self.__paddle.get_x - 4)
            self.__paddle.set_shape([11, 2])
            self.__paddle.set_element(config.BACK_COLOR + "🧱")
        elif i == 2:
            config.FRAME_RATE = 20
        elif i == 3:
            self.__paddle.set_sticky(False)
        elif i == 4:
            for ball in self.__balls:
                ball.set_through_ball(False)
                ball.set_element(config.BACK_COLOR + "🌎")

    def _initialize_ball(self):
        if len(self.__balls) == 1:
            ball = self.__balls[0]
            paddle = self.__paddle
            if ball.get_velocity == [0, 0] and ball.get_y >= config.FRAME_HEIGHT - 1:
                ball.set_x(paddle.get_x + random.randint(0, 2 * floor(paddle.get_shape[0]) - 1))
                ball.set_y(paddle.get_y - 1)
                self.__lives -= 1
                for i, obj in enumerate(self.__active_power_up):
                    self._deactivate_power_up(obj, i)
        else:
            for ball in self.__balls:
                if ball.get_velocity == [0, 0] and ball.get_y >= config.FRAME_HEIGHT - 1:
                    self.__balls.remove(ball)

    def _draw_bricks(self):
        for obj in self.__bricks:
            self._draw_in_range(obj.draw(), obj.get_element)

    def _draw_power_ups(self):
        for obj in self.__power_up_shown:
            if obj.get_y < config.FRAME_HEIGHT - 2:
                self._draw_in_range(obj.draw(), obj.get_element)
            else:
                if self.__paddle.get_x <= obj.get_x <= self.__paddle.get_x + self.__paddle.get_shape[0] * 2:
                    self.__active_power_up[obj.get_variety - 1][0] = True
                    self.__active_power_up[obj.get_variety - 1][1] = self._count
                    if obj.get_variety == 1 or obj.get_variety == 2 or obj.get_variety == 4:
                        obj.activate_power_up(self.__paddle)
                    elif obj.get_variety == 3 or obj.get_variety == 5:
                        for ball in self.__balls:
                            obj.activate_power_up(ball)
                    elif obj.get_variety == 6:
                        if len(self.__balls) < 4:
                            self.__balls = obj.activate_power_up(self.__balls)

                self.__power_up_shown.remove(obj)

    def _update_power_ups(self):
        for obj in self.__power_up_shown:
            obj.set_y(obj.get_y + 0.5)
        for i, obj in enumerate(self.__active_power_up):
            if obj[0] and self._count - obj[1] > config.POWER_UP_ACTIVE_TIME:
                self._deactivate_power_up(obj, i)

    def _draw(self):
        self.__grid = np.array([[Fore.WHITE + config.BACK_COLOR + " "
                                 for _ in range(config.FRAME_WIDTH)]
                                for _ in range(config.FRAME_HEIGHT)])

        self._draw_in_range(self.__paddle.draw(), self.__paddle.get_element)
        self._draw_bricks()
        for ball in self.__balls:
            self._draw_in_range(ball.draw(), ball.get_element)
        self._draw_power_ups()

        sra = str(Style.RESET_ALL)
        grid_str = "\n".join(
            [sra.join(row[:]) for row in self.get_grid()])

        # only a single print at the end makes rendering efficient
        os.write(1, str.encode(grid_str))

    def _terminate(self):
        self.__game_status = -1
        os.system('setterm -cursor on')
        print("Bye 👋")

    def _handle_input(self):
        inputted = ""

        if self.__keys.kbhit():
            inputted = self.__keys.getch()

        cin = get_key_pressed(inputted)
        if cin == -1:
            self._terminate()
        elif cin == 'a':
            for ball in self.__balls:
                self.__paddle.update_paddle(-config.PADDLE_SPEED, ball)
        elif cin == 'd':
            for ball in self.__balls:
                self.__paddle.update_paddle(config.PADDLE_SPEED, ball)
        elif cin == ' ':
            for ball in self.__balls:
                ball.give_velocity(self.__paddle.get_sticky)

        clear_buffer()
        return cin

    def _info_print(self):
        print("⏱ Time: ", format_time(self.__time), (config.FRAME_WIDTH - 39) * " ", "💓 Lives: ", self.__lives)
        print("🌟 Score: ", self.__score, (config.FRAME_WIDTH - 32 - len(str(self.__score))) * " ", "🧱 Bricks:",
              len(self.__bricks) - self.__unbreakable_bricks)

    def _game_status_check(self):
        if self.__lives <= 0:
            self.__game_status = -1
            os.system('setterm -cursor on')
            print("Game over 😕")
            self._info_print()
        elif self.__unbreakable_bricks == len(self.__bricks):
            self.__game_status = -1
            os.system('setterm -cursor on')
            print("You won 🎉")
            self._info_print()

    def _loop(self):
        self.__game_status = 1
        frames_looped = 0

        clear_terminal_screen()

        while self.__game_status == 1:
            if self._count % 200 == 0:
                clear_terminal_screen()
            frames_looped += 1
            if frames_looped >= config.FRAME_RATE:
                frames_looped = 0
                self.__time += 1
            reposition_cursor()
            self._count += 1
            self._info_print()
            self._detect_brick_ball_collision()
            self._explode_bricks()
            for ball in self.__balls:
                ball.update_ball()
            self._update_power_ups()
            self._initialize_ball()
            self._detect_ball_paddle_collision()
            self._draw()

            last_time = time.perf_counter()
            self._handle_input()
            self._game_status_check()
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
                        ball.set_temp_velocity(ball.get_velocity)
                    ball.set_velocity([0, 0])

    def _drop_power_up(self, brick_hit):
        self.__score += 100
        probability_of_power_up = random.random()
        if probability_of_power_up <= config.POWER_UP_DROP_PROBABILITY:
            variety = random.randint(1, 6)
            switcher = {
                1: ExpandPaddle(),
                2: ShrinkPaddle(),
                3: SpeedUpBall(),
                4: StickyPaddle(),
                5: ThroughBall(),
                6: BallMultiplier()
            }
            power_up = switcher[variety]
            power_up.set_x(brick_hit.get_x + 2)
            power_up.set_y(brick_hit.get_y)
            self.__power_up_shown.append(power_up)

    def _detect_brick_ball_collision(self):
        for ball in self.__balls:
            iterations = 20
            brick_hit = None
            step = 0
            index = -1
            got = False
            for i in range(1, iterations + 1):
                x_f = ball.get_x + i * ball.get_velocity[0] / iterations + 0.5  # (1 1)
                y_f = ball.get_y - i * ball.get_velocity[1] / iterations
                for j, brick in enumerate(self.__bricks):
                    if (brick.get_x <= x_f + 1 < brick.get_x + brick.get_shape[0] * 2
                        and brick.get_y <= y_f + 0.5 <= brick.get_y + brick.get_shape[1] - 1)\
                            or (brick.get_x <= x_f + 1 < brick.get_x + brick.get_shape[0] * 2
                                and brick.get_y <= y_f - 0.5 <= brick.get_y + brick.get_shape[1] - 1)\
                            or (brick.get_x <= x_f - 1 < brick.get_x + brick.get_shape[0] * 2
                                and brick.get_y <= y_f + 0.5 <= brick.get_y + brick.get_shape[1] - 1)\
                            or (brick.get_x <= x_f - 1 < brick.get_x + brick.get_shape[0] * 2
                                and brick.get_y <= y_f - 0.5 <= brick.get_y + brick.get_shape[1] - 1):
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

            if not ball.get_through_ball:
                if brick_hit.get_x - 1 <= x_previous <= brick_hit.get_x + brick_hit.get_shape[0] * 2 + 1 \
                        and (
                        y_previous < brick_hit.get_y or y_previous >= brick_hit.get_y + brick_hit.get_shape[1] - 1):
                    ball.set_x(floor(x_previous))
                    if y_previous < brick_hit.get_y:
                        ball.set_y(brick_hit.get_y - 1)
                    else:
                        ball.set_y(brick_hit.get_y + brick_hit.get_shape[1])
                    ball.set_velocity([ball.get_velocity[0], -1 * ball.get_velocity[1]])

                elif brick_hit.get_x >= x_previous or x_previous >= brick_hit.get_x + brick_hit.get_shape[0] * 2 \
                        and (brick_hit.get_y <= y_previous < brick_hit.get_y + brick_hit.get_shape[1]):
                    if brick_hit.get_x >= x_previous:
                        ball.set_x(brick_hit.get_x - 2)
                    else:
                        ball.set_x(brick_hit.get_x + brick_hit.get_shape[0] * 2 - 1)
                    ball.set_y(int(y_previous))
                    ball.set_velocity([-1 * ball.get_velocity[0], ball.get_velocity[1]])

                else:
                    ball.set_velocity([-1 * ball.get_velocity[0], -1 * ball.get_velocity[1]])
                    ball.set_y(round(y_previous))
                    ball.set_x(round(x_previous))

            if brick_hit.get_variety == 5:
                self.explode_each_brick(brick_hit)
                self.__bricks.remove(brick_hit)
                self.__score += 100
            elif brick_hit.get_variety == 1 or ball.get_through_ball:
                if brick_hit.get_variety == 4:
                    self.__unbreakable_bricks -= 1
                del self.__bricks[index]
                self._drop_power_up(brick_hit)
            else:
                if brick_hit.get_variety != 4:
                    brick_hit.set_variety(brick_hit.get_variety - 1)
