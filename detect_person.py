from ultralytics import YOLO
import cv2
import serial
import time

# ============================================
# CAU HINH
# ============================================
COM_PORT = 'COM5'
BAUD_RATE = 9600
CONFIDENCE = 0.3

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
# LOAD MODEL YOLO
# ============================================
print("Dang tai model YOLO...")
model = YOLO("yolo11n.pt")
print("San sang! Nhan 'Q' de thoat.\n")

# ============================================
# HAM GUI TIN HIEU VE ARDUINO
# ============================================
def send_signal(signal):
    if ser and ser.is_open:
        payload = (signal + "\r\n").encode('utf-8')
        ser.write(payload)
        ser.flush()
        time.sleep(0.2)
        if ser.in_waiting > 0:
            reply = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            print(f"[SERIAL REPLY] {reply.strip()}")
        print(f"[ARDUINO] Da gui tin hieu: '{signal}' (bytes={payload!r})")

prev_person_count = -1

# ============================================
# CHAY VIDEO
# ============================================
cap = cv2.VideoCapture("trom.mp4")

while True:
    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = cap.read()

    results = model(frame, verbose=False)

    annotated = frame.copy()
    person_count = 0

    for box in results[0].boxes:
        cls_id = int(box.cls[0])
        label = model.names[cls_id]
        conf = box.conf[0]
        if label == "person" and conf >= CONFIDENCE:
            person_count += 1
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(annotated, f"person {conf:.2f}",
                       (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Gui tin hieu dieu hoa khi so nguoi thay doi
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
        status = "0 nguoi | AC: OFF"
        color = (200, 200, 200)
    elif person_count <= 2:
        status = f"{person_count} nguoi | AC: 26C"
        color = (0, 255, 255)
    else:
        status = f"{person_count} nguoi | AC: 24C"
        color = (0, 100, 255)

    cv2.putText(annotated, status, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    cv2.imshow("Dem nguoi & Dieu hoa", annotated)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Thoat.")
        break

cap.release()
cv2.destroyAllWindows()
if ser:
    ser.close()
