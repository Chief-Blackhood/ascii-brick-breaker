"""
Common constants related to the screen and game
"""

from colorama import Back
import subprocess as sp
FRAME_RATE = 20
# FRAME_WIDTH = 173
# FRAME_HEIGHT = 43
print(sp.check_output(['stty', 'size']).split())
FRAME_HEIGHT, FRAME_WIDTH = sp.check_output(['stty', 'size']).split()
FRAME_WIDTH = int(str(FRAME_WIDTH)[2:-1])
FRAME_HEIGHT = int(str(FRAME_HEIGHT)[2:-1]) - 2
BACK_COLOR = Back.BLACK
DEBUG=True
