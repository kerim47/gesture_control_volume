from handDetector import HandDetector
from helper_func import *
import cv2, math
import numpy as np
import warnings

warnings.filterwarnings("ignore")

durumlari_al = get_status_with_resize(path='./svg2png')

hand_detector = HandDetector(trackConf=0.9, detectionConf=0.8)
cap = cv2.VideoCapture(0)

position = (45, 75)  # İkinci çerçevenin eklenmek istenen pozisyonu

while True:
    success, img = cap.read()
    if not success:
        print("Kameradan görüntü alınamadı.")
        break
    
    hand = hand_detector.find_hands(img)
    lm_list = hand_detector.find_position(img, draw=False)    
    
    if len(lm_list) >= 8:
        id1, x1, y1 = lm_list[4]
        id2, x2, y2 = lm_list[8]
        
        cv2.circle(img, (x1, y1), 15, (255, 0, 255))
        cv2.circle(img, (x2, y2), 15, (255, 0, 255))
        cv2.line(img, (x1, y1), (x2, y2), (0, 255, 255))
        
        # İki nokta arasındaki mesafeyi bulma
        # current_distance = cv2.norm(np.array([x1, y1]) - np.array([x2, y2]), cv2.NORM_L2)
        current_distance = math.hypot(x2-x1, y2-y1)
        print("Current distance", current_distance)

        # interpolasyon kullanarak iki değer arasında alınan değerleri istenen aralıkta oranlar.
        volume_val = round(np.interp(current_distance, [25, 190], [0, 100]))
        volume_val = set_valid_volume(volume_val)
        set_volume(volume_val)
        
        # Ses seviyesi göstergesi
        doldur = int(400 - volume_val * 2.5)
        cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
        cv2.rectangle(img, (50, doldur), (85, 400), (255, 0, 0), cv2.FILLED)
        cv2.putText(img, f'{int(volume_val)}%', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)
        

        if volume_val == 0:
            sound_type = 'ses_0'
        elif 0 < volume_val <= 33:
            sound_type = 'ses_1'
        elif 33 < volume_val <= 66:
            sound_type = 'ses_2'
        elif 66 < volume_val <= 100:
            sound_type = 'ses_3'

        hand = overlay_frames(img.copy(), change_icon_color(durumlari_al[sound_type], target_color=[0, 10, 0, 255]), position)

        
    cv2.imshow("El Kontrol", hand)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Program sonlandırılıyor...")
        break

cap.release()
cv2.destroyAllWindows()