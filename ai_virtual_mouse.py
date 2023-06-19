
import cv2
import mediapipe as mp
# görsel analiz
import pyautogui
"""otomasyon ve ekran yakalama kütüphanesi
 Bu kütüphane, klavye girişleri yapma, fare hareketleri gerçekleştirme,
 ekranı yakalama, pencere kontrolü gibi bir dizi otomasyon işlemi için kullanılabilir."""

cap = cv2.VideoCapture(0)
# mediapipe kütüphanesinin Hands sınıfını kullanarak bir el algılama modeli oluşturduk
hand_detector = mp.solutions.hands.Hands()
# algılanan ellerin üzerine çizim yapmak veya işaretlemeler eklemek için
drawing_utils = mp.solutions.drawing_utils
# işlevi kullanılarak ekranın genişliğini ve yüksekliğini alır
screen_width, screen_height = pyautogui.size()
index_y = 0
shortcut_keys = ['ctrl','tab']
fp = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [
    0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]

while True:
    # cap değişkeni ile video akışından bir kare okunur ve frame değişkenine atanır
    _, frame = cap.read()
    # Okunan kare, cv2.flip() işlevi kullanılarak yatay olarak çevrilir. Bu, görüntünün aynalanmasını sağlar.
    frame = cv2.flip(frame, 1)
    # framein bilgileri değişkenlere atanır
    frame_height, frame_width, _ = frame.shape
    # bgr to rgb işte mp ye uygun hale getirmek için
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # hand_detector nesnesi kullanılarak process() işlevi çağrılır ve RGB formatında çerçeve işlenir.
    output = hand_detector.process(rgb_frame)
    # el algılama mdelini çalıştırır
    # : output nesnesinin multi_hand_landmarks özelliği kullanılarak algılanan eller elde edilir.
    hands = output.multi_hand_landmarks
    """
    Bu şekilde, sürekli olarak video akışından kareler alınır,
    el algılama işlemi gerçekleştirilir ve algılanan ellerin koordinatları
    hands değişkeninde saklanır.
    """

    if hands:  # en az bir elin algılandığı durumu kontrol eder.
        for hand in hands:  # Algılanan her el için bir döngü oluşturulur.
            # elin noktalarını ve bağlantılarını çizim
            drawing_utils.draw_landmarks(frame, hand)
            # hand içindeki noktaların koordinatlarını içeren landmarks değişkenine atanır
            landmarks = hand.landmark
            # Her bir nokta için bir döngü oluşturulur ve noktaların koordinatlarının hesaplanması yapılır.
            for id, landmark in enumerate(landmarks):
                # Noktanın x koordinatı, noktanın orijinal konumunu kare genişliğiyle çarparak bulunur.
                x = int(landmark.x * frame_width)
                # Noktanın y koordinatı, noktanın orijinal konumunu kare genişliğiyle çarparak bulunur.
                y = int(landmark.y * frame_height)

                fp[id][0] = screen_width / frame_width * x
                fp[id][1] = screen_height / frame_height * y

                if id == 4 or id == 8 or id == 12 or id == 16 or id == 20:   # işaret parmağı en üst boğumu
                    cv2.circle(img=frame, center=(x, y), radius=10,
                               color=(0, 255, 255))  # yuvarlak çizdi



            if abs(fp[8][1] - fp[4][1]) < 20:#eğer baş parmak işaret parmağına deyiyosa 
                pyautogui.click()#tıkla
                pyautogui.sleep(1)         
                
            elif abs(fp[8][1] - fp[4][1]) < 100:
                pyautogui.moveTo(fp[8][0], fp[8][1])
            if abs(fp[12][1]-fp[9][1])<20 and  abs(fp[16][1]-fp[13][1])<20 and abs(fp[4][1]-fp[9][1])<20:
                pyautogui.hotkey(*shortcut_keys)
                print("AUUUUUUUUU")
            
                    
    
                    
    
    cv2.imshow('Virtual Mouse', frame)
    

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):  # qya basıncs kamerayı kapat
        break

# Release the video capture object and close windows
cap.release()
cv2.destroyAllWindows()