import cv2
import serial
import time
from roboflow import Roboflow
from cap_from_youtube import cap_from_youtube

# --- 1. CẤU HÌNH TÀI KHOẢN ROBOFLOW ---
API_KEY = "eozsPoZ1rW0A6gfmAkHy"
PROJECT_ID = "fire-smoke-detection-lk8z9"
VERSION = 1  # Kiểm tra trên Roboflow xem bạn đã Generate version mấy rồi

# Kết nối Roboflow Online
try:
    rf = Roboflow(api_key=API_KEY)
    project = rf.workspace().project(PROJECT_ID)
    model = project.version(VERSION).model
    print("✅ Đã kết nối thành công với Roboflow Cloud API")
except Exception as e:
    print(f"❌ Lỗi kết nối Roboflow: {e}")

# --- 2. CẤU HÌNH VIDEO & PHẦN CỨNG ---
YOUTUBE_URL = 'https://youtu.be/uMyXkqysop4'
# Mở video YouTube
cap = cap_from_youtube(YOUTUBE_URL, '720p')

# Kết nối 8051 qua cổng COM
ser = None
try:
    ser = serial.Serial('COM3', 9600, timeout=1)
    print("✅ Đã kết nối với 8051 qua COM3")
except:
    print("⚠️ Chế độ mô phỏng (Không tìm thấy mạch 8051)")

last_send_time = 0

# --- 3. VÒNG LẶP XỬ LÝ ---
print("--- HỆ THỐNG ĐANG CHẠY TRỰC TUYẾN ---")

while cap.isOpened():
    success, frame = cap.read()
    if not success: break

    # Gửi ảnh lên server Roboflow để nhận diện
    # Bạn không cần file best.pt ở đây vì máy chủ Roboflow sẽ xử lý
    predictions = model.predict(frame, confidence=40).json()
    
    fire_detected = False
    person_detected = False

    # Duyệt qua các kết quả trả về từ Cloud
    for pred in predictions['predictions']:
        label = pred['class'].lower()
        x, y, w, h = pred['x'], pred['y'], pred['width'], pred['height']
        
        # Tính tọa độ khung hình
        x1, y1 = int(x - w/2), int(y - h/2)
        x2, y2 = int(x + w/2), int(y + h/2)

        # Logic nhận diện (Tên class phải khớp với trên Roboflow của bạn)
        if label in ['fire', 'smoke']:
            fire_detected = True
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(frame, f"!!! {label.upper()} !!!", (x1, y1-10), 1, 1.5, (0,0,255), 2)
        elif label == 'person':
            person_detected = True
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, "PERSON", (x1, y1-10), 1, 1.5, (0,255,0), 2)

    # --- 4. GỬI LỆNH XUỐNG 8051 ---
    curr_time = time.time()
    if curr_time - last_send_time > 1.0: # 1 giây gửi 1 lần để ổn định API
        if fire_detected:
            if ser: ser.write(b'F')
            print("\r🔥 PHÁT HIỆN CHÁY! Gửi 'F'...", end="")
        elif person_detected:
            if ser: ser.write(b'A')
            print("\r👤 CÓ NGƯỜI. Gửi 'A'...", end="")
        else:
            if ser: ser.write(b'N')
        last_send_time = curr_time

    # Hiển thị kết quả
    cv2.imshow("Monitor - UTH Project Online", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
if ser: ser.close()
cv2.destroyAllWindows()