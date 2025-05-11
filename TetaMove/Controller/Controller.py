
import math
import copy
import cv2
import mediapipe as mp
import numpy as np

from CheckerBoard.CheckerBoard import CheckerBoard

class FaceAnglemeter:
    facetop_centerline_lm_idx = [8, 9, 10, 151, 168]
    facebtm_centerline_lm_idx = [18, 152, 175, 199, 200]

    def __init__(self):
        mp_face_mesh = mp.solutions.face_mesh
        self.__face_mesh = mp_face_mesh.FaceMesh()

    def __call__(self, rgb_img):
        return self.get_angle(rgb_img)
    
    def get_faceCenterlineLm(self, rgb_img):
        ret = self.__face_mesh.process(rgb_img)

        ft_lms = []
        fb_lms = []

        if ret.multi_face_landmarks:
            for face_landmarks in ret.multi_face_landmarks:
                for idx, lm in enumerate(face_landmarks.landmark):
                    if idx in self.facetop_centerline_lm_idx:
                        x, y = int(lm.x * rgb_img.shape[1]), int(lm.y * rgb_img.shape[0])
                        ft_lms.append([x, y])
                    if idx in self.facebtm_centerline_lm_idx:
                        x, y = int(lm.x * rgb_img.shape[1]), int(lm.y * rgb_img.shape[0])
                        fb_lms.append([x, y])
        else:
            return ret.multi_face_landmarks, None, None
        
        return ret.multi_face_landmarks, ft_lms, fb_lms

    
    def get_angle(self, rgb_img):
        '''
        Args
            img:
                RGBである必要あり
        '''
        ret, ft_lms, fb_lms = self.get_faceCenterlineLm(rgb_img)

        if not ret:
            return None, rgb_img
        
        angles = []
        for ft_lm in ft_lms:
            for fb_lm in fb_lms:
                ft_x, ft_y = ft_lm
                fb_x, fb_y = fb_lm
                dx, dy = fb_x - ft_x, fb_y - ft_y
                angle_rad = math.atan2(dy, dx)
                angle_deg = math.degrees(angle_rad)
                angles.append(angle_deg)
        
        ploted_img = self.plot_centerline(rgb_img, ft_lms, fb_lms)

        return sum(angles) / (len(angles) + np.finfo(float).eps), ploted_img
    
    def plot_centerline(self, rgb_img, ft_lms, fb_lms):
        ploted_img = copy.deepcopy(rgb_img)

        for ft_lm in ft_lms:
            x, y = ft_lm
            cv2.circle(ploted_img, (x, y), 1, (0, 255, 0), -1)
        for fb_lm in fb_lms:
            x, y = fb_lm
            cv2.circle(ploted_img, (x, y), 1, (0, 0, 255), -1)

        return ploted_img
        

class MoveController:
    def __init__(self, posLevel_resolution: int, angle_per_level: int):
        self.__faceAngleMetre = FaceAnglemeter()
        self.__posLevel_resolution = posLevel_resolution
        self.__angle_per_level = angle_per_level

        self.__last_angle = None
        self.__last_rotateLevel = None
        self.__last_posLevel = None
    
    def reset(self, img, chb):
        self.__last_angle = None
        self.__last_rotateLevel = None
        self.__last_posLevel = None

        self.calc(img, chb)
    
    def calc(self, img, chb):
        self.calc_rotateLevel(img)
        self.calc_positinoLevel(chb)
    
    def calc_Angle(self, img):
        self.__last_angle, _ = self.__faceAngleMetre.get_angle(img)
        return self.__last_angle
    
    def calc_rotateLevel(self, img):
        '''
        角度をレベル表現に変換し返す
        '''
        self.__last_angle = self.calc_Angle(img)

        if not self.__last_angle:
            return None
        
        if 90 - self.__angle_per_level <= self.__last_angle <= 90 + self.__angle_per_level:
            self.__last_rotateLevel = 0
        elif 90 + self.__angle_per_level <= self.__last_angle <= 90 + 2 * self.__angle_per_level:
            self.__last_rotateLevel = 1
        elif 90 + 2 * self.__angle_per_level <= self.__last_angle <= 90 + 3 * self.__angle_per_level:
            self.__last_rotateLevel = 2
        elif 90 - 2 * self.__angle_per_level <= self.__last_angle <= 90 - self.__angle_per_level:
            self.__last_rotateLevel = -1
        elif 90 - 3 * self.__angle_per_level <= self.__last_angle <= 90 - 2 * self.__angle_per_level:
            self.__last_rotateLevel = -2
        return self.__last_rotateLevel
    
    def calc_positinoLevel(self, chb: CheckerBoard):
        chb_center_coord = chb.get_boardCenter()
        frame_size = chb.img_shape()

        if chb_center_coord == [None, None]:
            return None

        x, _ = chb_center_coord
        _, w, _ = frame_size

        margin_ratio = 0.25
        if 0 <= x < w * margin_ratio:
            self.__last_posLevel = -2
        elif w * margin_ratio <= x <= w * (1 - margin_ratio):
            a = (self.__posLevel_resolution - 1) / ((1 - 2 * margin_ratio) * w)
            b = -1 * a * 0.25 * w
            self.__last_posLevel = round(a * x + b)
        else:
            self.__last_posLevel = self.__posLevel_resolution - 1
        
        return self.__last_posLevel
    
    def get_angle(self):
        return self.__last_angle
    
    def get_rotateLevel(self):
        return self.__last_rotateLevel
    
    def get_positionLevel(self):
        return self.__last_posLevel

def test():
    faceAngleMeter = FaceAnglemeter()
    controller = MoveController(faceAngleMeter, 11)

    cap = cv2.VideoCapture(1)

    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            print('フレームの取得に失敗')
        
        
        angle, ploted_frame = controller.get_Angle(frame)

        chb = CheckerBoard(frame, (9, 6), is_percept_aroundCorners=True)
        level = controller.get_level(chb)

        # for _ in range(20):
        #     print()
        # print(f'angle: {angle}')
        # print(f'level: {level}')

        ploted_frame = chb.plot_center(ploted_frame)

        angle_text = f'angle: {angle}'
        level_text = f'level: {level}'
        cv2.putText(ploted_frame, angle_text, (5, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(ploted_frame, level_text, (5, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow('display', ploted_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    test()