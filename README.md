[![Status: Completed](https://img.shields.io/badge/Status-Completed-brightgreen.svg)](#)
[![Language: C++](https://img.shields.io/badge/Language-C++-blue.svg)](#)
[![Language: Python](https://img.shields.io/badge/Language-Python-yellow.svg)](#)
[![Platform: Arduino](https://img.shields.io/badge/Platform-Arduino-red.svg)](#)
[![Tools: Proteus](https://img.shields.io/badge/Tools-Proteus-orange.svg)](#)

# Smart Home Security System (IoT-Based)

Dự án **Hệ thống an ninh nhà thông minh** sử dụng Arduino kết hợp giao tiếp Serial với máy tính thông qua **Python Bridge**. Hệ thống hỗ trợ giám sát môi trường (nhiệt độ, độ ẩm, khí gas) và tăng cường an ninh (phát hiện đột nhập) theo thời gian thực.

## Mục lục

1. [Tính năng hệ thống](https://www.google.com/search?q=%23-t%C3%ADnh-n%C4%83ng-h%E1%BB%87-th%E1%BB%91ng)
2. [Cấu trúc dự án](https://www.google.com/search?q=%23-c%E1%BA%A5u-tr%C3%BAc-d%E1%BB%B1-%C3%A1n)
3. [Sơ đồ nguyên lý](https://www.google.com/search?q=%23-s%C6%A1-%C4%91%E1%BB%93-nguy%C3%AAn-l%C3%BD)
4. [Hướng dẫn cài đặt](https://www.google.com/search?q=%23-h%C6%B0%E1%BB%9Bng-d%E1%BA%ABn-c%C3%A0i-%C4%91%E1%BA%B7t)
5. [Điều khiển hệ thống](https://www.google.com/search?q=%23-%C4%91i%E1%BB%81u-kh%E1%BB%9Fi-h%E1%BB%87-th%E1%BB%91ng)

---

## Tính năng hệ thống

* **Giám sát môi trường:** Đo nhiệt độ, độ ẩm qua cảm biến **DHT11** và hiển thị trên **LCD 16x2**.
* **Cảnh báo an toàn:** * Phát hiện khí **Gas** rò rỉ.
* Phát hiện chuyển động qua cảm biến **PIR**.
* Phát hiện cửa mở qua **Door Switch**.


* **Điều khiển từ xa:** Người dùng có thể điều khiển thủ công **LED** và **Còi hú** thông qua giao diện **Python Bridge** trên máy tính.

---

## Cấu trúc dự án

* `BTL.pdsprj`: File thiết kế mạch mô phỏng trên **Proteus**.
* `code C.txt`: Mã nguồn chương trình cho **Arduino (C++)**.
* `python_bridge.py`: Script **Python** trung gian giúp giao tiếp Serial với Arduino.
* `sketch_may22a.ino.hex`: File đã biên dịch dùng để nạp cho vi điều khiển trong Proteus.

---

## Sơ đồ nguyên lý

*(ảnh minh họa)*

---

## Hướng dẫn cài đặt

### 1. Phần cứng (Proteus)

1. Mở file `BTL.pdsprj` trong phần mềm **Proteus**.
2. Click đúp vào **Arduino**, tại phần **Program File**, chọn đường dẫn đến file `sketch_may22a.ino.hex`.
3. Kết nối các chân cảm biến theo sơ đồ.

### 2. Phần mềm (Python Bridge)

1. Yêu cầu cài đặt thư viện `pyserial`:
```bash
pip install pyserial

```


2. Kiểm tra cổng **COM** trong `python_bridge.py` (`COM_PORT = 'COM4'`) để đảm bảo khớp với cổng ảo trên máy tính.
3. Chạy chương trình:
```bash
python python_bridge.py

```



---

## Điều khiển hệ thống

Sau khi chạy `python_bridge.py`, bạn có thể nhập các lệnh sau vào terminal để tương tác với thiết bị:

| Lệnh | Chức năng |
| --- | --- |
| **1** | Bật đèn LED cảnh báo |
| **2** | Tắt đèn LED cảnh báo |
| **3** | Bật còi hú |
| **4** | Tắt còi hú |
| **exit** | Thoát chương trình |


