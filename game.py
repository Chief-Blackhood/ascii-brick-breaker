import time
import os
import random
from math import floor

import numpy as np
from colorama import init as coloramaInit, Fore, Style

import config
from ball import Ball
from boss import Boss, Bomb
from brick import Brick
from bullet import Bullet
from config import FRAME_RATE
from kbhit import KBHit
from paddle import Paddle
from powerup import ShrinkPaddle, ExpandPaddle, SpeedUpBall, StickyPaddle, ThroughBall, BallMultiplier, ShootingPaddle
from utils import clear_terminal_screen, reposition_cursor, get_key_pressed, clear_buffer, format_time


def _collision_checker(piece, x_f, y_f):
    if (piece.get_x <= x_f + 1 < piece.get_x + piece.get_shape[0] * 2
        and piece.get_y <= y_f + 0.5 <= piece.get_y + piece.get_shape[1] - 1) \
            or (piece.get_x <= x_f + 1 < piece.get_x + piece.get_shape[0] * 2
                and piece.get_y <= y_f - 0.5 <= piece.get_y + piece.get_shape[1] - 1) \
            or (piece.get_x <= x_f - 1 < piece.get_x + piece.get_shape[0] * 2
                and piece.get_y <= y_f + 0.5 <= piece.get_y + piece.get_shape[1] - 1) \
            or (piece.get_x <= x_f - 1 < piece.get_x + piece.get_shape[0] * 2
                and piece.get_y <= y_f - 0.5 <= piece.get_y + piece.get_shape[1] - 1):
        return True
    return False


