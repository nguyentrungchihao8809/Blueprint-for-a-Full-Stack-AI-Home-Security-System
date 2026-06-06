# import cv2
# from ultralytics import YOLO
# import serial
# import time
# import sys

# # --- CẤU HÌNH KẾT NỐI ---
# ser = None
# try:
#     # Đảm bảo COM3 khớp với cấu hình trong Proteus COMPIM
#     ser = serial.Serial('COM3', 9600, timeout=1) 
#     print("--- Kết nối thành công với cổng ảo COM3 ---")
# except Exception as e:
#     print(f"Lỗi kết nối Serial: {e}")

# # --- KHỞI TẠO YOLO11 ---
# model = YOLO('yolo11n.pt') 

# # --- MỞ CAMERA ---
# cap = cv2.VideoCapture(0)

# print("--- HỆ THỐNG ĐANG CHẠY: NHẬN DIỆN NGƯỜI ---")
# print("--- Nhấn Ctrl+C để dừng chương trình sạch sẽ ---")

# last_send_time = 0

# try:
#     while cap.isOpened():
#         success, frame = cap.read()
#         if not success:
#             break

#         # Chạy nhận diện (chỉ lấy class 0 - người)
#         results = model.predict(frame, classes=[0], conf=0.5, verbose=False)
        
#         person_detected = False

#         for r in results:
#             for box in r.boxes:
#                 person_detected = True
#                 x1, y1, x2, y2 = map(int, box.xyxy[0])
#                 conf = float(box.conf[0])
                
#                 # Vẽ khung nhận diện
#                 cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
#                 label = f"NGUOI: {conf:.2f}"
#                 cv2.putText(frame, label, (x1, y1 - 10), 
#                             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

#         # --- LOGIC GỬI LỆNH TỐI ƯU ---
#         current_time = time.time()
#         if person_detected:
#             # Chỉ gửi 'A' sau mỗi 0.1 giây để tránh tràn bộ đệm 8051
#             if ser and (current_time - last_send_time > 0.1):
#                 ser.write(b'A') 
#                 last_send_time = current_time
#             print(f"\r[STATUS] PHÁT HIỆN NGƯỜI -> Đang gửi 'A' ({current_time:.2f})", end="")
        
#         # Hiển thị cửa sổ
#         cv2.imshow("He thong AI Nhan dien Nguoi", frame)

#         # Thoát bằng phím 'q' trên cửa sổ hiển thị
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

# except KeyboardInterrupt:
#     print("\n\n--- Tín hiệu dừng từ bàn phím (Ctrl+C) ---")

# finally:
#     # GIẢI PHÓNG TÀI NGUYÊN
#     print("--- Đang dọn dẹp hệ thống... ---")
#     if cap is not None:
#         cap.release()
#     if ser is not None:
#         ser.close()
#     cv2.destroyAllWindows()
#     print("--- Đã thoát chương trình sạch sẽ. ---")
#     sys.exit(0)

import cv2
from ultralytics import YOLO
import serial
import time
import sys

# --- CẤU HÌNH KẾT NỐI SERIAL ---
ser = None
try:
    ser = serial.Serial('COM3', 9600, timeout=1) 
    print("--- Kết nối thành công với cổng ảo COM3 ---")
except Exception as e:
    print(f"Lỗi kết nối Serial: {e}")

# --- KHỞI TẠO CÁC MODEL YOLO ---
# 1. Model mặc định nhận diện người (lớp 0)
model_person = YOLO('yolo11n.pt') 

# 2. Model bạn vừa train xong (tải file best.pt từ Roboflow về để cùng thư mục)
# Nếu bạn chưa tải về, hãy thay đường dẫn tới file model của bạn
try:
    model_fire = YOLO('best.pt') 
    print("--- Load model Cháy Nổ thành công ---")
except:
    print("--- Lỗi: Không tìm thấy file best.pt. Vui lòng kiểm tra đường dẫn! ---")

# --- MỞ CAMERA ---
cap = cv2.VideoCapture(0)

print("--- HỆ THỐNG ĐANG CHẠY: NGƯỜI & CHÁY NỔ ---")
last_send_time = 0

try:
    while cap.isOpened():
        success, frame = cap.read()
        if not success: break

        # 1. NHẬN DIỆN NGƯỜI (Class 0)
        results_p = model_person.predict(frame, classes=[0], conf=0.5, verbose=False)
        person_detected = False

        # 2. NHẬN DIỆN CHÁY NỔ (Giả sử bạn gán nhãn Fire=0, Smoke=1 trong model mới)
        results_f = model_fire.predict(frame, conf=0.4, verbose=False)
        fire_detected = False

        # Xử lý vẽ khung cho NGƯỜI
        for r in results_p:
            for box in r.boxes:
                person_detected = True
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2) # Màu xanh lá
                cv2.putText(frame, "NGUOI", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Xử lý vẽ khung cho CHÁY NỔ
        for r in results_f:
            for box in r.boxes:
                fire_detected = True
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                label = model_fire.names[int(box.cls[0])].upper() # Lấy tên class (FIRE/SMOKE)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3) # Màu đỏ rực
                cv2.putText(frame, f"!!! {label} !!!", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # --- LOGIC GỬI LỆNH VỀ VI ĐIỀU KHIỂN ---
        current_time = time.time()
        if current_time - last_send_time > 0.2: # Giới hạn tần suất gửi 0.2s
            if fire_detected:
                if ser: ser.write(b'F') # Gửi 'F' khi có cháy (Ưu tiên cao nhất)
                print(f"\r[CẢNH BÁO] PHÁT HIỆN CHÁY NỔ! Đã gửi 'F'", end="")
                last_send_time = current_time
            elif person_detected:
                if ser: ser.write(b'A') # Gửi 'A' khi có người
                print(f"\r[STATUS] Có người tại trạm sạc. Đã gửi 'A'", end="")
                last_send_time = current_time

        # Hiển thị
        cv2.imshow("He thong Canh bao Tram sac EV", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'): break

except KeyboardInterrupt:
    print("\n--- Dừng bởi người dùng ---")
finally:
    if cap: cap.release()
    if ser: ser.close()
    cv2.destroyAllWindows()
    sys.exit(0)