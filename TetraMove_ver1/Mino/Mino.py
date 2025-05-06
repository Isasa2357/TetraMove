
import random
import copy

from Field.config import block_state, writable_block_state

import numpy as np

from abc import abstractmethod

class MinoCalculator:
    def __init__(self):
        pass

    @abstractmethod
    def grid(self, direction: int) -> list:
        pass
    
    def calc_pos_aft_lr(self, position: list, direction: int, field: np.array) -> list:
        '''
            left rotate後のミノグリッドの位置を計算する

            Args:
                position: ミノグリッドの左上の位置．[y, x]
                direction: 現在のミノの向き
                field: テトリスフィールド全体
            
            Ret:
                next_position, next_direction, is_rotated
                next_position: 回転後のグリッドの位置
                next_direction: 回転後のミノの向き
                is_rotated: 回転が行われたか
        '''
        next_direction = self.get_next_direction(0, copy.copy(direction))
        next_minoGrid = self.grid(next_direction)

        y, x = position
        dydx_cand = [
            [0, 0], 
            [0, 1], 
            [0, -1], 
            [1, 0], 
            [-1, 0], 
        ]

        for dy, dx in dydx_cand:
            pos_cand = [y + dy, x + dx]
            if self.can_place(next_minoGrid, pos_cand, field):
                return pos_cand, next_direction, True
        return position, direction, False
    
    def calc_pos_aft_rr(self, position: list, direction: int, field: np.array) -> list:
        '''
            right rotate後のミノグリッドの位置を計算する

            Args:
                position: ミノグリッドの左上の位置．[y, x]
                direction: ミノの向き
                field: テトリスフィールド全体
            
            Ret:
                next_position, next_direction, is_rotated
                next_position: 回転後のグリッドの位置
                next_direction: 回転後のミノの向き
                is_rotated: 回転が行われたか
        '''
        next_direction = self.get_next_direction(1, copy.copy(direction))
        next_minoGrid = self.grid(next_direction)

        y, x = position
        dydx_cand = [
            [0, 0], 
            [0, 1], 
            [0, -1], 
            [1, 0], 
            [-1, 0]
        ]

        for dy, dx in dydx_cand:
            pos_cand = [y + dy, x + dx]
            if self.can_place(next_minoGrid, pos_cand, field):
                return pos_cand, next_direction, True
        return position, direction, False
    
    def calc_pos_aft_lm(self, position: list, direction: int, field: np.array) -> list:
        '''
            left move後のミノグリッドの位置を計算する

            Args:
                position: ミノグリッドの左上の位置．[y, x]
                direction: ミノの向き
                field: テトリスフィールド全体
            
            Ret:
                next_position, next_direction, is_rotated
                next_position: 回転後のグリッドの位置
                next_direction: 回転後のミノの向き
                is_moved: 移動が行われたか
        '''
        minoGrid = self.grid(direction)

        y, x = position

        dydx_cand = [
            [0, -1], 
            [0, 0]
        ]

        for dy, dx in dydx_cand:
            pos_cand = [y + dy, x + dx]

            if self.can_place(minoGrid, pos_cand, field):
                return pos_cand, direction, not (dy == 0 and dx == 0)
        return position, direction, False

    def calc_pos_aft_rm(self, position: list, direction: int, field: np.array) -> list:
        '''
            right move後のミノグリッドの位置を計算する

            Args:
                position: ミノグリッドの左上の位置．[y, x]
                direction: ミノの向き
                field: テトリスフィールド全体
            
            Ret:
                ext_position, next_direction, is_rotated
                next_position: 回転後のグリッドの位置
                next_direction: 回転後のミノの向き
                is_moved: 移動が行われたか
        '''
        minoGrid = self.grid(direction)

        y, x = position
        

        dydx_cand = [
            [0, 1], 
            [0, 0]
        ]

        for dy, dx in dydx_cand:
            pos_cand = [y + dy, x + dx]

            if self.can_place(minoGrid, pos_cand, field):
                return pos_cand, direction, not (dy == 0 and dx == 0)
        return position, direction, False
    
    def calc_pos_aft_dm(self, position: list, direction: int, field: np.array) -> list:
        '''
            dowm move後のミノグリッドの位置を計算する

            Args:
                position: ミノグリッドの左上の位置．[y, x]
                direction: ミノの向き
                field: テトリスフィールド全体
            
            Ret:
                ext_position, next_direction, is_rotated
                next_position: 回転後のグリッドの位置
                next_direction: 回転後のミノの向き
                is_moved: 移動が行われたか
        '''
        minoGrid = self.grid(direction)
        y, x = position

        dydx_cand = [
            [1, 0], 
            [0, 0]
        ]

        for dy, dx in dydx_cand:
            pos_cand = [y + dy, x + dx]

            if self.can_place(minoGrid, pos_cand, field):
                return pos_cand, direction, not(dy == 0 and dx == 0)
        return position, direction, False

    def get_next_direction(self, act: int, direction: int):
        '''
            回転後のdirectionを計算
            左回転 → act = 0
            右回転 → act = 1
        '''
        if act == 'left':
            act = 0
        elif act == 'right':
            act = 1

        if act == 0:
            direction -= 1
        elif act == 1:
            direction += 1
        direction %= 4
        return direction
    
    def can_place(self, minoGrid: np.array, position: list, field: np.array):
        '''
            positionにあるminoGridがフィールドに配置可能か判定
        '''

        y, x = position

        # 範囲外判定
        if not (0 <= y <= len(field) - 1):
            return False
        if not (0 <= y + len(minoGrid) - 1 <= len(field) - 1):
            return False
        if not (0 <= x <= len(field[0]) - 1):
            return False
        if not (0 <= x + len(minoGrid) - 1 <= len(field[0]) - 1):
            return False
            

        # フィールドからミノグリッドに対応する位置のグリッドを抜き出す
        fieldGrid = field[y:y + len(minoGrid), x:x+len(minoGrid[0])]

        # 判定
        for mline, fline in zip(minoGrid, fieldGrid):
            for mblock, fblock in zip(mline, fline):
                if not self.can_place_oneBlock(mblock, fblock):
                    return False
                
        # judge_can_place_eachBlock = np.vectorize(self.can_place_oneBlock)
        # cans = judge_can_place_eachBlock(minoGrid, fieldGrid)
        # can = np.all(cans)

        return True

    def can_place_oneBlock(self, minoblock: int, fieldblock: int):
        return not ((minoblock not in writable_block_state) and (fieldblock not in writable_block_state))
    
    @abstractmethod
    def calc_center(self, position: list, direction: int):
        pass


    @abstractmethod
    def ID(self) -> str:
        pass

