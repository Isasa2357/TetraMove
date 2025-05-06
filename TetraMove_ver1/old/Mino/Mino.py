
import random
import copy

from abc import abstractmethod



class Mino:
    def __init__(self):
        pass

    @abstractmethod
    def position(self, center: list, direction: int) -> dict:
        pass

    def posCand_rr(self, center: list, direction: int) -> list[dict]:
        '''
            center位置と向きから，次の座標の候補のリストを列挙
        '''
        clone_center = copy.copy(center)
        clone_direction = copy.copy(direction)

        return self.position(center)
    
    def posCand_lr(self, center: list, direction: int) -> dict:
        self.change_direction(1)
        return self.position(center)
    
    def posCand_rm(self, center: list, dirction: int) -> dict:
        '''
            return:
                right move後の Mino の c の位置の候補
        '''
        candidates = []

        # cand1: 操作通り
        candidates.append([center[0], center[1] + 1])

        # cand2: 動けない
        candidates.append(center)

        return candidates
    
    def posCand_lm(self, center: list) -> dict:
        '''
            return:
                left move後の Mino の c の位置の候補
        '''
        candidates = []

        # cand1: 操作通り
        candidates.append([center[0], center[1] - 1])

        # cand2: 動けない
        candidates.append(center)

        return candidates
    
    def posCand_dm(self, center: list) -> dict:
        '''
            return:
                down move後の Mino の c の位置の候補
        '''
        candidates = []

        # cand1: 操作通り
        candidates.append([center[0] - 1, center[1]])

        # cand2: 動けない
        candidates.append(center)
        
        return candidates

    @abstractmethod
    def ID(self) -> str:
        pass

    def next_direction(self, cnt_direction, rotate_type: int) -> None:
        '''
            rotate_type:
                0: 右回転
                1: 左回転
        '''
        next_direction = copy.copy(cnt_direction)

        if rotate_type == 0:
            next_direction += 1
        elif rotate_type == 1:
            next_direction -= 1
        
        next_direction %= 4

        return next_direction

class Imino(Mino):
    '''
        Mino shape(c is center)
            direction 0
                oooo
                abcd
                oooo
                oooo
            
            directino 1
                ooao
                oobo
                ooco
                oodo
            
            direction 2
                oooo
                oooo
                dcba
                oooo

            direction 3
                odoo
                ocoo
                oboo
                oaoo
    '''
    def __init__(self):
        super().__init__()
    
    def position(self, center: list, direction: int) -> dict:
        c_y, c_x = center
        pos = None
        if direction == 1:
            pos = {
                'a': [center[0], center[1] - 2], 
                'b': [center[0], center[1] - 1], 
                'c': center, 
                'd': [center[0], center[1] + 1]
            }
        elif direction == 2:
            pos = {
                'a': [center[0] - 2, center[1]], 
                'b': [center[0] - 1, center[1]], 
                'c': center, 
                'd': [center[0] + 1, center[1]]
            }
        elif direction == 3:
            pos = {
                'a': [center[0], center[1] + 2], 
                'b': [center[0], center[1] + 1], 
                'c': center, 
                'd': [center[0], center[1] - 1]
            }
        elif direction == 4:
            pos = {
                'a': [center[0] + 2, center[1]], 
                'b': [center[0] + 1, center[1]], 
                'c': center, 
                'd': [center[0] - 1, center[1]]
            }

        return pos
    
    def ID(self) -> str:
        return 'Imino'

class Omino(Mino):
    '''
        Mino shape(c is center)
            direction is 0, 1, 2, 3
                ab
                cd
    '''
    def __init__(self):
        super().__init__()
    
    def position(self, center: list, direction: int) -> dict:
        c_y, c_x = center
        pos = {
            'a': [c_y - 1, c_x], 
            'b': [c_y - 1, c_x + 1], 
            'c': [c_y, c_x], 
            'd': [c_y, c_x + 1]
        }
        return pos
    
    def ID(self) -> str:
        return 'Omino'

class Smino(Mino):
    '''
        Mino shape(c is center)
            direction is 0 or 2
                 ba
                dc

            direction is 1 or 3
                d
                cb
                 a
    '''
    def __init__(self):
        super().__init__()
    
    def position(self, center: list, direction: int) -> dict:
        c_y, c_x = center
        pos = None
        if direction in [0, 2]:
            pos = {
                'a': [c_y - 1, c_x + 1], 
                'b': [c_y - 1, c_x], 
                'c': [c_y, c_x], 
                'd': [c_y, c_x - 1]
            }
        elif direction in [1, 3]:
            pos = {
                'a': [c_y + 1, c_x + 1], 
                'b': [c_y, c_x + 1], 
                'c': [c_y, c_x], 
                'd': [c_y - 1, c_x]
            }
        return pos
    
    def ID(self) -> str:
        return 'Smino'

class Zmino(Mino):
    '''
        Mino shape(c is center)
            direction is 0 or 2
                ab
                 cd
            
            direction is 1 or 3
                 a
                cb
                d
    '''
    def __init__(self):
        super().__init__()
    
    def position(self, center: list, direction: int) -> dict:
        c_y, c_x = center
        pos = None
        if direction in [0, 2]:
            pos = {
                'a': [c_y - 1, c_x - 1], 
                'b': [c_y - 1, c_x], 
                'c': [c_y, c_x], 
                'd': [c_y, c_x + 1]
            }
        elif direction in [1, 3]: 
            pos = {
                'a': [c_y - 1, c_x + 1], 
                'b': [c_y, c_x + 1], 
                'c': [c_y, c_x], 
                'd': [c_y + 1, c_x]
            }
        return pos

    def ID(self):
        return 'Zmino'

