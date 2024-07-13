import cv2
import mediapipe as mp
import pyautogui
import json
import tkinter as tk
from tkinter import ttk, messagebox
import threading

cap = None
camera_running = False

def camera_loop():
    global cap, camera_running
    hand_detector = mp.solutions.hands.Hands()
    drawing_utils = mp.solutions.drawing_utils
    screen_width, screen_height = pyautogui.size()
    fp = [[0, 0] for _ in range(21)]

    with open("settings.json", "r", encoding="utf-8") as f:
        settings = json.load(f)

    while camera_running:
        _, frame = cap.read()
        if frame is None:
            continue
        frame = cv2.flip(frame, 1)
        frame_height, frame_width, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = hand_detector.process(rgb_frame)
        hands = output.multi_hand_landmarks

        if hands:
            for hand in hands:
                drawing_utils.draw_landmarks(frame, hand)
                landmarks = hand.landmark
                for id, landmark in enumerate(landmarks):
                    x = int(landmark.x * frame_width)
                    y = int(landmark.y * frame_height)
                    fp[id][0] = screen_width / frame_width * x
                    fp[id][1] = screen_height / frame_height * y

                    if id in [4, 8, 12, 16, 20]:
                        cv2.circle(img=frame, center=(x, y), radius=10, color=(0, 255, 255))

                pyautogui.moveTo(fp[8][0], fp[8][1])
               
                #print(f"yüzük parmak: {fp[16][0]}, orta parmak : {fp[12][0]}, fark : {abs(fp[16][0]-fp[12][0])} ")

                # Baş parmağının ucunun işaret parmağının dibine değişi
                perform_action(abs(fp[3][0]-fp[5][0]) <= 70, settings["durum1"], settings["hassasiyet"])
                
                # İşaret parmağının ucunun işaret parmağına değişi
                perform_action(abs(fp[20][0] - fp[15][0]) < 60, settings["durum2"], settings["hassasiyet"])

                perform_action(abs(fp[16][0] - fp[12][0]) < 70, settings["durum3"], settings["hassasiyet"])

                perform_action(abs(fp[8][0] - fp[12][0]) < 70, settings["durum4"], settings["hassasiyet"])

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def perform_action(condition, action, sensitivity):
    if condition:
        if action == "sol tık":
            pyautogui.click()
        elif action == "sağ tık":
            pyautogui.click(button='right')
        elif action == "yukarı kaydırma":
            pyautogui.scroll(sensitivity)
        elif action == "aşağı kaydırma":
            pyautogui.scroll(-sensitivity)

def toggle_camera():
    global camera_running, cap
    if camera_running:
        camera_running = False
        cap.release()
        cv2.destroyAllWindows()
        camera_button.config(text="Kamerayı Aç", style="Red.TButton")
    else:
        camera_running = True
        cap = cv2.VideoCapture(0)
        threading.Thread(target=camera_loop).start()
        camera_button.config(text="Kamerayı Kapat", style="Green.TButton")

def save_settings():
    settings = {
        "durum1": dropdown1.get(),
        "durum2": dropdown2.get(),
        "durum3": dropdown3.get(),
        "durum4": dropdown4.get(),
        "hassasiyet": int(sensitivity_value.get())
    }

    actions = [settings["durum1"], settings["durum2"], settings["durum3"], settings["durum4"]]
    actions_without_empty = [action for action in actions if action != "boş"]

    if len(actions_without_empty) != len(set(actions_without_empty)):
        messagebox.showerror("Hata", "Aynı işlem birden fazla duruma atanmış.")
    else:
        with open("settings.json", "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False)

    messagebox.showinfo("Kayıt", "Kayıt işlemi başarılıyla gerçekleşmiştir")

def load_settings():
    try:
        with open("settings.json", "r", encoding="utf-8") as f:
            settings = json.load(f)
            dropdown1.set(settings.get("durum1", "sol tık"))
            dropdown2.set(settings.get("durum2", "sağ tık"))
            dropdown3.set(settings.get("durum3", "yukarı kaydırma"))
            dropdown4.set(settings.get("durum4", "aşağı kaydırma"))
            sensitivity_value.set(settings.get("hassasiyet", 80))
            sensitivity_scale.set(settings.get("hassasiyet", 80))
    except FileNotFoundError:
        save_settings()

def update_sensitivity_value(val):
    sensitivity_value.set(f"{int(float(val))}")

root = tk.Tk()
root.title("Virtual Mouse")
root.geometry("500x400")

style = ttk.Style(root)
style.configure('Red.TButton', background='red')
style.configure('Green.TButton', background='green')

options = ["sol tık", "sağ tık", "yukarı kaydırma", "aşağı kaydırma", "boş"]

padding_options = {'padx': 10, 'pady': 10}

ttk.Label(root, text="Durum 1:").grid(column=0, row=0, **padding_options)
dropdown1 = ttk.Combobox(root, values=options)
dropdown1.grid(column=1, row=0, **padding_options)

ttk.Label(root, text="Durum 2:").grid(column=0, row=1, **padding_options)
dropdown2 = ttk.Combobox(root, values=options)
dropdown2.grid(column=1, row=1, **padding_options)

ttk.Label(root, text="Durum 3:").grid(column=0, row=2, **padding_options)
dropdown3 = ttk.Combobox(root, values=options)
dropdown3.grid(column=1, row=2, **padding_options)

ttk.Label(root, text="Durum 4:").grid(column=0, row=3, **padding_options)
dropdown4 = ttk.Combobox(root, values=options)
dropdown4.grid(column=1, row=3, **padding_options)

ttk.Label(root, text="Hassasiyet:").grid(column=0, row=4, **padding_options)
sensitivity_value = tk.StringVar()
sensitivity_scale = ttk.Scale(root, from_=10, to=200, orient='horizontal', command=update_sensitivity_value)
sensitivity_scale.grid(column=1, row=4, **padding_options)
sensitivity_label = ttk.Label(root, textvariable=sensitivity_value)
sensitivity_label.grid(column=2, row=4, **padding_options)

ttk.Button(root, text="Kaydet", command=save_settings).grid(column=0, row=5, columnspan=3, **padding_options)
camera_button = ttk.Button(root, text="Kamerayı Aç", command=toggle_camera, style="Red.TButton")
camera_button.grid(column=0, row=6, columnspan=3, **padding_options)

load_settings()

def check_camera_status():
    if camera_running:
        camera_button.config(text="Kamerayı Kapat", style="Green.TButton")
    else:
        camera_button.config(text="Kamerayı Aç", style="Red.TButton")
    root.after(1000, check_camera_status)

root.after(1000, check_camera_status)
root.mainloop()