class IminoCalculator(MinoCalculator):
    '''
        Mino shape(c is center)
            direction 0
                0000
                1111
                0000
                0000
            
            directino 1
                0010
                0010
                0010
                0010
            
            direction 2
                0000
                0000
                1111
                0000
                

            direction 3
                0100
                0100
                0100
                0100
    '''
    def __init__(self):
        super().__init__()
    
    @abstractmethod
    def grid(self, direction: int) -> dict:
        if direction == 0:
            return [
                [0, 0, 0, 0], 
                [1, 1, 1, 1], 
                [0, 0, 0, 0], 
                [0, 0, 0, 0], 
            ]
        elif direction == 1:
            return [
                [0, 0, 1, 0],
                [0, 0, 1, 0],
                [0, 0, 1, 0],
                [0, 0, 1, 0],
            ]
        elif direction == 2:
            return [
                [0, 0, 0, 0], 
                [0, 0, 0, 0], 
                [1, 1, 1, 1], 
                [0, 0, 0, 0], 
            ]
        elif direction == 3:
            return [
                [0, 1, 0, 0], 
                [0, 1, 0, 0], 
                [0, 1, 0, 0], 
                [0, 1, 0, 0], 
            ]
    
    def calc_pos_aft_lr(self, position: list, mino_direction: int, field: np.array) -> list:
        return self.calc_pos_aft_lrr(position, mino_direction, field, 1)

    def calc_pos_aft_rr(self, position: list, mino_direction: int, field: np.array) -> list:
        return self.calc_pos_aft_lrr(position, mino_direction, field, 0)
    
    def calc_pos_aft_lrr(self, position: list, mino_direction: int, field: np.array, rotate_direction: int):
        next_direction = self.get_next_direction(rotate_direction, copy.copy(mino_direction))
        next_minoGrid = self.grid(next_direction)

        y, x = position
        dydx_cand = [
            [0, 0], 
            [0, 1], 
            [0, -1], 
            [0, 2], 
            [0, -2], 
            [-1, 0], 
            [1, 0], 
            [-2, 0], 
            [2, 0]
        ]

        for dy, dx in dydx_cand:
            if self.can_place(next_minoGrid, [y + dy, x + dx], field):
                return [y + dy, x + dx], next_direction, True
        return position, mino_direction, False
    
    def calc_center(self, position: list, direction: int):
        y, x = position
        if direction == 0:
            return [y + 1, x + 1]
        elif direction == 1:
            return [y + 1, x + 2]
        elif direction == 2:
            return [y + 2, x + 1]
        elif direction == 3:
            return [y + 1, x + 1]

    def ID(self) -> str:
        return 'Imino'

