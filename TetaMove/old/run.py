
from Mino.Mino import *
from Field.TetrisField import *

from Field.TetrisField import *

import keyboard
import time

import numpy as np

import tkinter as tk

import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtCore import QRect

class MinoTestCanvas(QWidget):
    def __init__(self, field, width=15, height=15, cell_size=30, margin=20):
        super().__init__()
        self.field = field
        self.cell_size = cell_size
        self.margin = margin  # マージンの設定

        self.height = height
        self.width = width
        self.setWindowTitle("Mino Test Canvas")
        self.resize(width * cell_size + 2 * margin, height * cell_size + 2 * margin)  # マージンを加味してサイズ変更
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)

        for i in range(self.height):
            for j in range(self.width):
                color_name = 'white'
                if self.field[i][j] == 1:
                    color_name = 'blue'
                color = QColor(color_name)
                painter.setBrush(color)
                painter.setPen(QColor("gray"))

                # 描画位置をマージンを加えて調整
                x = j * self.cell_size + self.margin
                y = i * self.cell_size + self.margin
                painter.drawRect(QRect(x, y, self.cell_size, self.cell_size))

    def plot(self, field):
        """新しいグリッドを受け取ってキャンバスを更新"""
        self.field = field
        self.update()  # 再描画をトリガー

def check_mino(mino: Mino):
    app = QApplication(sys.argv)


    field = np.zeros((15, 15))
    mino = Holdmino([6, 6], mino)

    canvas = MinoTestCanvas(field)
    pos = mino.position()
    for p in pos.values():
        field[p[0]][p[1]] = 1
    canvas.plot(field)
    
    while True:
        key = input('>> ')
        if key == 'a':
            field = np.zeros((15, 15))
            pos = mino.left_rotate()
            for p in pos.values():
                field[p[0]][p[1]] = 1
            canvas.plot(field)
            time.sleep(0.2)  # 押しっぱなし対策

        elif key == 's':
            field = np.zeros((15, 15))
            pos = mino.right_rotate()
            for p in pos.values():
                field[p[0]][p[1]] = 1
            canvas.plot(field)
            time.sleep(0.2)

        elif key == 'l':
            field = np.zeros((15, 15))
            pos = mino.left_move()
            for p in pos.values():
                field[p[0]][p[1]] = 1
            canvas.plot(field)
            time.sleep(0.2)

        elif key == 'r':
            field = np.zeros((15, 15))
            pos = mino.right_move()
            for p in pos.values():
                field[p[0]][p[1]] = 1
            canvas.plot(field)
            time.sleep(0.2)

        elif key == 'exit':
            print("終了します")
            break

        print(mino.direction())
    sys.exit()

def move_cursor(to: list):
    y, x = to
    sys.stdout.write(f'\033[{y}A\033[{x}D')


def test_display_canvas():
    canvas_size = (15, 9)

    for i in range(canvas_size[0]):
        for j in range(canvas_size[1]):
            print('o', end='')
        if i != canvas_size[0] - 1:
            print()

    time.sleep(3)

    move_cursor([3, 3])

    print('3', end='')

    sys.stdout.write(f'\033[{3}B\033[{3}C\n')


    time.sleep(3)



def test_TetrisField():
    field = TetrisField(9, 15)

    field.place_newMino('T')
    field.show_field()

    np_field = field.field()

    for i in range(len(np_field)):
        for j in range(len(np_field[0])):
            print(f'{field.is_gameArea([i, j])} ', end='')
        print()
        


if __name__ == '__main__':
    test_display_canvas()