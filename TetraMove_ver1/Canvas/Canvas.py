import os

import numpy as np
from Field.TetrisField import *



block_colors = {
    0 : (255, 255, 255),
    1 : 1,
    2 : (0, 0, 0),
    10 : (0, 255, 255),
    11 : (255, 255, 0),
    12 : (0, 255, 0),
    13 : (255, 0, 0),
    14 : (0, 0, 255),
    15 : (255, 165, 0),
    16 : (128, 0, 128),
    20: (0, 255, 255),
    21: (255, 255, 0),
    22: (0, 255, 0),
    23: (255, 0, 0),
    24: (0, 0, 255),
    25: (255, 165, 0),
    26: (128, 0, 128)
}

def conv_rgb2ANSIcode(rgb: tuple):
    r, g, b = rgb

    return f'\033[38;2;{r};{g};{b}m'

class PromptCanvas:
    def __init__(self, size: list):
        h, w = size
    
    def write(self, field: np.array):
        for line in field:
            for block in line:
                color = conv_rgb2ANSIcode(block_colors[block])
                reset = '\033[0m'

                print(f'{color}■{reset}', end='')
            print()




def canvas_test():
    for i in range(15):
        for j in range(9):
            color = '\033[31m' if j % 2 == (i % 2) else '\033[32m'
            reset = '\033[0m'

            print(f'{color}█{reset}', end='')
        print()

if __name__ == '__main__':
    canvas_test()