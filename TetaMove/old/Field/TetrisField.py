import numpy as np
import copy

from Mino.Mino import *



class TetrisField:
    '''
        テトリスのブロック位置などを管理する
        フィールドはMinoがおける範囲に加え，上下左右に4マス分のオフセットが存在する
    '''

    field_type = {
        'empty': 0, 
        'external': 1,
        'Imino': 21,
        'Omino': 22,
        'Smino': 23,
        'Zmino': 24, 
        'Jmino': 25, 
        'Lmino': 26, 
        'Tmino': 27,
        'hold_Imino': 31,
        'hold_Omino': 32,
        'hold_Smino': 33, 
        'hold_Zmino': 34, 
        'hold_Jmino': 35, 
        'hold_Lmino': 36, 
        'hold_Tmino': 37,
    }

    def __init__(self, width, height):
        self.__width = width
        self.__height = height

        self.__field: np.array = np.zeros((height + 8, width + 8))
        self.init_field()

        self.__holdmino = None
    
    

    def init_field(self):
        self.__field = np.zeros((self.__height + 8, self.__width + 8))
        self.__field[0:4] = self.field_type['external']
        self.__field[-4:] = self.field_type['external']
        self.__field[:, 0:4] = self.field_type['external']
        self.__field[:, -4:] = self.field_type['external']
    


    ### Mino関連 ###

    def place_newMino(self, mino=None):
        newMino = gen_mino(mino)

        # SZJLT
        if newMino.ID() == 'Imino':
            center = [2, int(len(self.__field[0]) / 2)]
        elif newMino.ID() == 'Omino':
            center = [3, int(len(self.__field[0]) / 2)]
        elif newMino.ID() == 'Smino':
            center = [3, int(len(self.__field[0]) / 2)]
        elif newMino.ID() == 'Zmino':
            center = [3, int(len(self.__field[0]) / 2)]
        elif newMino.ID() == 'Jmino':
            center = [2, int(len(self.__field[0]) / 2)]            
        elif newMino.ID() == 'Lmino':
            center = [2, int(len(self.__field[0]) / 2)]            
        elif newMino.ID() == 'Tmino':
            center = [2, int(len(self.__field[0]) / 2)]
        
        self.__holdmino = Holdmino(center, newMino)
        pos = self.__holdmino.position()
        for coord in pos.values():
            self.__field[coord[0]][coord[1]] = self.coord_type[self.__holdmino.ID()]

    def move_holdMino(self, action: int):
        # holdMinoの現在地を取得，cntposをemptyかexternalに変更
        cntpos = self.__holdmino.position()
        
        # holdMinoを移動 & 描画


    ### judge ###

    def is_gameArea(self, coord: list) -> bool:
        y, x = coord
        return (4 <= x < 4 + self.__width) and (4 <= y < 4 + self.__height)

    def is_external(self, coord: list) -> bool:
        return not self.is_gameArea(coord)

    ### getter ###

    def width(self):
        return copy.copy(self.__width)
    
    def height(self):
        return copy.copy(self.__width)
    
    def field(self):
        return copy.copy(self.__field)
    
    ### shower ###

    def show_field(self):
        print('Tetris Field')
        print(self.__field)