class Jmino(Mino):
    '''
        Mino shape(c is center)
            direction is 0
                 d
                 c
                ab

            direction is 1
                a
                bcd
            
            direction is 2
                ba
                c
                d
            
            direction is 3
                dcb
                  a
    '''
    def __init__(self):
        super().__init__()
    
    def position(self, center: list, direction) -> dict:
        cy, cx = center
        pos = None
        if direction == 0:
            pos = {
                'a': [cy + 1, cx - 1], 
                'b': [cy + 1, cx], 
                'c': [cy, cx], 
                'd': [cy - 1, cx]
            }
        elif direction == 1:
            pos = {
                'a': [cy - 1, cx - 1], 
                'b': [cy, cx - 1], 
                'c': [cy, cx], 
                'd': [cy, cx + 1]
            }
        elif direction == 2:
            pos = {
                'a': [cy - 1, cx + 1], 
                'b': [cy - 1, cx], 
                'c': [cy, cx], 
                'd': [cy + 1, cx]
            }
        elif direction == 3:
            pos = {
                'a': [cy + 1, cx + 1], 
                'b': [cy, cx + 1], 
                'c': [cy, cx], 
                'd': [cy, cx - 1]
            }
        return pos

    def ID(self):
        return 'Jmino'


class Lmino(Mino):
    '''
        Mino shape(c is center)
            direction is 0
                d
                c
                ba
            
            direction is 1
                bcd
                a
            
            direction is 2
                ab
                 c
                 d
            
            direction is 3
                  a
                dcb
    '''
    def __init__(self):
        super().__init__()
    
    def position(self, center: list, direction) -> dict:
        cy, cx = center
        pos = None
        if direction == 0:
            pos = {
                'a': [cy + 1, cx + 1], 
                'b': [cy + 1, cx], 
                'c': [cy, cx], 
                'd': [cy - 1, cx]
            }
        elif direction == 1:
            pos = {
                'a': [cy + 1, cx - 1], 
                'b': [cy, cx - 1], 
                'c': [cy, cx], 
                'd': [cy, cx + 1]
            }
        elif direction == 2:
            pos = {
                'a': [cy - 1, cx - 1], 
                'b': [cy - 1, cx], 
                'c': [cy, cx], 
                'd': [cy + 1, cx]
            }
        elif direction == 3:
            pos = {
                'a': [cy - 1, cx + 1], 
                'b': [cy, cx + 1], 
                'c': [cy, cx], 
                'd': [cy, cx - 1]
            }
        return pos

    def ID(self):
        return 'Lmino'

class Tmino(Mino):
    '''
        Mino shape(c is center)
            direction is 0
                acb
                 d
            
            direction is 1
                 a
                dc
                 b
            
            direction is 2
                 d
                bca
            
            direction is 3
                b
                cd
                a
    '''
    def __init__(self):
        super().__init__()
    
    def position(self, center: list, direction: int) -> dict:
        cy, cx = center
        pos = None
        if direction == 0:
            pos = {
                'a': [cy, cx - 1], 
                'b': [cy, cx + 1], 
                'c': [cy, cx], 
                'd': [cy + 1, cx]
            }
        elif direction == 1:
            pos = {
                'a': [cy - 1, cx], 
                'b': [cy + 1, cx], 
                'c': [cy, cx], 
                'd': [cy, cx - 1]
            }
        elif direction == 2:
            pos = {
                'a': [cy, cx + 1], 
                'b': [cy, cx - 1], 
                'c': [cy, cx], 
                'd': [cy - 1, cx]
            }
        elif direction == 3:
            pos = {
                'a': [cy + 1, cx], 
                'b': [cy - 1, cx], 
                'c': [cy, cx], 
                'd': [cy, cx + 1]
            }
        return pos

    def ID(self):
        return 'Tmino'

class Holdmino:
    '''
        操作中のMino
    '''
    def __init__(self, center: list, mino: Mino = None):
        self.__center: list = center
        self.__holdMino: Mino = mino
    
    def position(self) -> dict:
        return self.__holdMino.position(self.__center)

    def rr(self) -> dict:
        return self.__holdMino.right_rotate(self.__center)
    
    def lr(self) -> dict:
        return self.__holdMino.left_rotate(self.__center)
    
    def rm(self) -> dict:
        return self.__holdMino.right_move(self.__center)

    def lm(self) -> dict:
        return self.__holdMino.left_move(self.__center)

    def dm(self) -> dict:
        return self.__holdMino.down_move(self.__center)
    
    def ID(self) -> str:
        return 'hold_' + self.__holdMino.ID()

    def direction(self) -> int:
        return self.__holdMino.direction()

def gen_mino(mino :str = None) -> Mino:
    # ランダムにMinoを生成
    if mino == None:
        pass

    # ミノを指定して生成
    if mino == 'I':
        return Imino()
    elif mino == 'O':
        return Omino()
    elif mino == 'S':
        return Smino()
    elif mino == 'Z':
        return Zmino()
    elif mino == 'J':
        return Jmino()
    elif mino == 'L':
        return Lmino()
    elif mino == 'T':
        return Tmino()