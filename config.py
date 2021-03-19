"""
Common constants related to the screen and game
"""

from colorama import Back
import subprocess as sp

FRAME_RATE = 20
FRAME_HEIGHT, FRAME_WIDTH = sp.check_output(['stty', 'size']).split()
FRAME_WIDTH = int(str(FRAME_WIDTH)[2:-1])
FRAME_HEIGHT = int(str(FRAME_HEIGHT)[2:-1]) - 5
BACK_COLOR = Back.BLACK
BOMB_BACKGROUND = Back.LIGHTMAGENTA_EX
LIVES = 7
POWER_UP_ACTIVE_TIME = 300  # 300/20(FRAME_RATE) = 15 seconds
PADDLE_SPEED = 2
POWER_UP_DROP_PROBABILITY = 0.2
BRICK_CONSTANT_TIME = 90
RAINBOW_PROBABILITY = 0.08
DEBUG = False
