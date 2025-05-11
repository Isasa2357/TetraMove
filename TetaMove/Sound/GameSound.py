import pygame
import time
import keyboard
from playsound import playsound
import os


class GameSound:
    def __init__(self, base_path, BGM, sound_dict: dict):
        pygame.init()
        pygame.mixer.init()

        # BGM
        self.__base_path = base_path
        self.__bgm_path = os.path.join(base_path, BGM)
        # BGMをロード
        pygame.mixer.music.load(self.__bgm_path)  # BGMのファイルパスを指定
        pygame.mixer.music.set_volume(0.5)  # 音量を設定（0.0〜1.0）

        self.__sound_dict = dict()
        for key, value in sound_dict.items():
            self.__sound_dict[key] = pygame.mixer.Sound(os.path.join(base_path, value))
            self.__sound_dict[key].set_volume(1.0)
    
    def play_sound(self, key):
        self.__sound_dict[key].play()

    def play_bgm(self):
        pygame.mixer.music.play(-1)  # -1は無限ループで再生

    def kill(self):
        pygame.mixer.music.stop()
        pygame.quit()

def test():
    base_path = 'C:\\Work\\UV_env\\present_opencv\\Tetris\\Sound\\sound'
    BGM = 'Tetris_BGM.wav'
    sound_dict = {
        'landing': 'land_mino.wav', 
        'del_line': 'del_line.wav'
    }
    player = GameSound(base_path, BGM, sound_dict)
    player.play_bgm()

    # ゲームのメインループ（例）
    while True:
        if keyboard.is_pressed('q'):
            break
        if keyboard.is_pressed('a'):
            player.play_sound('landing')
        if keyboard.is_pressed('s'):
            player.play_sound('del_line')

    player.kill()

if __name__ == '__main__':
    test()