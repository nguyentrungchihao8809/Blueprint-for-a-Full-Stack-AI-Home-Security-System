from ultralytics import YOLO
import argparse
import cv2
import serial
import serial.tools.list_ports
import time

# ============================================
# CAU HINH
# ============================================
BAUD_RATE = 9600
CONFIDENCE = 0.3


def find_serial_port():
    preferred = ['COM4', 'COM5']
    available = [port.device for port in serial.tools.list_ports.comports()]
    print(f"[INFO] Ports available: {available if available else 'none'}")

    for port in preferred + available:
        if port in preferred and port not in available:
            pass
        try:
            probe = serial.Serial(port, BAUD_RATE, timeout=0.2, write_timeout=1)
            probe.reset_input_buffer()
            probe.reset_output_buffer()
            probe.write(b'7\r\n')
            probe.flush()
            time.sleep(0.4)
            raw = probe.read(probe.in_waiting) if probe.in_waiting > 0 else b''
            reply = raw.decode('utf-8', errors='ignore')
            probe.close()
            if 'EVENT:' in reply or 'TEMP:' in reply:
                print(f"[PORT-OK] {port} tra loi du lieu: {reply.strip()}")
                return port
            print(f"[PORT-NOT-RESPOND] {port} khong tra loi.")
        except Exception as e:
            print(f"[PORT-ERROR] {port}: {e}")
    return preferred[0]


def parse_args():
    parser = argparse.ArgumentParser(description='YOLO + Serial control')
    parser.add_argument('--port', default=None, help='chon cong serial (VD: COM4)')
    return parser.parse_args()


args = parse_args()
COM_PORT = args.port if args.port else find_serial_port()

# ============================================
# KET NOI SERIAL VOI ARDUINO
# ============================================
try:
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=0.5, write_timeout=1)
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    time.sleep(0.5)
    print(f"[OK] Ket noi thanh cong voi {COM_PORT} ({BAUD_RATE} baud)")
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
    if ser and ser.is_open:
        payload = (signal + "\r\n").encode('utf-8')
        reply_lines = []

        for attempt in range(3):
            ser.reset_input_buffer()
            ser.write(payload)
            ser.flush()

            deadline = time.time() + 1.0
            while time.time() < deadline:
                if ser.in_waiting > 0:
                    raw = ser.read(ser.in_waiting)
                    if raw:
                        decoded = raw.decode('utf-8', errors='ignore')
                        reply_lines.extend([line.strip() for line in decoded.splitlines() if line.strip()])
                else:
                    time.sleep(0.05)

            if reply_lines:
                break
            time.sleep(0.2)

        if reply_lines:
            print(f"[SERIAL REPLY] {' | '.join(reply_lines)}")
        else:
            print(f"[SERIAL WARNING] Khong nhan duoc phan hoi sau khi gui '{signal}'")
            print(f"[DEBUG] COM={ser.name} baud={ser.baudrate} timeout={ser.timeout}")
        print(f"[ARDUINO] Da gui tin hieu: '{signal}' (bytes={payload!r})")

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

    annotated_fire = frame_fire.copy()
    for box in results_fire[0].boxes:
        if box.conf[0] >= CONFIDENCE:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(annotated_fire, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(annotated_fire, f"fire {box.conf[0]:.2f}",
                       (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

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

    # ---- CHI PHAT HIEN NGUOI ----
    results_thief = model_thief(frame_thief, verbose=False)

    annotated_thief = frame_thief.copy()
    person_count = 0
    for box in results_thief[0].boxes:
        cls_id = int(box.cls[0])
        label = model_thief.names[cls_id]
        conf = box.conf[0]
        if label == "person" and conf >= CONFIDENCE:
            person_count += 1
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(annotated_thief, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(annotated_thief, f"person {conf:.2f}",
                       (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

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

    # Hien thi trang thai
    if person_count == 0:
        status_ac = "0 nguoi | AC: OFF"
        color_ac = (200, 200, 200)
    elif person_count <= 2:
        status_ac = f"{person_count} nguoi | AC: 26C"
        color_ac = (0, 255, 255)
    else:
        status_ac = f"{person_count} nguoi | AC: 24C"
        color_ac = (0, 100, 255)

    cv2.putText(annotated_thief, status_ac, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color_ac, 2)
    cv2.imshow("Camera 2 - Chi phat hien NGUOI", annotated_thief)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Thoat chuong trinh.")
        break

cap_fire.release()  
cap_thief.release()
cv2.destroyAllWindows()
if ser:
    ser.close()