class Game:
    """Shape of the level"""
    brick_strings = [
        [
            "00000000000000000000",
            "00000000000000000000",
            "00000000000000000000",
            "00000211133111200000",
            "00000121133112100000",
            "00000111133111100000",
            "00000111111111100000",
            "00000113333331100000",
            "00000121111112100000",
            "00000211111111200000",
        ], [
            "00000333333333300000",
            "00000111133111100000",
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
        ], [
            "0000000000000000000",
            "0000000000000000000",
            "0000000000000000000",
            "0000000000000000000",
            "0000000000000000000",
            "0000000000000000000",
            "0000000000000000000",
            "0000000000000000000",
            "0020000000000000200",
        ]
    ]
    boss_string = [
        "0000000111110000000",
        "0000001000001000000",
        "0000010002000100000",
        "0000100022200010000",
        "0000100222220010000",
        "0000100000000010000",
        "0001111111111111000",
        "0010000000000000100",
        "0100000003000000010",
        "1000000030300000001",
        "0100000000000000010",
        "0011111111111111100",
        "0000100100010010000",
        "0000011000001100000",
        "0000044000004400000",
    ]
    _refresh_time = 1 / FRAME_RATE

    def _draw_in_range(self, info, obj):
        """Common function to draw any object in the given position and shape"""
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
        self.__bullets = []
        self.__power_up_shown = []
        self.__boss = []
        self.__bombs = []
        self.__unbreakable_bricks = 0
        self.__boss_health = 100
        self.__lives = config.LIVES + 1
        self.__score = 0
        self.__time = 0
        self.__level = 1
        self.__first_layer = False
        self.__second_layer = False
        self.__drop_bomb = True
        self.__time_attack = 0
        self.__active_power_up = [[False, 0] for _ in range(7)]
        self._initialize_bricks(self.brick_strings[self.__level - 1])
        self._loop()

    def _initialize_boss(self, boss_string):
        for row in range(len(boss_string)):
            for col in range(len(boss_string[0])):
                if boss_string[row][col] != '0':
                    boss = Boss()
                    if boss_string[row][col] == '2':
                        boss.set_variety(2)
                    elif boss_string[row][col] == '3':
                        boss.set_variety(3)
                    elif boss_string[row][col] == '4':
                        boss.set_variety(4)
                    else:
                        boss.set_variety(1)
                    boss.set_x(70 + 2 * boss.get_shape[0] * col)
                    boss.set_y(boss.get_shape[1] * row)
                    self.__boss.append(boss)

    def _initialize_bricks(self, brick_string):
        """To set the position and type of each brick at the start of the game"""
        for row in range(len(brick_string)):
            for col in range(len(brick_string[0])):
                if brick_string[row][col] != '0':
                    brick = Brick()
                    if brick_string[row][col] == '2':
                        brick.set_variety(4)
                        self.__unbreakable_bricks += 1
                    elif brick_string[row][col] == '3':
                        brick.set_variety(5)
                    else:
                        brick.set_variety(random.randint(1, 3))
                        chance = random.random()
                        if chance < config.RAINBOW_PROBABILITY:
                            brick.set_rainbow(True)
                    brick.set_x(5 + 2 * brick.get_shape[0] * col)
                    brick.set_y(2 + brick.get_shape[1] * row)
                    self.__bricks.append(brick)

    def _pull_bricks_down(self):
        for brick in self.__bricks:
            brick.set_y(brick.get_y + 1)

    def explode_each_brick(self, brick_hit):
        """
        To remove each brick surrounding an explosive brick or set a timer on it if it is an explosive brick itself
        """
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
                        self._drop_power_up(nearby, [random.randint(-1, 1), random.randint(0, 1)])
        self.__bricks = [x for x in self.__bricks if x not in to_remove]

    def _explode_bricks(self):
        """To loop on all explosive bricks"""
        for brick in self.__bricks:
            if brick.get_variety == 5 and brick.get_explode == self._count:
                self.explode_each_brick(brick)
                self.__bricks.remove(brick)

    def _deactivate_power_up(self, obj, i):
        """To deactivate power up and make the properties of the paddle and the ball normal"""
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
        """To reset the position of the ball after every death"""
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

    def _draw_boss(self):
        """To draw bricks on the screen"""
        for obj in self.__boss:
            self._draw_in_range(obj.draw(), obj.get_element)

    def _draw_bricks(self):
        """To draw bricks on the screen"""
        for obj in self.__bricks:
            if obj.get_rainbow:
                obj.set_variety(random.randint(1, 3))
            self._draw_in_range(obj.draw(), obj.get_element)

    def _draw_power_ups(self):
        """To draw power up and call the activate function if touched by the paddle"""
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
        """To update the position of the power up or deactivate the power up whose time is up"""
        for obj in self.__power_up_shown:
            obj.update_velocity_y()
            obj.update_power_up()
        for i, obj in enumerate(self.__active_power_up):
            if obj[0] and self._count - obj[1] > config.POWER_UP_ACTIVE_TIME:
                self._deactivate_power_up(obj, i)

    def _draw(self):
        """To draw all the objects on the screen"""
        self.__grid = np.array([[Fore.WHITE + config.BACK_COLOR + " "
                                 for _ in range(config.FRAME_WIDTH)]
                                for _ in range(config.FRAME_HEIGHT)])

        self._draw_in_range(self.__paddle.draw(), self.__paddle.get_element)
        if self.__active_power_up[6][0]:
            self.__grid[self.__paddle.get_y][self.__paddle.get_x + 1] = config.BACK_COLOR + "🌋"
            self.__grid[self.__paddle.get_y][
                self.__paddle.get_x - 1 + self.__paddle.get_shape[0] * 2] = config.BACK_COLOR + "🌋"
        self._draw_bricks()
        if self.__level == 3:
            self._draw_boss()
        for ball in self.__balls:
            self._draw_in_range(ball.draw(), ball.get_element)
        to_remove = []
        for bullet in self.__bullets:
            if bullet.get_y > 0:
                self._draw_in_range(bullet.draw(), bullet.get_element)
            else:
                to_remove.append(bullet)
        self.__bullets = [x for x in self.__bullets if x not in to_remove]
        to_remove = []
        for bomb in self.__bombs:
            if bomb.get_y < config.FRAME_HEIGHT - 3:
                self._draw_in_range(bomb.draw(), bomb.get_element)
            else:
                to_remove.append(bomb)
        self.__bombs = [x for x in self.__bombs if x not in to_remove]
        self._draw_power_ups()

        sra = str(Style.RESET_ALL)
        grid_str = "\n".join(
            [sra.join(row[:]) for row in self.get_grid()])

        # only a single print at the end makes rendering efficient
        os.write(1, str.encode(grid_str))

    def _terminate(self):
        """To terminate if key "q" is pressed"""
        self.__game_status = -1
        self._info_print()
        os.system('setterm -cursor on')
        print("Bye 👋")

    def _handle_input(self):
        """To handle input from the user"""
        inputted = ""

        if self.__keys.kbhit():
            inputted = self.__keys.getch()

        cin = get_key_pressed(inputted)
        if cin == -1:
            self._terminate()
        elif cin == 'a':
            for ball in self.__balls:
                self.__paddle.update_paddle(-config.PADDLE_SPEED, ball)
            if self.__level == 3:
                do_not_move = False
                for piece in self.__boss:
                    if piece.get_x - config.PADDLE_SPEED < 0 or self.__paddle.get_x >= 142:
                        do_not_move = True
                        break
                if not do_not_move:
                    for piece in self.__boss:
                        piece.set_x(piece.get_x - config.PADDLE_SPEED)
        elif cin == 'd':
            for ball in self.__balls:
                self.__paddle.update_paddle(config.PADDLE_SPEED, ball)

            if self.__level == 3:
                do_not_move = False
                for piece in self.__boss:
                    if piece.get_x + config.PADDLE_SPEED > config.FRAME_WIDTH - 2 or self.__paddle.get_x <= 8:
                        do_not_move = True
                        break
                if not do_not_move:
                    for piece in self.__boss:
                        piece.set_x(piece.get_x + config.PADDLE_SPEED)
        elif cin == ' ':
            for ball in self.__balls:
                ball.give_velocity(self.__paddle.get_sticky)
        elif cin == 'l':
            if self.__level < 3:
                self._update_level()
            else:
                self._game_over()
        elif cin == 'h':
            if self.__level == 3:
                self.__boss_health -= 10

        clear_buffer()
        return cin

    def _info_print(self):
        """Print the status of the game"""
        if self.__level != 1:
            print(config.FRAME_WIDTH * " ")
        print("⏱ Time: ", format_time(self.__time), (config.FRAME_WIDTH - 39) * " ", "💓 Lives: ", self.__lives,
              "      ")
        print("🌟 Score: ", self.__score, (config.FRAME_WIDTH - 32 - len(str(self.__score))) * " ", "🧱 Bricks:",
              len(self.__bricks) - self.__unbreakable_bricks, "    ")
        if self.__active_power_up[6][0]:
            print("💈 Time:",
                  (config.POWER_UP_ACTIVE_TIME - self._count + self.__active_power_up[6][1]) // config.FRAME_RATE,
                  (config.FRAME_WIDTH - 9 - len(str(self.__score))) * " ")
        if self.__level == 3:
            print("Boss Health:",
                  (self.__boss_health//10) * "🟥",
                  (config.FRAME_WIDTH - 33 - len(str(self.__score))) * " ")

    def _update_level(self):
        self.__level += 1
        self.__unbreakable_bricks = 0
        self.__time_attack = 0
        self.__bricks = []
        self.__balls = []
        self.__power_up_shown = []
        self.__bullets = []
        lives = self.__lives
        for i, power_up in enumerate(self.__active_power_up):
            self._deactivate_power_up(power_up, i)
        clear_terminal_screen()
        self._info_print()
        self.__paddle.set_x(round(config.FRAME_WIDTH / 2 - round(self.__paddle.get_shape[0] / 2)) - 2)
        self._initialize_bricks(self.brick_strings[self.__level - 1])
        new_ball = Ball()
        self.__balls.append(new_ball)
        self._initialize_ball()
        if self.__level == 3:
            self._initialize_boss(self.boss_string)
        self.__lives = lives
        self._draw()

    def _game_over(self):
        self.__game_status = -1
        os.system('setterm -cursor on')
        print("Game over 😕", " " * (config.FRAME_WIDTH - 14))
        self._info_print()

    def _game_status_check(self):
        """Check the condition of whether the player won or not"""
        if self.__lives <= 0:
            self._game_over()
        elif self.__unbreakable_bricks == len(self.__bricks):
            if self.__level < 3:
                self._update_level()
        elif self.__level == 3 and self.__boss_health <= 0:
            self.__game_status = -1
            os.system('setterm -cursor on')
            print("You won 🎉")
            self._info_print()

    def _loop(self):
        """The main loop where each function is called"""
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
                self.__time_attack += 1
                if self.__level == 3:
                    if self.__drop_bomb:
                        bomb = Bomb()
                        bomb.set_x(self.__paddle.get_x + self.__paddle.get_shape[0] - 1)
                        bomb.set_y(11)
                        self.__bombs.append(bomb)
                        self.__drop_bomb = False
                    else:
                        self.__drop_bomb = True
                if self.__active_power_up[6][0]:
                    bullet = Bullet()
                    bullet.set_x(self.__paddle.get_x)
                    bullet.set_y(self.__paddle.get_y)
                    self.__bullets.append(bullet)
                    bullet = Bullet()
                    bullet.set_x(self.__paddle.get_x + self.__paddle.get_shape[0] * 2 - 1)
                    bullet.set_y(self.__paddle.get_y)
                    self.__bullets.append(bullet)
            reposition_cursor()
            self._count += 1
            self._info_print()
            self._explode_bricks()
            self._detect_brick_ball_collision()
            self._detect_bullet_brick_collision()
            if self.__level == 3:
                self._detect_ufo_ball_collision()
                if self.__boss_health == 70 and not self.__first_layer:
                    for i in range(15):
                        brick = Brick()
                        brick.set_y(20)
                        brick.set_x(i * brick.get_shape[0] * 2 + 21)
                        brick.set_variety(1 if i % 2 == 0 else 2)
                        self.__bricks.append(brick)
                    self.__first_layer = True

                if self.__boss_health == 30 and not self.__second_layer:
                    for i in range(13):
                        brick = Brick()
                        brick.set_y(18)
                        brick.set_x(i * brick.get_shape[0] * 2 + 29)
                        brick.set_variety(1 if i % 2 == 0 else 2)
                        self.__bricks.append(brick)
                    self.__second_layer = True
            for ball in self.__balls:
                ball.update_ball()
            for bullet in self.__bullets:
                bullet.update_bullet()
            for bomb in self.__bombs:
                bomb.update_bomb()
            self._update_power_ups()
            self._initialize_ball()
            self._detect_ball_paddle_collision()
            self._detect_bomb_paddle_collision()
            self._brick_paddle_collision()
            self._draw()
            last_time = time.perf_counter()
            self._handle_input()
            self._game_status_check()
            while time.perf_counter() - last_time < self._refresh_time:
                pass

    def get_grid(self):
        """getter"""
        return self.__grid

    def _brick_paddle_collision(self):
        for brick in self.__bricks:
            if brick.get_y + brick.get_shape[1] >= self.__paddle.get_y:
                self._game_over()

    def _detect_bomb_paddle_collision(self):
        for bomb in self.__bombs:
            if self.__paddle.get_x - 1 <= bomb.get_x <= self.__paddle.get_x + self.__paddle.get_shape[0] * 2 \
                    and bomb.get_y == self.__paddle.get_y - 1:
                pass
                self.__lives -= 1

    def _detect_ball_paddle_collision(self):
        """To detect ball paddle collision"""
        for ball in self.__balls:
            if self.__paddle.get_x - 1 <= ball.get_x <= self.__paddle.get_x + self.__paddle.get_shape[0] * 2 \
                    and ball.get_y == self.__paddle.get_y - 1:
                ball.set_velocity([ball.get_velocity[0], -ball.get_velocity[1]])
                if ball.get_velocity[1] != 0:
                    if self.__time_attack > config.BRICK_CONSTANT_TIME:
                        self._pull_bricks_down()
                    center = round(self.__paddle.get_x + self.__paddle.get_shape[0])
                    distance = ball.get_x - center
                    ball.set_velocity([ball.get_velocity[0] + round(
                        distance / self.__paddle.get_shape[0] * 2), ball.get_velocity[1]])
                if self.__paddle.get_sticky:
                    if ball.get_velocity != [0, 0]:
                        ball.set_temp_velocity(ball.get_velocity)
                    ball.set_velocity([0, 0])

    def _drop_power_up(self, brick_hit, initial_velocity=[0, -0.5]):
        """To decide if a power up spawns at the place where the brick was broken"""
        self.__score += 100
        probability_of_power_up = random.random()
        if probability_of_power_up <= config.POWER_UP_DROP_PROBABILITY:
            variety = random.randint(1, 7)
            switcher = {
                1: ExpandPaddle(),
                2: ShrinkPaddle(),
                3: SpeedUpBall(),
                4: StickyPaddle(),
                5: ThroughBall(),
                6: BallMultiplier(),
                7: ShootingPaddle()
            }
            power_up = switcher[variety]
            power_up.set_x(brick_hit.get_x + 2)
            power_up.set_y(brick_hit.get_y)
            power_up.set_velocity(initial_velocity)
            self.__power_up_shown.append(power_up)

    def _detect_ufo_ball_collision(self):
        max_x = -1
        min_x = 300
        for piece in self.__boss:
            if max_x < piece.get_x:
                max_x = piece.get_x
            if min_x > piece.get_x:
                min_x = piece.get_x
        for ball in self.__balls:
            iterations = 20
            # piece_hit = None
            step = 0
            got = False
            for i in range(1, iterations + 1):
                x_f = ball.get_x + i * ball.get_velocity[0] / iterations + 0.5  # (1 1)
                y_f = ball.get_y - i * ball.get_velocity[1] / iterations
                if min_x <= x_f <= max_x and 0 <= y_f <= 14:
                    step = i
                    got = True
                    break
                if got:
                    break

            if not got:
                continue
            self.__boss_health -= 10
            x_previous = ball.get_x + (step - 1) * ball.get_velocity[0] / iterations + 0.5
            y_previous = ball.get_y - (step - 1) * ball.get_velocity[1] / iterations

            if y_previous >= 14:
                ball.set_y(14)
                ball.set_velocity([ball.get_velocity[0], -1 * ball.get_velocity[1]])
            else:
                if 2 * x_previous <= min_x + max_x:
                    ball.set_x(min_x - 8)
                    if ball.get_velocity[0] == 0:
                        ball.set_velocity([-2, ball.get_velocity[1]])
                    ball.set_velocity([-1 * abs(ball.get_velocity[0]), ball.get_velocity[1]])
                elif 2 * x_previous >= max_x + min_x:
                    ball.set_x(max_x + 8)
                    if ball.get_velocity[0] == 0:
                        ball.set_velocity([2, ball.get_velocity[1]])
                    ball.set_velocity([abs(ball.get_velocity[0]), ball.get_velocity[1]])

    def _detect_bullet_brick_collision(self):
        temp_bullets = []
        for bullet in self.__bullets:
            got = False
            index = -1
            brick_hit = None
            for j, brick in enumerate(self.__bricks):
                if (brick.get_x <= bullet.get_x + 1.5 < brick.get_x + brick.get_shape[0] * 2
                    and brick.get_y <= bullet.get_y - 0.5 <= brick.get_y + brick.get_shape[1] - 1) \
                        or (brick.get_x <= bullet.get_x - 0.5 < brick.get_x + brick.get_shape[0] * 2
                            and brick.get_y <= bullet.get_y - 0.5 <= brick.get_y + brick.get_shape[1] - 1):
                    brick_hit = brick
                    index = j
                    brick_hit.set_rainbow(False)
                    got = True
                    break
            if not got:
                temp_bullets.append(bullet)
                continue

            if brick_hit.get_variety == 5:
                self.explode_each_brick(brick_hit)
                self.__bricks.remove(brick_hit)
                self.__score += 100
            elif brick_hit.get_variety == 1:
                del self.__bricks[index]
                self._drop_power_up(brick_hit, [0, 1])
            elif brick_hit.get_variety != 4:
                brick_hit.set_variety(brick_hit.get_variety - 1)
        self.__bullets = temp_bullets

    def _detect_brick_ball_collision(self):
        """To detect collision between ball and bricks"""
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
                    if _collision_checker(brick, x_f, y_f):
                        brick_hit = brick
                        brick_hit.set_rainbow(False)
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

            initial_power_up_velocity = ball.get_velocity

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
                if self.__level != 3:
                    self._drop_power_up(brick_hit, initial_power_up_velocity)
                else:
                    self.__score += 100
            else:
                if brick_hit.get_variety != 4:
                    brick_hit.set_variety(brick_hit.get_variety - 1)