class OminoCalculator(MinoCalculator):
    '''
        Mino shape(c is center)
            direction is 0, 1, 2, 3
                11
                11
    '''
    def __init__(self):
        super().__init__()
    
    def grid(self, direction: int) -> list:
        return [
            [1, 1], 
            [1, 1], 
        ]
    
    def calc_center(self, position: list, direction: int):
        return position
    
    def ID(self) -> str:
        return 'Omino'

class SminoCalculator(MinoCalculator):
    '''
        Mino shape(c is center)
            direction is 0 or 2
                000
                011
                110

            direction is 1 or 3
                100
                110
                010
    '''
    def __init__(self):
        super().__init__()
    
    def grid(self, direction: int) -> list:
        if direction in [0, 2]:
            return [
                [0, 0, 0], 
                [0, 1, 1], 
                [1, 1, 0]
            ]
        elif direction in [1, 3]:
            return [
                [1, 0, 0], 
                [1, 1, 0], 
                [0, 1, 0]
            ]
        
    def calc_center(self, position: list, direction: int):
        y, x = position
        return [y + 1, x + 1]
    
    def ID(self) -> str:
        return 'Smino'

class ZminoCalculator(MinoCalculator):
    '''
        Mino shape(c is center)
            direction is 0 or 2
                000
                110
                011
            
            direction is 1 or 3
                010
                110
                100
    '''
    def __init__(self):
        super().__init__()
    
    def grid(self, direction: int) -> list:
        if direction in [0, 2]:
            return [
                [0, 0, 0], 
                [1, 1, 0], 
                [0, 1, 1]
            ]
        elif direction in [1, 3]:
            return [
                [0, 1, 0], 
                [1, 1, 0], 
                [1, 0, 0]
            ]
        
    def calc_center(self, position: list, direction: int):
        y, x = position
        return [y + 1, x + 1]

    def ID(self):
        return 'Zmino'

class JminoCalculator(MinoCalculator):
    '''
        Mino shape(c is center)
            direction is 0
                010
                010
                110

            direction is 1
                100
                111
                000
            
            direction is 2
                011
                010
                010
            
            direction is 3
                000
                111
                001
    '''
    def __init__(self):
        super().__init__()
    
    def grid(self, direction: int) -> list:
        if direction == 0:
            return [
                [0, 1, 0], 
                [0, 1, 0], 
                [1, 1, 0]
            ]
        elif direction == 1:
            return [
                [1, 0, 0], 
                [1, 1, 1], 
                [0, 0, 0]
            ]
        elif direction == 2:
            return [
                [0, 1, 1], 
                [0, 1, 0], 
                [0, 1, 0]
            ]
        elif direction == 3:
            return [
                [0, 0, 0], 
                [1, 1, 1], 
                [0, 0, 1]
            ]
        
    def calc_center(self, position: list, direction: int):
        y, x = position
        return [y + 1, x + 1]

    def ID(self):
        return 'Jmino'


class LminoCalculator(MinoCalculator):
    '''
        Mino shape(c is center)
            direction is 0
                010
                010
                011
            
            direction is 1
                000
                111
                100
            
            direction is 2
                110
                010
                010
            
            direction is 3
                001
                111
                000
    '''
    def __init__(self):
        super().__init__()
    
    def grid(self, direction: int) -> list:
        if direction == 0:
            return [
                [0, 1, 0], 
                [0, 1, 0], 
                [0, 1, 1]
            ]
        elif direction == 1:
            return [
                [0, 0, 0], 
                [1, 1, 1], 
                [1, 0, 0]
            ]
        elif direction == 2:
            return [
                [1, 1, 0], 
                [0, 1, 0], 
                [0, 1, 0]
            ]
        elif direction == 3:
            return [
                [0, 0, 1], 
                [1, 1, 1], 
                [0, 0, 0]
            ]
        
    def calc_center(self, position: list, direction: int):
        y, x = position
        return [y + 1, x + 1]

    def ID(self):
        return 'Lmino'

