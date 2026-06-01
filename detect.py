from ultralytics import YOLO
import cv2

# ============================================
# CHON CHE DO PHAT HIEN
# 1 = Phat hien lua (best.pt + test_fire.mp4)
# 2 = Phat hien trom (yolo11n.pt + trom.mp4)
# ============================================
MODE = 2

if MODE == 1:
    model_path = "best.pt"
    video_path = "test_fire.mp4"
    window_title = "Phat hien LUA - Fire Detection"
    print(">>> Che do: Phat hien LUA")
else:
    model_path = "yolo11n.pt"
    video_path = "trom.mp4"
    window_title = "Phat hien TROM - Thief Detection"
    print(">>> Che do: Phat hien TROM")

# Load model
print(f"Dang tai model: {model_path}")
model = YOLO(model_path)

# Mo video
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print(f"[LOI] Khong mo duoc video: {video_path}")
    exit()

print("Dang chay... Nhan 'Q' de thoat.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Video da chay xong.")
        break

    # Chay YOLO detection
    results = model(frame, verbose=False)

    # Ve bounding box len frame
    annotated_frame = results[0].plot()

    # Hien thi ket qua
    cv2.imshow(window_title, annotated_frame)

    # Nhan Q de thoat
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Thoat chuong trinh.")
        break

cap.release()
cv2.destroyAllWindows()
