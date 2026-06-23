import argparse
import sys
import threading
import time
import serial
import serial.tools.list_ports

# Cấu hình hệ thống
BAUD_RATE = 9600


def parse_args():
    parser = argparse.ArgumentParser(description='Python bridge for Arduino serial control')
    parser.add_argument('--port', default=None, help='Specify COM port manually (e.g. COM4)')
    return parser.parse_args()


def find_serial_port():
    preferred = ['COM4', 'COM5']
    available = [port.device for port in serial.tools.list_ports.comports()]
    print(f"[INFO] Ports available: {available if available else 'none'}")
    for port in preferred + available:
        try:
            test = serial.Serial(port, BAUD_RATE, timeout=0.2)
            test.close()
            return port
        except Exception:
            continue
    return preferred[0]


args = parse_args()
COM_PORT = args.port if args.port else find_serial_port()


class SerialBridge:
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.is_running = False
        self.recv_thread = None
        self.serial_lock = threading.Lock()

    def start(self):
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=0.2
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
            
        except (serial.SerialException, OSError) as e:
            print(f"[ERROR] Khong the mo cong {self.port}: {e}")
            fallback_port = find_serial_port()
            if fallback_port != self.port:
                print(f"[INFO] Thu lai cong khac: {fallback_port}")
                self.port = fallback_port
                return self.start()
            return False

    def stop(self):
        self.is_running = False
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
        print("[INFO] Da dong he thong cau noi an toan.")

    def _receive_loop(self):
        print(f"[INFO] Luong nhan du lieu tu {self.port} da khoi dong.")
        
        while self.is_running:
            try:
                if self.serial_conn and self.serial_conn.is_open:
                    with self.serial_lock:
                        if self.serial_conn.in_waiting > 0:
                            raw_data = self.serial_conn.read(self.serial_conn.in_waiting)
                            if raw_data:
                                decoded = raw_data.decode('utf-8', errors='ignore')
                                for line in decoded.splitlines():
                                    cleaned = line.strip()
                                    if cleaned:
                                        print(f"[RAW-IN] {cleaned}")
                                        self._handle_incoming_data(cleaned)
                time.sleep(0.02)
            except Exception as e:
                print(f"\n[ERROR] Mat ket noi khi doc du lieu: {e}")
                self.is_running = False
                break

    def _handle_incoming_data(self, data):
        # Xu ly du lieu cam bien
        if data.startswith("TEMP:"):
            try:
                parts = data.split('|')
                temp = float(parts[0].split(':')[1])
                humid = float(parts[1].split(':')[1])
                gas = int(parts[2].split(':')[1])
                pir = int(parts[3].split(':')[1])
                door = int(parts[4].split(':')[1])
                ac = int(parts[5].split(':')[1]) if len(parts) > 5 else 0
                person = int(parts[6].split(':')[1]) if len(parts) > 6 else 0
                
                door_status = "MO" if door == 1 else "DONG"
                ac_status = f"{ac}C" if ac > 0 else "OFF"
                
                print(f"\n[SENSOR] Temp: {temp}C | Humid: {humid}% | Gas: {gas}PPM | PIR: {pir} | Door: {door_status} | AC: {ac_status} | Person: {person}")
                print("Nhap lenh (1-7) hoac 'exit': ", end="", flush=True)
            except (IndexError, ValueError):
                pass
                
        # Xu ly su kien
        elif data.startswith("EVENT:"):
            print(f"\n[EVENT] {data}")
            if "MOTION_DETECTED" in data:
                print(" --> Phat hien chuyen dong!")
            elif "DOOR_OPENED" in data:
                print(" --> Cua bi mo!")
            elif "LED_ON" in data:
                print(" --> Da bat LED!")
            elif "LED_OFF" in data:
                print(" --> Da tat LED!")
            elif "BUZZER_ON" in data:
                print(" --> Da bat coi!")
            elif "BUZZER_OFF" in data:
                print(" --> Da tat coi!")
            elif "AC_26C" in data:
                print(" --> Dieu hoa dat 26 do C!")
            elif "AC_24C" in data:
                print(" --> Dieu hoa dat 24 do C!")
            elif "AC_OFF" in data:
                print(" --> Dieu hoa tat!")
            print("Nhap lenh (1-7) hoac 'exit': ", end="", flush=True)

    def send_command(self, cmd):
        if self.serial_conn and self.serial_conn.is_open:
            payload = (cmd + "\r\n").encode('utf-8')
            reply_lines = []

            with self.serial_lock:
                for attempt in range(3):
                    self.serial_conn.reset_input_buffer()
                    self.serial_conn.write(payload)
                    self.serial_conn.flush()

                    deadline = time.time() + 1.0
                    while time.time() < deadline:
                        if self.serial_conn.in_waiting > 0:
                            chunk = self.serial_conn.read(self.serial_conn.in_waiting)
                            if chunk:
                                decoded = chunk.decode('utf-8', errors='ignore')
                                for line in decoded.splitlines():
                                    cleaned = line.strip()
                                    if cleaned:
                                        reply_lines.append(cleaned)
                                        print(f"[RAW] {cleaned}")
                        else:
                            time.sleep(0.05)

                    if reply_lines:
                        break
                    time.sleep(0.2)

            print(f"[TX] Da gui lenh: {cmd} (bytes={payload!r})")
            if reply_lines:
                print(f"[SERIAL REPLY] {' | '.join(reply_lines)}")
            else:
                print(f"[SERIAL WARNING] Khong nhan duoc phan hoi sau khi gui '{cmd}'")
                print(f"[INFO] Neu khong co response, kiem tra lai Proteus/HEX va cong COM ({self.port})")
            return True
        return False


def main():
    print("--- [Python Two-way Bridge] Starting System ---")
    bridge = SerialBridge(port=COM_PORT, baudrate=BAUD_RATE)
    
    if not bridge.start():
        sys.exit(1)
        
    time.sleep(0.5)
    
    print("\n============================================")
    print(" HUONG DAN DIEU KHIEN MACH PROTEUS")
    print(" - '1': Bat LED bao dong")
    print(" - '2': Tat LED bao dong")
    print(" - '3': Bat Coi Hu")
    print(" - '4': Tat Coi Hu")
    print(" - '5': Dieu hoa 26 do C (1-2 nguoi)")
    print(" - '6': Dieu hoa 24 do C (3+ nguoi)")
    print(" - '7': Tat dieu hoa")
    print(" - 'exit': Thoat chuong trinh")
    print("============================================\n")
    
    try:
        while bridge.is_running:
            cmd = input().strip()
            
            if cmd.lower() == 'exit':
                break
                
            if cmd in ['1', '2', '3', '4', '5', '6', '7']:
                bridge.send_command(cmd)
            else:
                print("[INVALID] Vui long chi nhap tu 1 den 7 hoac 'exit'.")
                
    except KeyboardInterrupt:
        print("\n[INFO] Nguoi dung yeu cau dung chuong trinh.")
    finally:
        bridge.stop()


if __name__ == '__main__':
    main()