
import json

from Canvas.Canvas import *
from Field.TetrisField import *
from Mino.Mino import *
from CheckerBoard.CheckerBoard import *
import numpy as np
import keyboard
from Controller.Controller import MoveController
from Camera.Camera import CalibratedVideoCapture
from Sound.GameSound import GameSound

from App import Tetris_App

def calibrating_img(img, DIM, K, D):
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
    calibrated_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

    return calibrated_img

def test_field_show():
    field = TetrisField(15, 9)
    
    field.show()
    while True:
        act = input('>> ')

        if act.isdigit():
            field.step(int(act))
        elif act == 'set':
            y, x, val = input('coord >> ').split(',')
            y, x = int(y), int(x)
            field.set_block([y, x], val)
        
        field.show()

def test_canvas_show():
    field = TetrisField(15, 9)
    canvas = PromptCanvas((15, 9))

    canvas.write(field.show(showing=False))
    while True:
        act = input('>> ')

        if act.isdigit():
            _, is_gameover = field.step(int(act))
        elif act == 'set':
            y, x, val = input('coord >> ').split(',')
            y, x = int(y), int(x)
            field.set_block([y, x], val)
        
        canvas.write(field.show(showing=False))

        if is_gameover:
            break
    print('game over')

def test_RTGame():
    field = TetrisField(15, 9)
    canvas = PromptCanvas((15, 9))

    canvas.write(field.show(showing=False))
    while True:
        # キー入力の認識
        action = 0
        if keyboard.is_pressed('a'):
            action = 1
        elif keyboard.is_pressed('s'):
            action = 2
        elif keyboard.is_pressed('left'):
            action = 3
        elif keyboard.is_pressed('right'):
            action = 4
        elif keyboard.is_pressed('down'):
            action = 5
        elif keyboard.is_pressed('up'):
            action = 6

        num_del_line, is_gameover = field.step(action)
        
        for _ in range(10):
            print()
        canvas.write(field.show(showing=False))

        print(field.get_holdMino().get_minoCenter())

        if is_gameover:
            break

        time.sleep(0.1)
    print('game over')

