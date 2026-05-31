from ultralytics import YOLO
import cv2
import serial
import time

# ============================================
# CAU HINH
# ============================================
COM_PORT = 'COM5'       # Cong serial ket noi Arduino
BAUD_RATE = 9600
CONFIDENCE = 0.5        # Nguong tin cay toi thieu (50%)

# ============================================
# KET NOI SERIAL VOI ARDUINO
# ============================================
try:
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print(f"[OK] Ket noi thanh cong voi {COM_PORT}")
except Exception as e:
    print(f"[LOI] Khong the ket noi Serial: {e}")
    print("     Hay chac chan Proteus dang chay!")
    ser = None

# ============================================
# LOAD 2 MODEL YOLO
# ============================================
print("Dang tai model YOLO...")
model_fire = YOLO("best.pt")        # Phat hien lua
model_thief = YOLO("yolo11n.pt")    # Phat hien nguoi

print("San sang! Nhan 'Q' de thoat.\n")

# ============================================
# HAM GUI TIN HIEU VE ARDUINO
# ============================================
def send_signal(signal):
    if ser:
        ser.write(signal.encode())
        print(f"[ARDUINO] Da gui tin hieu: '{signal}'")

# Bien trang thai de tranh gui lien tuc
fire_detected = False
person_detected = False

# ============================================
# CHAY 2 VIDEO SONG SONG
# ============================================
cap_fire = cv2.VideoCapture("test_fire.mp4")
cap_thief = cv2.VideoCapture("trom.mp4")

while True:
    ret1, frame_fire = cap_fire.read()
    ret2, frame_thief = cap_thief.read()

    # Loop lai video khi het
    if not ret1:
        cap_fire.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret1, frame_fire = cap_fire.read()
    if not ret2:
        cap_thief.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret2, frame_thief = cap_thief.read()

    # ---- PHAT HIEN LUA ----
    results_fire = model_fire(frame_fire, verbose=False)
    annotated_fire = results_fire[0].plot()

    fire_found = False
    for box in results_fire[0].boxes:
        if box.conf[0] >= CONFIDENCE:
            fire_found = True
            break

    if fire_found and not fire_detected:
        print("[CANH BAO] Phat hien LUA!")
        send_signal('3')    # Bat coi hu
        send_signal('1')    # Bat LED
        fire_detected = True
    elif not fire_found and fire_detected:
        print("[OK] Lua da tat.")
        send_signal('4')    # Tat coi
        send_signal('2')    # Tat LED
        fire_detected = False

    # Hien thi trang thai len man hinh
    status_fire = "LUA PHAT HIEN!" if fire_found else "Binh thuong"
    color_fire = (0, 0, 255) if fire_found else (0, 255, 0)
    cv2.putText(annotated_fire, status_fire, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color_fire, 2)
    cv2.imshow("Camera 1 - Phat hien LUA", annotated_fire)

    # ---- PHAT HIEN NGUOI ----
    results_thief = model_thief(frame_thief, verbose=False)
    annotated_thief = results_thief[0].plot()

    person_found = False
    for box in results_thief[0].boxes:
        cls_id = int(box.cls[0])
        label = model_thief.names[cls_id]
        if label == "person" and box.conf[0] >= CONFIDENCE:
            person_found = True
            break

    if person_found and not person_detected:
        print("[CANH BAO] Phat hien NGUOI LA!")
        send_signal('1')    # Bat LED
        send_signal('3')    # Bat coi
        person_detected = True
    elif not person_found and person_detected:
        print("[OK] Khong con nguoi la.")
        send_signal('2')    # Tat LED
        send_signal('4')    # Tat coi
        person_detected = False

    # Hien thi trang thai len man hinh
    status_thief = "NGUOI LA PHAT HIEN!" if person_found else "Binh thuong"
    color_thief = (0, 0, 255) if person_found else (0, 255, 0)
    cv2.putText(annotated_thief, status_thief, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color_thief, 2)
    cv2.imshow("Camera 2 - Phat hien NGUOI", annotated_thief)

    # Nhan Q de thoat
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Thoat chuong trinh.")
        break

# Don dep
cap_fire.release()
cap_thief.release()
cv2.destroyAllWindows()
if ser:
    ser.close()
