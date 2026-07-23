# config/settings.py

COM_PORT = 'COM2'
BAUD_RATE = 9600

# Định nghĩa các nhãn cần lọc từ YOLOv8 để phục vụ các Workflow
YOLO_CLASSES = {
    'person': 'person',     # Workflow 1: Đột nhập
    'fire': 'fire',         # Workflow 2: Cháy (nếu dùng model custom)
    'smoke': 'smoke'        # Workflow 2: Khói
}