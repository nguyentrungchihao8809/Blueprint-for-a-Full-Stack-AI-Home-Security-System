import cv2
from ultralytics import YOLO
import serial
import time
import sys

# --- CẤU HÌNH KẾT NỐI 8051 ---
ser = None
try:
    # Đảm bảo COM3 khớp với cấu hình trong Proteus/Phần cứng thật
    ser = serial.Serial('COM3', 9600, timeout=1) 
    print("--- Kết nối thành công với cổng COM3 ---")
except Exception as e:
    print(f"Lỗi kết nối Serial: {e}")

# --- CẤU HÌNH VIDEO CÓ SẴN ---
# Thay 'duong_dan_video.mp4' bằng tên file video của bạn
VIDEO_PATH = "trom.mp4" 

# --- KHỞI TẠO ---
model = YOLO('yolo11n.pt') 

# Mở video trực tiếp từ đường dẫn file
cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    print(f"Không thể mở file video: {VIDEO_PATH}. Thoát...")
    sys.exit(1)

last_send_time = 0

print(f"--- HỆ THỐNG ĐANG CHẠY: NHẬN DIỆN NGƯỜI (FILE: {VIDEO_PATH}) ---")
print("--- Nhấn 'q' hoặc Ctrl+C để dừng chương trình ---")

try:
    while cap.isOpened():
        success, frame = cap.read()
        if not success: 
            print("\nKết thúc video hoặc không thể đọc khung hình.")
            break

        # Chạy nhận diện (class 0 là người)
        results = model.predict(frame, classes=[0], conf=0.5, verbose=False)
        
        person_detected = False

        for r in results:
            for box in r.boxes:
                person_detected = True
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                
                # Vẽ khung và nhãn
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                label = f"NGUOI: {conf:.2f}"
                cv2.putText(frame, label, (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # --- LOGIC GỬI LỆNH ---
        current_time = time.time()
        if person_detected:
            # Giới hạn tốc độ gửi để tránh treo vi điều khiển (10 lần/giây)
            if ser and (current_time - last_send_time > 0.1):
                ser.write(b'A') 
                last_send_time = current_time
            print(f"\r[STATUS] PHÁT HIỆN NGƯỜI -> Gửi 'A' ({current_time:.2f})", end="")
        
        # Hiển thị cửa sổ
        cv2.imshow("He thong AI Nhan dien Nguoi - Video File", frame)

        # Thoát bằng phím 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("\n\n--- Nhận tín hiệu dừng từ bàn phím (Ctrl+C) ---")

finally:
    # GIẢI PHÓNG TÀI NGUYÊN
    print("--- Đang đóng tài nguyên... ---")
    if cap.isOpened():
        cap.release()
    if ser:
        ser.close()
    cv2.destroyAllWindows()
    print("--- Đã dừng hệ thống sạch sẽ. ---")
    sys.exit(0)