import os
import cv2
import copy
import numpy as np
import time

# テトリスパッケージ
from Canvas.Canvas import block_colors
from Controller.Controller import MoveController
from Field.TetrisField import TetrisField, block_state
from Camera.Camera import CalibratedVideoCapture
from CheckerBoard.CheckerBoard import CheckerBoard
from Sound.GameSound import GameSound
from Mino.Mino import MinoCalculator

class NextMinoCanvas:
    def __init__(self, mino: MinoCalculator, pos: tuple, block_size: int, margin):
        self.__mino = mino
        self.__pos = pos
        self.__block_size = block_size
        self.__margin = margin
    
    def plot(self, img: np.array):
        '''
        imgに次のミノを表示する
        '''
        minoGrid = self.__mino.grid(0)

        for i in range(len(minoGrid)):
            for j in range(len(minoGrid[0])):
                y, x = self.__pos
                points = np.array([
                    [y + i * (self.__block_size + self.__margin), x + j * (self.__block_size + self.__margin)], 
                    [y + i * (self.__block_size + self.__margin) + self.__block_size, x + j * (self.__block_size + self.__margin)], 
                    [y + i * (self.__block_size + self.__margin) + self.__block_size, x + j * (self.__block_size + self.__margin) + self.__block_size], 
                    [y + i * (self.__block_size + self.__margin), x + j * (self.__block_size + self.__margin) + self.__block_size]
                ], dtype=np.int32)
                color = block_colors[block_state[self.__mino.ID()]] if minoGrid[i][j] == 1 else (255, 255, 255)

                cv2.fillConvexPoly(img, points, color)
        
        return img

class ScoreBoard:
    '''
    TetraMoveのスコアボード
    '''
    def __init__(self, score: int, pos: tuple):
        self.__score = 0
    
    def plot(self, frame: np.array):
        '''
        スコアボードのプロット
        '''
        pass

