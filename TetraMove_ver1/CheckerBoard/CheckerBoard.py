

import os
import cv2
import numpy as np
import copy

class CheckerBoard:
    '''
    チェッカーボードの認識をするクラス
    コーナーの補間や拡張も行う

    TODO コーナーの補間が未実装
    '''
    def __init__(self, img: np.array, pattern_size: tuple, is_percept_aroundCorners: bool=False):
        '''
        Args
            img: チェッカーボードが含まれた画像．RGBを想定している
        '''
        self.__img = img
        self.__pattern_size = pattern_size
        
        self.__corners = None
        self.__ret = None
        if is_percept_aroundCorners:
            self.__ret, self.__corners = self.percept_corners_with_aroundCorners()
        else:
            self.__ret, self.__corners = self.percept_corners()
    
    def could_percept(self):
        '''
        チェッカーボードを認識しているか
        '''
        return self.__ret
    
    def percept_corners_with_aroundCorners(self):
        '''
        推測したチェッカーボードの縁上の交点をcornerに追加
        '''
        ret, corners = self.percept_corners()
        if not ret:
            return ret, corners
        corners = self.estimate_aroundCorners()

        # pattern_sizeの修正
        x, y = self.__pattern_size
        self.__pattern_size = (x + 2, y + 2)
        return ret, corners
    
    def percept_corners(self) -> np.array:
        '''
        チェッカーボードの交点を認識
        '''
        # グレー画像に変換
        gray = cv2.cvtColor(self.__img, cv2.COLOR_RGB2GRAY)

        # コーナーの認識
        ret, self.__corners = cv2.findChessboardCorners(gray, self.__pattern_size)

        if not ret:
            return ret, self.__corners

        # コーナーをサブピクセル精度で洗練
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        self.__corners = cv2.cornerSubPix(gray, self.__corners, (11, 11), (-1, -1), criteria)

        return ret, self.__corners 

    def estimate_aroundCorners(self):
        '''
        cv2.findChessboardCornersによって認識した交点から，縁上の位置の交点を計算する
        '''
        ### 列方向の縁上の交点を追加
        # 左端
        leftside_new_corners = []
        for i in range(self.__pattern_size[0]):
            x1, y1 = self.__corners[i + self.__pattern_size[0] * (self.__pattern_size[1] - 1)][0]
            x2, y2 = self.__corners[i + self.__pattern_size[0] * (self.__pattern_size[1] - 2)][0]

            new_x, new_y = 2*x1 - x2, 2*y1 - y2

            leftside_new_corners.append([[new_x, new_y]])

        self.__corners = np.vstack([self.__corners, leftside_new_corners])
        
        # 右端
        rightside_new_corners = []
        for i in range(self.__pattern_size[0]):
            x1, y1 = self.__corners[i][0]
            x2, y2 = self.__corners[i + self.__pattern_size[0]][0]

            new_x, new_y = 2*x1 - x2, 2*y1 - y2

            rightside_new_corners.append([[new_x, new_y]])

        self.__corners = np.vstack([rightside_new_corners, self.__corners])

        ### 行方向の交点を追加

        for i in reversed(range(self.__pattern_size[1] + 2)):
            # 上側位置計算
            x1, y1 = self.__corners[i * self.__pattern_size[0]][0]
            x2, y2 = self.__corners[i * self.__pattern_size[0] + 1][0]
            upper_corner = [2*x1 - x2, 2*y1 - y2]

            # 下側位置計算
            x1, y1 = self.__corners[self.__pattern_size[0] * (i + 1) - 1][0]
            x2, y2 = self.__corners[self.__pattern_size[0] * (i + 1) - 2][0]
            lower_corner = [2*x1 - x2, 2*y1 - y2]

            self.__corners = np.vstack([self.__corners[0:self.__pattern_size[0] * (i + 1)], 
                                       [[lower_corner]], 
                                       self.__corners[self.__pattern_size[0] * (i + 1):]])
            self.__corners = np.vstack([self.__corners[0:i * self.__pattern_size[0]], 
                                      [[upper_corner]], 
                                      self.__corners[i * self.__pattern_size[0]:]])
        
        return self.__corners

    def interpolate_corners(self, corners):
        '''
        cs2.findChessboardCornersで認識できなかった交点を補間する

        TECHECK この環境で，cv2.findChessboardCornersが交点を全て認識できなかった場合に何を返すかを確認
        '''
        pass

    def get_Angle(self):
        '''
        チェッカーボードの角度を計算する
        '''
        if not self.could_percept():
            return None
        
        num_holizonLine = int(len(self.__corners) / self.__pattern_size[0])

        angles = []
        for i in range(num_holizonLine):
            x1, y1 = self.__corners[i][0]
            x2, y2 = self.__corners[i + self.__pattern_size[0] * (self.__pattern_size[1] - 1)][0]
            angle = (y1 - y2) / (x1 - x2)
            # angle = math.atan((y1 - y2) / (x1 - x2))
            angles.append(angle)
        return sum(angles) / len(angles)

    def get_boardCenter(self):
        '''
        ボードの中心を計算する
        '''
        if not self.could_percept():
            return [None, None]

        xs = [corner[0][0] for corner in self.__corners]
        ys = [corner[0][1] for corner in self.__corners]

        center = [
            sum(xs) / len(xs), 
            sum(ys) / len(ys)
        ]
        return center

        # # cornerの四隅を抜き出す
        # points = [
        #     self.__corners[0], 
        #     self.__corners[self.__pattern_size[0] - 1], 
        #     self.__corners[-1 - self.__pattern_size[0] + 1], 
        #     self.__corners[-1]
        # ]

        # xs = [point[0][0] for point in points]
        # ys = [point[0][1] for point in points]

        # # ボードの中心を計算
        # center = [sum(xs) / len(xs), sum(ys) / len(xs)]

        # return center
    
    def plot_corners(self, color=(0, 255, 0)):
        '''
        認識したcornerを画像にプロット
        '''
        if not self.could_percept():
            return None
        
        ploted_img = copy.deepcopy(self.__img)
        for corner in self.__corners:
            x, y = corner[0]
            x, y = int(x), int(y)
            cv2.circle(ploted_img, (x, y), 2, color, -1)
        return ploted_img
    
    def plot_center(self, img, color=(255, 0, 0)):
        '''
        ボードの中心を画像にプロット
        '''
        if not self.could_percept():
            return img

        center = self.get_boardCenter()
        x, y = center
        x, y = int(x), int(y)
        
        ploted_img = copy.deepcopy(img)
        cv2.circle(ploted_img, (x, y), 4, color, -1)
        return ploted_img
    
    def plot_color(self, img, arr: np.array, color_table: dict):
        '''
        チェッカーボードのグリッドに色を塗る

        arr: グリッドごとの色ID
        color_table: IDと色の対応表
        '''
        ploted_img = copy.deepcopy(img)
        if not self.could_percept():
            return self.__img

        if arr.size != (self.__pattern_size[0] - 1) * (self.__pattern_size[1] - 1):
            err_str = 'CheckerBoard.plot_color(): arrのサイズが不正です'
            raise RuntimeError(err_str)

        arr_clone = copy.deepcopy(arr)
        for i in reversed(range(self.__pattern_size[1] - 2)):
            arr_clone = np.concatenate([arr_clone[0:(self.__pattern_size[0] - 1)*(i+1)], 
                                        [None], 
                                        arr_clone[(self.__pattern_size[0] - 1)*(i+1):]], 0)
        arr_clone = np.concatenate([arr_clone, [None], [None for _ in range(self.__pattern_size[0])]], 0)

        for i in range(len(self.__corners)):
            ### 左端，下側の場合パス
            # 下側
            if ((i + 1) % self.__pattern_size[0] == 0):
                continue
            # 左端
            if (i + 1 > self.__pattern_size[0] * (self.__pattern_size[1] - 1)):
                continue
            
            idx_dxs = [
                0, 
                1, 
                self.__pattern_size[0] + 1, 
                self.__pattern_size[0]
            ]
            coord_dydxs = [
                [3, -3], 
                [-3, -3], 
                [-3, 3], 
                [3, 3]
            ]
            
            points = []
            for idx_dx, (coord_dy, coord_dx) in zip(idx_dxs, coord_dydxs):
                x = self.__corners[i + idx_dx][0][0] + coord_dx
                y = self.__corners[i + idx_dx][0][1] + coord_dy
                point = [x, y]
                points.append(point)
            points = np.array(points, dtype=np.int32)

            # points = np.array([
            #     self.__corners[i][0], 
            #     self.__corners[i + 1][0], 
            #     self.__corners[i + self.__pattern_size[0] + 1][0], 
            #     self.__corners[i + self.__pattern_size[0]][0], 
            # ], dtype=np.int32)
            # print(points)
            # print(type(points))
            
            if arr_clone[i] not in color_table.keys():
                continue

            cv2.fillPoly(ploted_img, [points], color_table[arr_clone[i]])
        
        return ploted_img
    
    def write_x(self, img: np.array, arr: np.array, vals):
        if not self.could_percept():
            return self.__img

        arr_clone = copy.deepcopy(arr)
        for i in reversed(range(self.__pattern_size[1] - 2)):
            arr_clone = np.concatenate([arr_clone[0:(self.__pattern_size[0] - 1)*(i+1)], 
                                        [None], 
                                        arr_clone[(self.__pattern_size[0] - 1)*(i+1):]], 0)
        arr_clone = np.concatenate([arr_clone, [None], [None for _ in range(self.__pattern_size[0])]], 0)

        ploted_img = copy.deepcopy(img)
        for i, block in enumerate(arr_clone):
            if block in vals:
                idx_dxs = [
                    0, 
                    1, 
                    self.__pattern_size[0] + 1, 
                    self.__pattern_size[0]
                ]
                
                points = []
                for idx_dx in idx_dxs:
                    x = self.__corners[i + idx_dx][0][0]
                    y = self.__corners[i + idx_dx][0][1]
                    point = [x, y]
                    points.append(point)
                points = np.array(points, dtype=np.int32)

                cv2.line(ploted_img, points[0], points[2], (0, 0, 255), 1)
                cv2.line(ploted_img, points[1], points[3], (0, 0, 255), 1)
        return ploted_img
    
    def img_shape(self):
        return self.__img.shape
    
def test():
    imgs_path = [os.path.join('./img', img) for img in os.listdir('./img') if img.split('.')[-1] == 'jpg']

    for img_path in imgs_path:

        img = cv2.imread(img_path)

        chb = CheckerBoard(img, (9, 6), is_percept_aroundCorners=True)
        
        cv2.imshow('center', chb.plot_center())
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        cv2.imshow('corners', chb.plot_corners())
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        print(chb.get_Angle())
    print('Done')

if __name__ == '__main__':
    test()