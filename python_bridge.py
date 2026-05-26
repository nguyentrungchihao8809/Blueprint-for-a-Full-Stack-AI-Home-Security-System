import sys
import threading
import time
import serial

# Cấu hình hệ thống
COM_PORT = 'COM4'
BAUD_RATE = 9600


class SerialBridge:
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.is_running = False
        self.recv_thread = None

    def start(self):
        """Khởi tạo kết nối Serial và kích hoạt luồng nhận dữ liệu ngầm."""
        try:
            self.serial_conn = serial.Serial(
                port=self.port, 
                baudrate=self.baudrate, 
                timeout=1
            )
            self.serial_conn.flushInput()
            self.serial_conn.flushOutput()
            print(f"[INFO] Ket noi thanh cong toi cong {self.port}")
            
            self.is_running = True
            self.recv_thread = threading.Thread(
                target=self._receive_loop, 
                daemon=True
            )
            self.recv_thread.start()
            return True
            
        except serial.SerialException as e:
            print(f"[ERROR] Khong the mo cong {self.port}: {e}")
            return False

    def stop(self):
        """Dừng hệ thống và giải phóng tài nguyên."""
        self.is_running = False
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
        print("[INFO] Da dong he thong cau noi an toan.")

    def _receive_loop(self):
        """Luồng chạy ngầm liên tục kiểm tra và đọc dữ liệu từ Serial."""
        print(f"[INFO] Luong nhan du lieu tu {self.port} da khoi dong.")
        
        while self.is_running:
            try:
                if self.serial_conn.in_waiting > 0:
                    raw_data = self.serial_conn.readline()
                    decoded_data = raw_data.decode('utf-8').strip()
                    
                    if decoded_data:
                        self._handle_incoming_data(decoded_data)
                        
                time.sleep(0.01)  # Giảm tải CPU nhưng vẫn đảm bảo độ nhạy
            except Exception as e:
                print(f"\n[ERROR] Mat ket noi khi doc du lieu: {e}")
                self.is_running = False
                break

    def _handle_incoming_data(self, data):
        """Phân tích và xử lý chuỗi dữ liệu nhận được."""
        # 1. Xử lý dữ liệu định kỳ từ các cảm biến
        if data.startswith("TEMP:"):
            try:
                parts = data.split('|')
                temp = float(parts[0].split(':')[1])
                humid = float(parts[1].split(':')[1])
                gas = int(parts[2].split(':')[1])
                pir = int(parts[3].split(':')[1])
                door = int(parts[4].split(':')[1])
                
                door_status = "MO" if door == 1 else "DONG"
                
                print(f"\n[SENSOR] Temp: {temp}C | Humid: {humid}% | Gas: {gas}PPM | PIR: {pir} | Door: {door_status}")
                print("Nhap lenh (1-4) hoac 'exit': ", end="", flush=True)
            except (IndexError, ValueError):
                pass  # Bỏ qua nếu chuỗi dữ liệu bị lỗi định dạng khi truyền
                
        # 2. Xử lý sự kiện khẩn cấp
        elif data.startswith("EVENT:"):
            print(f"\n[WARN_SYSTEM] {data}")
            if "MOTION_DETECTED" in data:
                print(" --> AI: Phat hien dot nhap! Kich hoat kich ban camera...")
            elif "DOOR_OPENED" in data:
                print(" --> ALERT: Cua bi cay trai phep!")
            print("Nhap lenh (1-4) hoac 'exit': ", end="", flush=True)

    def send_command(self, cmd):
        """Gửi lệnh xuống mạch ngoại vi."""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.write(cmd.encode('utf-8'))
            print(f"[TX] Da gui lenh: {cmd}")
            return True
        return False


def main():
    print("--- [Python Two-way Bridge] Starting System ---")
    bridge = SerialBridge(port=COM_PORT, baudrate=BAUD_RATE)
    
    if not bridge.start():
        sys.exit(1)
        
    time.sleep(0.5)  # Chờ luồng nhận ổn định giao diện
    
    print("\n============================================")
    print(" HUONG DAN DIEU KHIEN MACH PROTEUS")
    print(" - '1': Bat LED bao dong")
    print(" - '2': Tat LED bao dong")
    print(" - '3': Bat Coi Hu")
    print(" - '4': Tat Coi Hu")
    print(" - 'exit': Thoat chuong trinh")
    print("============================================\n")
    
    try:
        while bridge.is_running:
            cmd = input().strip()
            
            if cmd.lower() == 'exit':
                break
                
            if cmd in ['1', '2', '3', '4']:
                bridge.send_command(cmd)
            else:
                print("[INVALID] Vui long chi nhap tu 1 den 4 hoac 'exit'.")
                
    except KeyboardInterrupt:
        print("\n[INFO] Nguoi dung yeu cau dung chuong trinh.")
    finally:
        bridge.stop()


if __name__ == '__main__':
    main()