def playTetris_onChb():
    field = TetrisField(10, 7)
    
    cap = cv2.VideoCapture(1)
    img = cv2.imread(os.path.join('img', '2_chb.jpg'))
    p_canvas = PromptCanvas((10, 7))

    controller = MoveController(posLevel_resolution=9, angle_per_level=15)

    DIM=(640, 480)
    K=np.array([[510.02904573020135, 0.0, 263.0317530718527], [0.0, 509.0654512480136, 195.13538414706917], [0.0, 0.0, 1.0]])
    D=np.array([[0.10768690741978285], [0.1302694020642326], [-1.198695351884587], [1.4520532216539979]])

    while (cap.isOpened()):
        ret, frame = cap.read()

        if not ret:
            print('ret is False')
            break

        frame = calibrating_img(frame, DIM, K, D)

        ### 入力
        
        ## 回転
        angle_level = controller.calc_rotateLevel(frame)
        dist_direction = 0
        if angle_level == 1:
            dist_direction = 1
        elif angle_level == 2:
            dist_direction = 2
        elif angle_level == -1:
            dist_direction = 3
        elif angle_level == -2:
            dist_direction = 2

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
        
        ## 移動
        chb = CheckerBoard(frame, (9, 6), is_percept_aroundCorners=True)
        posLevel = controller.calc_positinoLevel(chb)

        holdmino_cnt_center_x = field.get_holdMino().get_minoCenter()[1]
        dist_pos = None
        if posLevel == None:
            dist_pos = holdmino_cnt_center_x
        else:
            dist_pos = 9 - posLevel
        
        if dist_pos > holdmino_cnt_center_x:
            for _ in range(dist_pos - holdmino_cnt_center_x):
                acts.append(4)
        else:
            for _ in range(holdmino_cnt_center_x - dist_pos):
                acts.append(3)

        num_del_line, is_gameover = field.step(acts)

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
        frame = chb.plot_color(frame, field_forChb, block_colors_forChb)
        frame = chb.write_x(frame, field_forChb, [2])

        # print('---------------------')
        # field.show(showing=True)

        # 画面拡大 & 反転
        frame = cv2.resize(frame, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_LINEAR)
        frame = cv2.flip(frame, 1)

        angle_text = f'angle : {controller.get_angle()}'
        angleL_text = f'angleL: {controller.get_rotateLevel()}'
        level_text = f'level : {controller.get_positionLevel()}'
        cv2.putText(frame, angle_text, (5, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(frame, angleL_text, (5, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(frame, level_text, (5, 160), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        cv2.imshow('Tetris', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        time.sleep(0.1)

        if is_gameover:
            print('gameover')
            break
    
    cap.release()
    cv2.destroyAllWindows()

def test_Canvas():
    canvas_test()

def test_Mino(mino='Imino'):
    field = TetrisField(10, 7, mino)
    
    cap = cv2.VideoCapture(1)
    img = cv2.imread(os.path.join('img', '2_chb.jpg'))

    controller = MoveController(posLevel_resolution=9, angle_per_level=15)

    DIM=(640, 480)
    K=np.array([[510.02904573020135, 0.0, 263.0317530718527], [0.0, 509.0654512480136, 195.13538414706917], [0.0, 0.0, 1.0]])
    D=np.array([[0.10768690741978285], [0.1302694020642326], [-1.198695351884587], [1.4520532216539979]])

    while (cap.isOpened()):
        ret, frame = cap.read()

        if not ret:
            print('ret is False')
            break

        frame = calibrating_img(frame, DIM, K, D)

        ### 入力
        
        ## 回転
        angle_level = controller.calc_rotateLevel(frame)
        dist_direction = 0
        if angle_level == 1:
            dist_direction = 1
        elif angle_level == 2:
            dist_direction = 2
        elif angle_level == -1:
            dist_direction = 3
        elif angle_level == -2:
            dist_direction = 2

        holdmino_cnt_direction = field.get_holdMino().get_direction()
        acts = []

        print(angle_level, dist_direction, holdmino_cnt_direction)
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
        
        ## 移動
        chb = CheckerBoard(frame, (9, 6), is_percept_aroundCorners=True)
        posLevel = controller.calc_positinoLevel(chb)

        holdmino_cnt_center_x = field.get_holdMino().get_minoCenter()[1]
        dist_pos = None
        if posLevel == None:
            dist_pos = holdmino_cnt_center_x
        else:
            dist_pos = 9 - posLevel

        if dist_pos > holdmino_cnt_center_x:
            for _ in range(dist_pos - holdmino_cnt_center_x):
                acts.append(4)
        else:
            for _ in range(holdmino_cnt_center_x - dist_pos):
                acts.append(3)

        field.action(acts, )

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
        frame = chb.plot_color(frame, field_forChb, block_colors_forChb)
        frame = chb.write_x(frame, field_forChb, [2])

        # print('---------------------')
        # field.show(showing=True)

        # 画面拡大 & 反転
        frame = cv2.resize(frame, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_LINEAR)
        frame = cv2.flip(frame, 1)

        angle_text = f'angle : {controller.get_angle()}'
        angleL_text = f'angleL: {controller.get_rotateLevel()}'
        level_text = f'level : {controller.get_positionLevel()}'
        cv2.putText(frame, angle_text, (5, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(frame, angleL_text, (5, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(frame, level_text, (5, 160), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        cv2.imshow('Tetris', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

def play_TetrisApp():
    calibrating_config_path = 'C:\\Work\\UV_env\\present_opencv\\Tetris\\config\\TUNSONE_WEBCAM_CALIBRATION_CONFIG.json'
    calibrating_config = None
    with open(calibrating_config_path, 'r') as cf:
        calibrating_config = json.load(cf)
    
    cam = CalibratedVideoCapture(1, calibrating_config)
    if not cam.isOpened():
        cam = cv2.VideoCapture(0)

    sound_base_path = 'C:\\Work\\UV_env\\present_opencv\\Tetris\\Sound\\sound'
    BGM = 'Tetris_BGM.wav'
    sound_dict = {
        'landing': 'land_mino.wav', 
        'del_line': 'del_line.wav', 
        'gameover': 'gameover.wav', 
        'select': 'land_mino.wav',       # 決定時の音声は落下時の設置時の音声と同じ
    }
    player = GameSound(sound_base_path, BGM, sound_dict)

    cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    game = Tetris_App.TetraMove(cam, player)

    game.start()

if __name__ == '__main__':
    # test_RTGame()
    # playTetris_onChb()
    # test_Mino('Imino')
    play_TetrisApp()