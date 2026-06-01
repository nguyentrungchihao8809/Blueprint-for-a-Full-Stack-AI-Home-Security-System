from ultralytics import YOLO
import cv2
import serial
import time

# ============================================
# CAU HINH
# ============================================
COM_PORT = 'COM5'
BAUD_RATE = 9600
CONFIDENCE = 0.5

# ============================================
# KET NOI SERIAL VOI ARDUINO
# ============================================
try:
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print(f"[OK] Ket noi thanh cong voi {COM_PORT}")
except Exception as e:
    print(f"[LOI] Khong the ket noi Serial: {e}")
    ser = None

# ============================================
# LOAD 2 MODEL YOLO
# ============================================
print("Dang tai model YOLO...")
model_fire = YOLO("best.pt")
model_thief = YOLO("yolo11n.pt")
print("San sang! Nhan 'Q' de thoat.\n")

# ============================================
# HAM GUI TIN HIEU VE ARDUINO
# ============================================
def send_signal(signal):
    if ser:
        ser.write(signal.encode())
        print(f"[ARDUINO] Da gui tin hieu: '{signal}'")

# Bien trang thai
fire_detected = False
prev_person_count = -1

# ============================================
# CHAY 2 VIDEO
# ============================================
cap_fire = cv2.VideoCapture("test_fire.mp4")
cap_thief = cv2.VideoCapture("trom.mp4")

while True:
    ret1, frame_fire = cap_fire.read()
    ret2, frame_thief = cap_thief.read()

    if not ret1:
        cap_fire.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret1, frame_fire = cap_fire.read()
    if not ret2:
        cap_thief.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret2, frame_thief = cap_thief.read()

    # ---- PHAT HIEN LUA ----
    results_fire = model_fire(frame_fire, verbose=False)
    annotated_fire = results_fire[0].plot()

    fire_found = any(box.conf[0] >= CONFIDENCE for box in results_fire[0].boxes)

    if fire_found and not fire_detected:
        print("[CANH BAO] Phat hien LUA!")
        send_signal('3')
        send_signal('1')
        fire_detected = True
    elif not fire_found and fire_detected:
        print("[OK] Lua da tat.")
        send_signal('4')
        send_signal('2')
        fire_detected = False

    status_fire = "LUA PHAT HIEN!" if fire_found else "Binh thuong"
    color_fire = (0, 0, 255) if fire_found else (0, 255, 0)
    cv2.putText(annotated_fire, status_fire, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color_fire, 2)
    cv2.imshow("Camera 1 - Phat hien LUA", annotated_fire)

    # ---- PHAT HIEN VA DEM NGUOI ----
    results_thief = model_thief(frame_thief, verbose=False)
    annotated_thief = results_thief[0].plot()

    # Dem so nguoi trong frame
    person_count = sum(
        1 for box in results_thief[0].boxes
        if model_thief.names[int(box.cls[0])] == "person"
        and box.conf[0] >= CONFIDENCE
    )

    # Gui tin hieu dieu hoa neu so nguoi thay doi
    if person_count != prev_person_count:
        if person_count == 0:
            print(f"[DIEU HOA] 0 nguoi -> TAT dieu hoa")
            send_signal('7')
        elif person_count <= 2:
            print(f"[DIEU HOA] {person_count} nguoi -> Dat 26 do C")
            send_signal('5')
        else:
            print(f"[DIEU HOA] {person_count} nguoi -> Dat 24 do C")
            send_signal('6')
        prev_person_count = person_count

    # Hien thi trang thai nguoi + dieu hoa
    if person_count == 0:
        status_ac = "0 nguoi | AC: OFF"
        color_ac = (200, 200, 200)
    elif person_count <= 2:
        status_ac = f"{person_count} nguoi | AC: 26C"
        color_ac = (255, 200, 0)
    else:
        status_ac = f"{person_count} nguoi | AC: 24C"
        color_ac = (0, 100, 255)

    cv2.putText(annotated_thief, status_ac, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color_ac, 2)
    cv2.imshow("Camera 2 - Dem nguoi & Dieu hoa", annotated_thief)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Thoat chuong trinh.")
        break

cap_fire.release()
cap_thief.release()
cv2.destroyAllWindows()
if ser:
    ser.close()