class TminoCalculator(MinoCalculator):
    '''
        Mino shape(c is center)
            direction is 0
                000
                111
                010
            
            direction is 1
                010
                110
                010
            
            direction is 2
                010
                111
                000
            
            direction is 3
                010
                011
                010
    '''
    def __init__(self):
        super().__init__()
    
    def grid(self, direction: int) -> list:
        if direction == 0:
            return [
                [0, 0, 0], 
                [1, 1, 1], 
                [0, 1, 0]
            ]
        elif direction == 1:
            return [
                [0, 1, 0], 
                [1, 1, 0], 
                [0, 1, 0]
            ]
        elif direction == 2:
            return [
                [0, 1, 0], 
                [1, 1, 1], 
                [0, 0, 0]
            ]
        elif direction == 3:
            return [
                [0, 1, 0], 
                [0, 1, 1], 
                [0, 1, 0]
            ]
    
    def calc_center(self, position: list, direction: int):
        y, x = position
        return [y + 1, x + 1]

    def ID(self):
        return 'Tmino'

def int_to_MinoCalculator(id: int):
    if id == 0:
        return IminoCalculator()
    elif id == 1:
        return OminoCalculator()
    elif id == 2:
        return SminoCalculator()
    elif id == 3:
        return ZminoCalculator()
    elif id == 4:
        return JminoCalculator()
    elif id == 5:
        return LminoCalculator()
    elif id == 6:
        return TminoCalculator()
    else:
        return None

class Holdmino:
    '''
        操作中のミノ
    '''

    def __init__(self, field: np.array, position: list=None,  minoType: MinoCalculator=None, direction: int = 0):
        self.__direction = direction

        self.__minoCalculator = None
        if minoType == None:
            self.__minoCalculator = gen_minoCalculator()
        else:
            self.__minoCalculator = gen_minoCalculator(minoType)
        
        self.__position = position
        if position == None:
            h, w = field.shape
            self.__position = get_mino_initPos(self.__minoCalculator.ID(), h, w)

    ### ミノの操作 ###

    def left_rotate(self, field: np.array):
        self.__position, self.__direction, is_rotated = self.__minoCalculator.calc_pos_aft_lr(self.__position, self.__direction, field)
        return is_rotated
    
    def right_rotate(self, field: np.array):
        self.__position, self.__direction, is_rotated = self.__minoCalculator.calc_pos_aft_rr(self.__position, self.__direction, field)
        return is_rotated
    
    def left_move(self, field: np.array):
        self.__position, self.__direction, is_moved = self.__minoCalculator.calc_pos_aft_lm(self.__position, self.__direction, field)
        return is_moved

    def right_move(self, field: np.array):
        self.__position, self.__direction, is_moved = self.__minoCalculator.calc_pos_aft_rm(self.__position, self.__direction, field)
        return is_moved

    def down_move(self, field:np.array):
        self.__position, self.__direction, is_moved = self.__minoCalculator.calc_pos_aft_dm(self.__position, self.__direction, field)
        return is_moved

    ### getter ###
    def get_direction(self):
        return copy.copy(self.__direction)
        
    def get_minoGrid(self):
        return copy.deepcopy(self.__minoCalculator.grid(self.__direction))

    def get_position(self):
        return copy.copy(self.__position)
    
    def get_holdID(self):
        return 'hold-' + self.__minoCalculator.ID()
    
    def get_minoID(self):
        return self.__minoCalculator.ID()
    
    def get_minoCenter(self):
        return self.__minoCalculator.calc_center(self.__position, self.__direction)



def gen_minoCalculator(mino :str = None) -> MinoCalculator:
    # ランダムにMinoを生成
    if mino == None:
        return int_to_MinoCalculator(random.randint(0, 6))

    # ミノを指定して生成
    if mino == 'Imino':
        return IminoCalculator()
    elif mino == 'Omino':
        return OminoCalculator()
    elif mino == 'Smino':
        return SminoCalculator()
    elif mino == 'Zmino':
        return ZminoCalculator()
    elif mino == 'Jmino':
        return JminoCalculator()
    elif mino == 'Lmino':
        return LminoCalculator()
    elif mino == 'Tmino':
        return TminoCalculator()

def get_mino_initPos(minoID, h, w):
        if minoID in ['Imino', 'hold-Imino']:
            return [2, int(w / 2) - 1]
        elif minoID in ['Omino', 'hold-Omino']:
            return [2, int(w / 2) - 1]
        elif minoID in ['Smino', 'hold-Smino']:
            return [1, int(w / 2) - 1]
        elif minoID in ['Zmino', 'hold-Zmino']:
            return [1, int(w / 2) - 1]
        elif minoID in ['Jmino', 'hold-Jmino']:
            return [1, int(w / 2) - 1]
        elif minoID in ['Lmino', 'hold-Lmino']:
            return [1, int(w / 2) - 1]
        elif minoID in ['Tmino', 'hold-Tmino']:
            return [1, int(w / 2) - 1]