class TetraMove:
    '''
    TetraMove アプリケーション

    TODO
        得点機能の実装
            1列消し → 100
            2列消し → 100 * 2 * (1 + 2 * 0.1)
            n列消し → 100 * n * (1 + n * 0.1)
        得点ボードの追加
    '''
    def __init__(self, 
                 cam: cv2.VideoCapture, 
                 player: GameSound, 
                 fieldSize: tuple=(10, 7), 
                 controller=MoveController(posLevel_resolution=9, angle_per_level=15)):
        # フィールド関連
        self.__fieldSize = fieldSize
        self.__field = TetrisField(fieldSize[0], fieldSize[1])

        # コントローラ関連
        self.__controller = controller

        # カメラ関連
        self.__cam = cam
        ret, self.__cnt_frame = cam.read()
        if not ret:
            raise RuntimeError('TetraMove init Error: カメラからのフレームの取得に失敗')
        
        # サウンド関連
        self.__player = player

        # チェッカーボード関連
        self.__cnt_chb = CheckerBoard(self.__cnt_frame, (fieldSize[0] - 1, fieldSize[1] - 1), is_percept_aroundCorners=True)

        # 遷移フラグ
        self.__flag_quit = False

        # プレイ中に使用される変数
        self.__score = 0

    def start(self):
        
        self.__player.play_bgm()
        while self.__cam.isOpened():

            # リセット
            self.__controller.reset(self.__cnt_frame, self.__cnt_chb)
            self.__field = TetrisField(self.__fieldSize[0], self.__fieldSize[1])
            self.__score = 0

            ### 待機
            self.phase_title()
            
            if self.__flag_quit:
                break
            
            ### スタート合図
            self.phase_ready()

            if self.__flag_quit:
                break

            self.phase_countdown()

            ### ゲーム
            self.phase_game()

            if self.__flag_quit:
                break

            # ゲームオーバー
            self.phase_gameover()

            if self.__flag_quit:
                break

        self.__player.kill()

    def phase_title(self):
        '''
        タイトル画面
        '''
        self.write_console('phase: タイトル画面')
        while self.__cam.isOpened() and not self.__flag_quit:
            ret = self.update_state()

            # カメラからフレームが読み取れなければ終了
            if not ret:
                self.__flag_quit = True
                break

            ploted_frame = copy.deepcopy(self.__cnt_frame)
            ploted_frame = self.adjustFrame(ploted_frame, False, do_plot_title=True, do_plot_state=False)
            key = self.show_frame(ploted_frame)

            # ゲームをやめる
            if key == ord('q'):
                self.write_console('pushed q')

                self.__player.play_sound('select')
                self.__flag_quit = True
                break

            if key == ord('s'):
                self.write_console('pushed q')

                self.__player.play_sound('select')
                break

            if key == ord('d'):
                self.write_console('pushed d')

                self.__player.play_sound('select')
                self.phase_optest()

    def phase_ready(self):
        '''
        スタート待機状態
        '''
        
        self.write_console('phase: ready')
        while not self.can_game_start():

            # 顔の角度とボードの中心を同時に取得できなければ，スタートできない
            ret = self.update_frame()
            self.__controller.reset(self.__cnt_frame, self.__cnt_chb)

            if not ret:
                self.__flag_quit = True
                break

            # Attentionメッセージの決定
            attention_text = ''
            if self.__controller.get_positionLevel() == None:
                attention_text = 'Checkerboard not Detected'
            if self.__controller.get_rotateLevel() == None:
                attention_text = 'Your Face not Detected'

            ploted_frame = copy.deepcopy(self.__cnt_frame)
            ploted_frame = self.adjustFrame(ploted_frame, False, do_text_frameCenter=True, text='', sub_text=attention_text)
            key = self.show_frame(ploted_frame)

            # ゲームをやめる
            if key == ord('q'):
                self.write_console('pushed q')

                self.__player.play_sound('select')
                self.__flag_quit = True
                break

    def phase_countdown(self, first_count: int=3):
        
        self.write_console('phase: countdown')
        for count in reversed(range(1, first_count + 1)):
            start = time.time()
            end = time.time()
            while not (end - start >= 1):
                ret = self.update_state()
                if not ret:
                    self.__flag_quit = True
                    break

                ploted_frame = copy.deepcopy(self.__cnt_frame)
                ploted_frame = self.adjustFrame(ploted_frame, False, do_text_frameCenter=True, text=count)
                key = self.show_frame(ploted_frame)
                end = time.time()

                if key == ord('q'):
                    self.write_console('pushed q')

                    self.__player.play_sound('select')
                    self.__flag_quit = True
                    break
    
    def phase_game(self):
        '''
        ゲームプレイ状態
        '''
        while True:
            # 状態を更新
            ret = self.update_state()
            if not ret:
                self.__flag_quit = True
                break

            # 操作を取得 ⁺ 実行
            acts = self.get_actions()
            num_del_lines, is_game_over, is_landing = self.__field.step(acts)

            if num_del_lines > 0:
                self.__player.play_sound('del_line')
            elif is_landing:
                self.__player.play_sound('landing')
            
            # 得点の計算
            self.__score = self.update_score(self.__score, num_del_lines)

            # コンソールへ現在の状態の出力
            self.output_gamestate()

            # ラインを消すとレベルアップ
            if num_del_lines > 0:
                self.write_console(f'level up. threshold changed to {self.__field.get_downCounter_threshold()}')
                for _ in range(num_del_lines):
                    self.__field.levelup(step=3)

            # 描画 + 表示
            ploted_frame = copy.deepcopy(self.__cnt_frame)
            ploted_frame = self.adjustFrame(ploted_frame, True)
            key = self.show_frame(ploted_frame)

            # ゲームをやめる
            if key == ord('q'):
                self.write_console('pushed q')

                self.__player.play_sound('select')
                self.__flag_quit = True
                break

            if is_game_over:
                break
        print(f'score: {self.__score}')

    def phase_gameover(self):
        '''
        ゲームオーバー状態
        '''
        self.write_console('phase: gameover')
        self.__player.play_sound('gameover')
        while True:
            ret = self.update_state()
            if not ret:
                self.__flag_quit = True
                break

            ploted_frame = copy.deepcopy(self.__cnt_frame)
            ploted_frame = self.adjustFrame(ploted_frame, True, do_text_frameCenter=True, text='Game Over', sub_text='press \'R\' to restart')
            key = self.show_frame(ploted_frame)

            # ゲームをやめる
            if key == ord('q'):
                self.write_console('pushed q')

                self.__player.play_sound('select')
                self.__flag_quit = True
                break

            # リスタート
            if key == ord('r'):
                self.write_console('pushed r')

                self.__player.play_sound('select')
                break
 
    def phase_optest(self):
        '''
        操作テスト状態
        '''
        self.write_console('phase: debug mode')
        testField = TetrisField(10, 7, position=(7, 3))

        while self.__cam.isOpened():
            # 状態を更新
            ret = self.update_state()
            if not ret:
                self.__flag_quit = True
                break

            # 操作を取得 ⁺ 実行
            acts = self.get_actions(testField)
            num_del_lines, is_game_over, is_landing = testField.step(acts, debug=True)

            # 描画 + 表示
            ploted_frame = copy.deepcopy(self.__cnt_frame)
            ploted_frame = self.adjustFrame(ploted_frame, True, field=testField)
            key = self.show_frame(ploted_frame)

            # テストモード終了
            if key == 27:
                self.__player.play_sound('select')
                break

            ### ミノの変更
            if key == ord('i'):
                self.__player.play_sound('select')
                testField = TetrisField(10, 7, position=(7, 3), firstMinoID='Imino')

            if key == ord('o'):
                self.__player.play_sound('select')
                testField = TetrisField(10, 7, position=(7, 3), firstMinoID='Omino')

            if key == ord('s'):
                self.__player.play_sound('select')
                testField = TetrisField(10, 7, position=(7, 3), firstMinoID='Smino')

            if key == ord('z'):
                self.__player.play_sound('select')
                testField = TetrisField(10, 7, position=(7, 3), firstMinoID='Zmino')

            if key == ord('j'):
                self.__player.play_sound('select')
                testField = TetrisField(10, 7, position=(7, 3), firstMinoID='Jmino')

            if key == ord('l'):
                self.__player.play_sound('select')
                testField = TetrisField(10, 7, position=(7, 3), firstMinoID='Lmino')

            if key == ord('t'):
                self.__player.play_sound('select')
                testField = TetrisField(10, 7, position=(7, 3), firstMinoID='Tmino')

    def update_score(self, cnt_score: int, num_del_line) -> int:
        '''
        得点の計算

        Args:
            cnt_score: 現在のスコア
            num_del_line: 消去ライン数

        Return:
            更新後のスコア
        '''
        return int(cnt_score + 100 * num_del_line * (1 + 0.1 * (num_del_line - 1)))

    def can_game_start(self):
        '''
        ゲームがスタートできるか

        具体的には以下が満たされているか
        ・ チェッカーボードを認識している
        ・ 顔の角度を認識している
        '''
        rotateLevel = self.__controller.get_rotateLevel()
        positionLevel = self.__controller.get_positionLevel()

        return rotateLevel != None and positionLevel != None
    
    def update_frame(self):
        ret, self.__cnt_frame = self.__cam.read()

        if not ret:
            self.__flag_quit = True
            return False
        
        self.__cnt_chb = CheckerBoard(self.__cnt_frame, (self.__fieldSize[0] - 1, self.__fieldSize[1] - 1), is_percept_aroundCorners=True)

        return True
    
    def update_state(self):
        ret = self.update_frame()
        if not ret:
            return False
        
        self.__controller.calc(self.__cnt_frame, self.__cnt_chb)
        
        return True
    
    def get_actions(self, field: TetrisField=None):
        acts = self.get_rotate_actions(field) + self.get_move_actions(field)
        return acts

    def get_rotate_actions(self, field: TetrisField=None):
        '''
        回転操作の入力を取得
        '''
        if field == None:
            field = self.__field

        # 向けたいミノの向き(dist_direction)を取得
        angle_level = self.__controller.get_rotateLevel()
        dist_direction = 0
        if angle_level == 1:
            dist_direction = 1
        elif angle_level == 2:
            dist_direction = 2
        elif angle_level == -1:
            dist_direction = 3
        elif angle_level == -2:
            dist_direction = 2

        # どの方向に何回回転すればよいかを計算
        holdmino_cnt_direction = field.get_holdMino().get_direction()
        acts = []
        if dist_direction == 0:
            if holdmino_cnt_direction == 0:
                pass
            elif holdmino_cnt_direction == 1:
                acts.append(2)
            elif holdmino_cnt_direction == 2:
                acts.append(2)
                acts.append(2)
            elif holdmino_cnt_direction == 3:
                acts.append(1)
        elif dist_direction == 1:
            if holdmino_cnt_direction == 0:
                acts.append(2)
            elif holdmino_cnt_direction == 1:
                pass
            elif holdmino_cnt_direction == 2:
                acts.append(1)
            elif holdmino_cnt_direction == 3:
                acts.append(2)
                acts.append(2)
        elif dist_direction == 2:
            if holdmino_cnt_direction == 0:
                acts.append(2)
                acts.append(2)
            elif holdmino_cnt_direction == 1:
                acts.append(2)
            elif holdmino_cnt_direction == 2:
                pass
            elif holdmino_cnt_direction == 3:
                acts.append(1)
        elif dist_direction == 3:
            if holdmino_cnt_direction == 0:
                acts.append(2)
            elif holdmino_cnt_direction == 1:
                acts.append(2)
                acts.append(2)
            elif holdmino_cnt_direction == 2:
                acts.append(1)
            elif holdmino_cnt_direction == 3:
                pass
        
        return acts

    def get_move_actions(self, field: TetrisField=None):
        '''
        移動入力の操作を取得
        '''
        if field == None:
            field = self.__field
        # 最終的に移動したい場所(dist_pos)を計算
        posLevel = self.__controller.get_positionLevel()
        holdmino_cnt_center_x = field.get_holdMino().get_minoCenter()[1]
        dist_pos = None
        if posLevel == None:
            dist_pos = holdmino_cnt_center_x
        else:
            dist_pos = 9 - posLevel
        
        # どちらに何回移動させれば酔いかを計算
        acts = []
        if dist_pos > holdmino_cnt_center_x:
            for _ in range(dist_pos - holdmino_cnt_center_x):
                acts.append(4)
        else:
            for _ in range(holdmino_cnt_center_x - dist_pos):
                acts.append(3)
        
        return acts
        
    def plot_state(self, frame: np.array) -> np.array:
        '''
        状態を画面上に表示
        現在は入力状態のみ
        '''
        # angle_text = f'angle : {self.__controller.get_angle()}'
        angleL_text = f'angle level: {self.__controller.get_rotateLevel()}'
        level_text = f'pos level  : {self.__controller.get_positionLevel()}'
        # cv2.putText(frame, angle_text, (5, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(frame, angleL_text, (5, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(frame, level_text, (5, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        return frame
    
    def plot_field(self, frame: np.array, field: TetrisField=None) -> np.array:
        '''
        フィールドをプロットする
        '''

        if field == None:
            field = self.__field
        # チェッカーボード用に表示フィールドを変形
        clone_field = copy.deepcopy(field.show()).T
        field_forChb = np.array([])
        
        for line in clone_field:
            field_forChb = np.concatenate([line, field_forChb], 0)
        
        # チェッカーボードへ描画
        block_colors_forChb = copy.deepcopy(block_colors)
        block_colors_forChb.pop(0)
        block_colors_forChb.pop(1)
        block_colors_forChb.pop(2)
        frame = self.__cnt_chb.plot_color(frame, field_forChb, block_colors_forChb)
        frame = self.__cnt_chb.write_x(frame, field_forChb, [2])

        return frame
    
    def show_frame(self, frame):
        cv2.imshow('TetraMove', frame)
        key = cv2.waitKey(1) & 0xFF
        return key
    
    def flip_and_resize_frame(self, frame: np.array) -> np.array:
        frame = cv2.resize(frame, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_LINEAR)
        frame = cv2.flip(frame, 1)

        return frame
    
    def plot_text_frameCenter(self, frame: np.array, text: str, sub_text=None):
        displayed_count = str(text)
        h, w, _ = frame.shape

        # フォント設定
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 5 
        thickness = 10
        color = (0, 0, 255) 

        # テキストサイズ決定
        (text_width, text_height), _ = cv2.getTextSize(displayed_count, font, font_scale, thickness)
        text_x = (w - text_width) // 2
        text_y = (h + text_height) // 2

        cv2.putText(frame, displayed_count, (text_x, text_y), font, font_scale, color, thickness, cv2.LINE_AA)

        # サブテキストがある場合はその下に表示
        if sub_text:
            sub_font_scale = 1.5
            sub_thickness = 3
            sub_color = (0, 0, 0)
            (sub_text_width, sub_text_height), _ = cv2.getTextSize(sub_text, font, sub_font_scale, sub_thickness)
            sub_text_x = (w - sub_text_width) // 2
            sub_text_y = text_y + sub_text_height + 40  # メインテキストの下に余白を取って表示

            cv2.putText(frame, sub_text, (sub_text_x, sub_text_y), font, sub_font_scale, sub_color, sub_thickness, cv2.LINE_AA)

        return frame 

    def plot_next_mino(self, frame):
        '''
        次に落下するミノを表示する
        '''
        minoQue = self.__field.get_minoQue()
        next_mino = minoQue[0]

        plot_pos = (5, 5)
        block_size = 5
        margin = 1

        h, w, _ = frame.shape

        nextMinoCanvas = NextMinoCanvas(next_mino, (w - 150, 5), 30, 2)
        frame = nextMinoCanvas.plot(frame)

        return frame

    def plot_title(self, frame):

        h, w, _ = frame.shape

        # 文字列（すべて大文字）
        line1 = "TETRA"
        line2 = "MOVE"
        lines = [line1, line2]

        # 各文字の色（BGR）
        colors_line1 = [
            (0, 0, 255),       # T
            (0, 165, 255),     # E
            (0, 255, 255),     # T
            (0, 255, 0),       # R
            (255, 0, 0)        # A
        ]

        colors_line2 = [
            (128, 0, 128),     # M
            (0, 0, 255),       # O
            (255, 128, 0),     # V
            (255, 255, 0)      # E
        ]
        colors = [colors_line1, colors_line2]

        # フォント設定
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 8
        thickness = 30
        line_spacing = 30

        # 各行の文字サイズと幅合計を計算（中央揃えのため）
        line_sizes = []
        line_widths = []

        for line in lines:
            sizes = [cv2.getTextSize(ch, font, font_scale, thickness)[0] for ch in line]
            widths = [s[0] for s in sizes]
            total_width = sum(widths)
            line_sizes.append(sizes)
            line_widths.append(total_width)

        # 全体の高さ（行数と行間を含めて中央揃え）
        total_height = sum([max(s[1] for s in sizes) for sizes in line_sizes]) + line_spacing
        y0 = (h - total_height) // 2  # 上端 y 座標（全体中央揃え）

        # 描画
        y = y0
        for line_idx, line in enumerate(lines):
            sizes = line_sizes[line_idx]
            widths = [s[0] for s in sizes]
            height = max([s[1] for s in sizes])
            x = (w - line_widths[line_idx]) // 2

            for i, ch in enumerate(line):
                cv2.putText(frame, ch, (x, y + height), font, font_scale, colors[line_idx][i], thickness, cv2.LINE_AA)
                x += widths[i]
            y += height + line_spacing
        
        instruction_text = 'press \'s\' to start'
        x = (w - cv2.getTextSize(instruction_text, font, 1.5, 3)[0][0]) // 2
        cv2.putText(frame, 'press \'s\' to start', (x, y + 50), font, 1.5, (0, 0, 0), 3)
        
        return frame

    def adjustFrame(self, 
                    frame, 
                    in_game_phase: bool, field: TetrisField=None, 
                    do_text_frameCenter: bool=False, text=None, sub_text=None, 
                    do_plot_state: bool=True, 
                    do_plot_title: bool=False) -> np.array:
        ploted_frame = copy.deepcopy(frame)

        if in_game_phase:
            ploted_frame = self.plot_field(ploted_frame, field=field)

        ploted_frame = self.flip_and_resize_frame(ploted_frame)

        if in_game_phase:
            ploted_frame = self.plot_next_mino(ploted_frame)

        if do_text_frameCenter:
            ploted_frame = self.plot_text_frameCenter(ploted_frame, text, sub_text=sub_text)
        
        if do_plot_state:
            ploted_frame = self.plot_state(ploted_frame)
        
        if do_plot_title:
            ploted_frame = self.plot_title(ploted_frame)

        return ploted_frame

    def write_console(self, text: str):
        '''
        コンソール出力を明示的に行うために定義
        わかりやすいように緑の文字で出力
        '''
        print('\033[32m' + str(text) + '\033[0m')
    
    def output_gamestate(self):
        '''
        ゲーム中の状態の出力
        '''
        print('----------------------------')
        print('game state')
        print(f'score: {self.__score}')
        print(f'downcount threshold: {self.__field.get_downCounter_threshold()}')
        self.__field.show(all=True, showing=True)

