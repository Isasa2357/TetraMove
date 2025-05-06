import time
import sys
from Mino.Mino import *
import numpy as np
from Field.config import block_state

action_table = {
    'None': 0, 
    'lr': 1, 
    'rr': 2, 
    'lm': 3, 
    'rm': 4, 
    'dm': 5
}

class TetrisField:
    def __init__(self, height:int, width:int, firstMinoID:str=None, side_margin: int=2, bottom_margin=2, position: list=None):
        self.__side_margin = side_margin
        self.__bottom_margin = bottom_margin
        self.__above_height = 4
        self.__field:np.array = np.zeros((height + self.__above_height + bottom_margin, width + 2 * side_margin), dtype=np.int32)
        self.__field[-2:] = block_state['external']
        self.__field[:, 0:2] = block_state['external']
        self.__field[:, -2:] = block_state['external']

        self.__holdMino:Holdmino = None
        self.place_nextMino(firstMinoID, position=position)

        self.__downCounter = 0
        self.__downCounter_threshold = 20

        # self.step()で使用する
        self.flag_landing = False
    
    def action(self, act: int):
        '''
            0: 何もしない
            1: left rotate
            2: right rotate
            3: left move
            4: right move
            5: down move
            6: abs move(TODO 未定義)
        '''
        if type(act) == type('str'):
            act = action_table[act]

        game_field = self.__field[:-1, 1:-1]
        if act == 0:
            pass
            ret = False
        elif act == 1:
            ret = self.__holdMino.left_rotate(self.__field)
        elif act == 2:
            ret = self.__holdMino.right_rotate(self.__field)
        elif act == 3:
            ret = self.__holdMino.left_move(self.__field)
        elif act == 4:
            ret = self.__holdMino.right_move(self.__field)
        elif act == 5:
            ret = self.__holdMino.down_move(self.__field)

        return ret
    
    def step(self, acts: tuple, debug=False) -> tuple[int, bool]:
        '''
            テトリスの1ステップ

            Ret
                (num_del_lines, done)

                num_del_lines: 消したラインの数
                done: ゲームオーバーならTrue
        '''

        if type(acts) == type(int(0)):
            acts = [acts]


        # ミノの移動
        for act in acts:
            if act in [0, 1, 2, 3, 4]:
                self.action(act)

            if act == 6:
                while self.__holdMino.down_move(self.__field):
                    pass
                break

        # 自動落下判定
        self.__downCounter += 1
        if (self.__downCounter >= self.__downCounter_threshold or 5 in acts or 6 in acts) and not debug:
            self.flag_landing = not self.action('dm')
            self.__downCounter = 0
        
        # print(self.flag_landing)

        # ミノ書き込み
        num_del_lines = 0
        if self.flag_landing:
            # フィールドに設置されたミノを書き込み
            self.write_mino(self.__holdMino.get_minoGrid(), self.__holdMino.get_position())

            # ラインの消去
            num_del_lines = self.del_line()

        # ゲームオーバー判定
        if self.judge_gameover():
            return num_del_lines, True, True

        # 次のミノを生成
        if self.flag_landing:
            self.place_nextMino()

        ret_flag_landing = copy.copy(self.flag_landing)
        self.flag_landing = False

        return num_del_lines, False, ret_flag_landing

    def place_nextMino(self, mino:str=None, position: list=None):
        self.__holdMino = Holdmino(self.__field, minoType=mino, position=position)
        
        # TODO: 初期位置に設置できない可能性を考慮してない
        
    def write_mino(self, minoGrid: np.array, position: list):
        '''
            minoGridをfieldに書き込む
            holdMinoが設置した際に使用する
        '''
        if not self.can_write_mino(minoGrid, position):
            raise RuntimeError('ミノの書き込みに失敗')
        
        y, x = position
        field_grid = self.__field[y:y+len(minoGrid), x:x+len(minoGrid[0])]

        for i in range(len(minoGrid)):
            for j in range(len(minoGrid[0])):
                if minoGrid[i][j] != 0:
                    field_grid[i][j] = block_state[self.__holdMino.get_minoID()]
                    
    def can_write_mino(self, minoGrid: np.array, position: list):
        '''
            minoGridがfieldに書き込めるか判定
        '''
        y, x = position
        field_grid = self.__field[y:y+len(minoGrid), x:x+len(minoGrid[0])]

        # 書き込めるか
        for mline, fline in zip(minoGrid, field_grid):
            for  mblock, fblock in zip(mline, fline):
                if mblock not in writable_block_state and fblock not in writable_block_state:
                    return False
        return True
    
    def del_line(self):
        '''
            ラインの消去
        '''
        gameArea = self.get_gameArea()
        del_count = 0

        for idx in range(len(gameArea)):
            can_del = gameArea[idx].all()

            if can_del:
                del_count += 1
                gameArea[0:idx+1] = np.vstack([[np.zeros(len(gameArea[0]), dtype=int)], gameArea[0:idx]])
        
        return del_count
    
    def show(self, all=False, showing=False):
        minopos_y, minopos_x = self.__holdMino.get_position()
        minoGrid = self.__holdMino.get_minoGrid()

        show_field = copy.deepcopy(self.__field)

        # ゲームオーバーエリアを書き込む
        gameover_pos = self.get_gameover_pos()
        for y, x in gameover_pos:
            show_field[y][x] = block_state['gameover']

        show_fieldGrid = show_field[ minopos_y: minopos_y+len(minoGrid),  minopos_x: minopos_x+len(minoGrid[0])]
        # print(show_fieldGrid)
        # print(f'y, x = {y}, {x}')
        # print(len(minoGrid), len(minoGrid[0]))

        # holdMinoを画面表示用に書き込む
        for i in range(len(minoGrid)):
            for j in range(len(minoGrid[0])):
                if minoGrid[i][j] != 0:
                    show_fieldGrid[i][j] = block_state[self.__holdMino.get_holdID()]

        if not all:
            show_field = show_field[self.__above_height:-1 * self.__side_margin, self.__side_margin:-1 * self.__side_margin]

        if not showing:
            return show_field

        for line in show_field:
            for block in line:
                print(f'{block:2d}', end='')
            print()
        
        return show_field
    
    def set_block(self, pos: list, val: int):
        y, x = pos
        self.__field[y][x] = val

    def judge_gameover(self):
        '''
        ゲームオーバー判定
        '''
        gameover_areas_idx = [
            [self.__above_height, int(len(self.__field[0]) / 2)], 
            [self.__above_height, int(len(self.__field[0]) / 2) - 1]
        ]

        if len(self.__field) % 2 == 1:
            gameover_areas_idx.append([4, int(len(self.__field[0]) / 2) + 1])

        # print(self.__field)
        for idx in gameover_areas_idx:
            y, x = idx
            if self.__field[y][x] != 0:
                return True
        return False
    
    ### getter ###
    def get_gameArea(self):
        return self.__field[0:-2, 2:-2]
    
    def get_displayArea(self):
        return self.__field[4:-2, 2:-2]
    
    def get_holdMino(self):
        return copy.deepcopy(self.__holdMino)
    
    def get_gameover_pos(self):
        pos = []
        pos.append([self.__above_height, int(len(self.__field[0]) / 2)])
        pos.append([self.__above_height, int(len(self.__field[0]) / 2) + 1])

        if len(self.__field[0]) % 2 == 1:
            pos.append([self.__above_height, int(len(self.__field[0]) / 2) - 1])
        return pos
            
