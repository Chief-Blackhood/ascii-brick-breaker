import os
from termios import tcflush, TCIFLUSH
import sys


def clear_terminal_screen():
    """
    Clears terminal screen
    """
    os.system('clear')


def reposition_cursor():
    """
    Reposition cursor to the top left of the screen
    """
    print("\033[0;0H")

def filler(el, height, width, return_matrix=False):
    res = []
    for _ in range(height):
        res2 = []
        for __ in range(width):
            res2.append(el)
        res.append(res2)
    # have to understand the if condition
    return res[0] if height == 1 and not return_matrix else res

def get_key_pressed(keyin):
    keyin = keyin.lower()

    if keyin not in ('q', 'a', 'd', ' '):
        return 0
    if keyin == 'q':
        return -1

    return keyin

def clear_buffer():
    """Clears the input buffer"""
    tcflush(sys.stdin, TCIFLUSH)
