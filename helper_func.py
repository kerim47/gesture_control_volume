import subprocess
import numpy as np
import os, cv2

def set_valid_volume(volume, min_v=0, max_v=100):
    return max(min_v, min(max_v, volume))

def change_volume(action='set', amount='50'):
    """
    Ses seviyesini ayarlamak için genel fonksiyon.
    
    action: 'set', 'increase' veya 'decrease' olabilir.
    amount: Ses seviyesi veya artış/azalış miktarı.
    """
    if action == 'set':
        command = f"{amount}%"
    elif action == 'increase':
        command = f"+{amount}%"
    elif action == 'decrease':
        command = f"-{amount}%"

    subprocess.call(["pactl", "set-sink-volume", "@DEFAULT_SINK@", command])

def increase(increment=5):
    change_volume('increase', increment)

def decrease(decrement=5):
    change_volume('decrease', decrement)

def set_volume(volume):
    change_volume('set', volume)

def load_png_volume_as_nparray(path, extension='.png'):
    if isinstance(path, str):
        path = [path]  # Gelen yol bir string ise listeye çeviriyoruz
    
    images = {}
    for p in path:
        if os.path.isfile(p):  # Eğer gelen yol bir dosya ise
            if p.lower().endswith(extension):  # Sadece PNG dosyalarını kabul ediyoruz
                img = cv2.imread(p, cv2.IMREAD_UNCHANGED)
                fname = os.path.splitext(os.path.split(p)[-1])[0]
                images[fname] = img
            else:
                print(f"{p} is not a {extension.upper()} file. Skipping.")  # PNG dosyası değilse geç
        elif os.path.isdir(p):  # Eğer gelen yol bir dizin ise
            for file_name in os.listdir(p):
                file_path = os.path.join(p, file_name)
                if os.path.isfile(file_path) and file_name.lower().endswith(extension):  # Sadece PNG dosyalarını kabul ediyoruz
                    img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
                    fname = os.path.splitext(file_name)[0]
                    images[fname] = img
        else:
            print(f"{p} is not a valid file or directory path.")
    
    return images

def overlay_frames(frame1, frame2, position):
    """
    İkinci çerçeveyi birinci çerçevenin belirtilen pozisyonuna ekler.
    """
    # İkinci çerçevenin boyutlarını al
    height2, width2 = frame2.shape[:2]
    
    # Eklenmek istenen pozisyonu al
    x, y = position
    
    # İkinci çerçeveyi birinci çerçeveye eklemek için gerekli hesaplamalar
    if x + width2 > frame1.shape[1] or y + height2 > frame1.shape[0]:
        print("Warning: Second frame exceeds dimensions of first frame. Clipping may occur.")
    
    # Alfa kanalını kullanarak overlay yap
    alpha_s = frame2[:, :, 3] / 255.0
    alpha_l = 1.0 - alpha_s

    for c in range(0, 3):
        frame1[y:y+height2, x:x+width2, c] = (alpha_s * frame2[:, :, c] + alpha_l * frame1[y:y+height2, x:x+width2, c])
    return frame1

def get_status_with_resize(path, size=(80, 80), extension='.png'):
    durumlari_al = load_png_volume_as_nparray(path, extension)
    durum = {name: cv2.resize(arr, size) for name, arr in durumlari_al.items()}
    return durum

def change_icon_color(frame, target_color=[255, 0, 0, 255], mask_color=[0, 0, 0, 255]):
    """
    Verilen numpy dizisindeki mask_color ile eşleşen pikselleri target_color ile değiştirir.
    
    frame: Numpy dizisi, her piksel RGBA değerlerini içerir.
    target_color: Değiştirilecek hedef renk, varsayılan olarak kırmızı [255, 0, 0, 255].
    mask_color: Değiştirilecek hedef pikselleri belirlemek için maske renk, varsayılan olarak tamamen şeffaf [0, 0, 0, 0].
    
    Returns:
    --------
    Numpy dizisi, renk değiştirilmiş hali.
    """
    # Yeni bir dizi oluşturarak orijinal frame'i değiştirmeden çalışmak daha güvenlidir.
    new_frame = frame.copy()
    
    # Her pikseli kontrol et ve mask_color ile eşleşenleri target_color ile değiştir
    mask = (new_frame == mask_color).all(axis=-1)
    new_frame[mask] = target_color
    
    return new_frame

