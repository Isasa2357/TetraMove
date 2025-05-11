import numpy as np

type_GameOver = {
     'cant_placeMino_initPos': 1
}

class GameOverException(BaseException):
        '''
        

        インスタンス変数
        __field: ゲームオーバー時のフィールドの状態
        _type_GO: ゲームオーバーした原因を示すID．type_GameOverのこと
        '''
        def __init__(self, field: np.array, type_GO: int):
            self.__field = field
            self.__type_GO = type_GO
        
        def get_field(self):
            return self.__field
        
        def get_type_GO(self):
            return self.__type_GO