class TestField:
    def __init__(self, mino=None, size=(10, 7)):
        self.__field = np.zeros(size, dtype=np.int32)
        self.__holdMino = Holdmino(self.__field, position=(3, 3), minoType=mino)
    
    def show(self):
        minopos_y, minopos_x = self.__holdMino.get_position()
        minoGrid = self.__holdMino.get_minoGrid()

        show_field = copy.deepcopy(self.__field)

        show_fieldGrid = show_field[ minopos_y: minopos_y+len(minoGrid),  minopos_x: minopos_x+len(minoGrid[0])]

        # holdMinoを画面表示用に書き込む
        for i in range(len(minoGrid)):
            for j in range(len(minoGrid[0])):
                if minoGrid[i][j] != 0:
                    show_fieldGrid[i][j] = block_state[self.__holdMino.get_holdID()]
        
        # for line in show_field:
        #     for block in line:
        #         print(block, end='')
        #     print()
        
        return show_field
    
    def action(self, act: int):
        '''
            0: 何もしない
            1: left rotate
            2: right rotate
            3: left move
            4: right move
            5: down move
            6: abs move(TODO 未定義)
        '''
        if type(act) == type('str'):
            act = action_table[act]

        game_field = self.__field[:-1, 1:-1]
        if act == 0:
            pass
            ret = False
        elif act == 1:
            ret = self.__holdMino.left_rotate(self.__field)
        elif act == 2:
            ret = self.__holdMino.right_rotate(self.__field)
        elif act == 3:
            ret = self.__holdMino.left_move(self.__field)
        elif act == 4:
            ret = self.__holdMino.right_move(self.__field)
        elif act == 5:
            ret = self.__holdMino.down_move(self.__field)

        return ret
    
    def get_holdMino(self):
        return self.__holdMino