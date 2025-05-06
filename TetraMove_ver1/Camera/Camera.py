

import json

import cv2
import numpy as np


class CalibratedVideoCapture(cv2.VideoCapture):
    def __init__(self, source: int, config: dict):
        super().__init__(source)

        self.__do_calibrate = True
        self.__DIM = config['DIM']
        self.__K = np.array(config['K'])
        self.__D = np.array(config['D'])

    def read(self) -> tuple[bool, np.array]:
        '''
        キャリブレーション済みフレームを出力
        '''
        ret, frame = super().read()

        if (ret and 
            self.__do_calibrate and 
            all(dim is not None for dim in self.__DIM) and 
            all(k is not None for k in self.__K) and 
            all(d is not None for d in self.__D)):
            frame = self.calibrating_frame(frame)
        
        return ret, frame
    
    def calibrating_frame(self, frame):
        map1, map2 = cv2.fisheye.initUndistortRectifyMap(self.__K, self.__D, np.eye(3), self.__K, self.__DIM, cv2.CV_16SC2)
        calibrated_img = cv2.remap(frame, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

        return calibrated_img

    def set_do_calibrate(self, do_calibrate):
        self.__do_calibrate = do_calibrate

def test():
    DIM=(640, 480)
    K=np.array([[510.02904573020135, 0.0, 263.0317530718527], [0.0, 509.0654512480136, 195.13538414706917], [0.0, 0.0, 1.0]])
    D=np.array([[0.10768690741978285], [0.1302694020642326], [-1.198695351884587], [1.4520532216539979]])
    cap = CalibratedVideoCapture(1, DIM, K, D)

    
    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            print('ret is false')
            break

        cv2.imshow('cap', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

def write_json():
    DIM=(640, 480)
    K=np.array([[510.02904573020135, 0.0, 263.0317530718527], [0.0, 509.0654512480136, 195.13538414706917], [0.0, 0.0, 1.0]])
    D=np.array([[0.10768690741978285], [0.1302694020642326], [-1.198695351884587], [1.4520532216539979]])

    config_dict = {
        'DIM': DIM, 
        'K': K.tolist(), 
        'D': D.tolist()
    }
    with open('TUNSONE_WEBCAM_CALIBRATION_CONFIG.json', 'w') as f:
        json.dump(config_dict, f, indent=2)

if __name__ == '__main__':
    write_json()