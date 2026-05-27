# Blueprint-for-a-Full-Stack-AI-Home-Security-System


**Hệ thống an ninh nhà thông minh Smart Home Security System (IoT-Based)
**
**Giới thiệu:
**Dự án hệ thống an ninh nhà thông minh sử dụng Arduino kết hợp giao tiếp Serial với máy tính thông qua Python Bridge. Hệ thống giúp giám sát môi trường (nhiệt độ, độ ẩm, khí gas) và an ninh (phát hiện đột nhập) theo thời gian thực.

**Mục lục
**1. Tính năng hệ thống

2. Cấu trúc dự án

3. Sơ đồ nguyên lý

4. Hướng dẫn cài đặt

5. Điều khiển hệ thống


**1. Tính năng hệ thống
**Giám sát môi trường: Đo nhiệt độ, độ ẩm qua cảm biến DHT11 và hiển thị trên LCD 16x2.

Cảnh báo an toàn: * Phát hiện khí Gas rò rỉ (cảm biến GAS).

Phát hiện chuyển động (PIR).

Phát hiện mở cửa (Door Switch).

Điều khiển từ xa: Người dùng có thể điều khiển thủ công LED và Còi hú thông qua giao diện Python Bridge trên máy tính.


**2. Cấu trúc dự án
**BTL.pdsprj: File thiết kế mạch mô phỏng trên Proteus.

code C.txt: Mã nguồn chương trình cho Arduino (C++).

python_bridge.py: Script Python trung gian giúp giao tiếp Serial với Arduino.

sketch_may22a.ino.hex: File đã biên dịch dùng để nạp cho vi điều khiển trong Proteus.


**3. Sơ đồ nguyên lý
**(Hình ảnh mô phỏng mạch)


**4. Hướng dẫn cài đặt

**1. Phần cứng (Proteus)
Mở file BTL.pdsprj trong phần mềm Proteus.

Click đúp vào Arduino, tại phần Program File, chọn dẫn đến file sketch_may22a.ino.hex.

Kết nối các chân cảm biến theo đúng sơ đồ.

**2. Phần mềm (Python Bridge)
**Yêu cầu cài đặt thư viện pyserial:

pip install pyserial

Kiểm tra cổng COM trong python_bridge.py (COM_PORT = 'COM4') để khớp với cổng ảo trên máy tính.

Chạy chương trình:

python python_bridge.py


Điều khiển hệ thốngSau khi chạy python_bridge.py, bạn có thể nhập các lệnh sau vào terminal để tương tác với thiết bị:LệnhChức năng1Bật đèn LED cảnh báo2Tắt đèn LED cảnh báo3Bật còi hú4Tắt còi húexitThoát chương trình



