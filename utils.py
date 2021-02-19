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


def format_number(time):
    return f"{time if time > 9 else ('0'+f'{time}')}"


def format_time(time_in_sec):
    return f"{format_number(int((time_in_sec//3600)%24))}:{format_number(int((time_in_sec//60)%60))}:" \
           f"{format_number(int(time_in_sec%60))} "


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
