from ultralytics import YOLO
import cv2 # Thêm thư viện này để xử lý khung hình

# 1. Load model xịn của Hào
model = YOLO("best.pt")

# 2. Nguồn dữ liệu
video_source = "test_fire.mp4"

# 3. Chạy nhận diện với chế độ STREAM
# stream=True giúp máy không bị tràn RAM khi chạy video dài
results = model.predict(
    source=video_source,
    show=True,         # Hiện cửa sổ trực tiếp
    conf=0.5,          # Chỉ lấy những gì chắc chắn trên 50%
    device='cpu',      # Chạy bằng CPU
    stream=True        # Bật chế độ luồng (Rất quan trọng cho video/webcam)
)

# 4. Vòng lặp để "ép" máy hiển thị liên tục
print("🚀 Đang kết nối với YouTube và nhận diện... Nhấn 'q' để thoát.")
for r in results:
    # r chứa kết quả của từng khung hình (boxes, classes,...)
    # Vì đã để show=True nên YOLO sẽ tự mở cửa sổ cho bạn
    pass

# Đóng tất cả cửa sổ khi xong
cv2.destroyAllWindows()