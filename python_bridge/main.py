# main.py
import serial
import time
import threading
import cv2
import paho.mqtt.client as mqtt
from ultralytics import YOLO
from config import settings
from flask import Flask, Response
import json
import os
from flask import request, jsonify

# --- IMPORT THƯ VIỆN FIREBASE ---
import firebase_admin
from firebase_admin import credentials, db

from core.workflow_1 import handle_workflow_1
from core.workflow_2 import handle_workflow_2
from core.workflow_3 import handle_workflow_3
from flask_cors import CORS

# --- ĐƯỜNG DẪN ĐẾN THƯ MỤC CONFIG ---
JSON_KEY_PATH = "config/serviceAccountKey.json"

if not os.path.exists(JSON_KEY_PATH):
    print(f"\n[FIREBASE CRITICAL ERROR] KHÔNG TÌM THẤY FILE TẠI: '{JSON_KEY_PATH}'!")
    firebase_ready = False
else:
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(JSON_KEY_PATH)
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://sentinel-edeb5-default-rtdb.asia-southeast1.firebasedatabase.app'
            })
        print("[FIREBASE] Khởi tạo kết nối Realtime Database THÀNH CÔNG!")
        firebase_ready = True
    except Exception as e:
        print(f"[FIREBASE CRITICAL] Lỗi cấu hình Firebase SDK: {e}")
        firebase_ready = False

current_detected_objects = set()
running = True

mqtt_c = mqtt.Client()
global_ser_conn = None

# --- KHỞI TẠO FLASK APP ---
app = Flask(__name__)
CORS(app)
output_frame = None
frame_lock = threading.Lock()

global_status_state = {
    "isIntruderAlarm": False,
    "isFireAlarm": False,
    "isDoorAlarm": False
}

def update_firebase_status(updates_dict):
    global global_status_state
    if not firebase_ready:
        return
    try:
        ref = db.reference('sentinel/status')
        global_status_state.update(updates_dict)
        payload = global_status_state.copy()
        payload['last_updated'] = int(time.time() * 1000)
        ref.update(payload)
        print(f"[FIREBASE PUSH] Đã đồng bộ trạng thái lên Web: {payload}")
    except Exception as e:
        print(f"[FIREBASE ERROR] Lỗi không thể update trạng thái: {e}")

def push_firebase_history(event_type, msg):
    if not firebase_ready:
        return
    try:
        ref = db.reference('sentinel/history')
        ref.push({
            "event": event_type,
            "message": msg,
            "timestamp": int(time.time() * 1000)
        })
    except Exception as e:
        print(f"[FIREBASE LOG ERROR] Lỗi ghi lịch sử: {e}")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[MQTT] Kết nối thành công Broker Mosquitto!")
        client.subscribe("apartment/control/commands")

def on_message(client, userdata, msg):
    global global_ser_conn
    try:
        payload_raw = msg.payload.decode('utf-8').strip()
        print(f"\n[MQTT RECEIVE] Nhận dữ liệu lệnh: {payload_raw}")
        data = json.loads(payload_raw)
        action = data.get("action")

        if action == "DISARM_INTRUDER":
            if global_ser_conn and global_ser_conn.is_open:
                global_ser_conn.write(b"KF\n")
                print("-> [Serial] Đã gửi lệnh 'KF' xuống Proteus tắt còi Đột nhập.")
            update_firebase_status({"isIntruderAlarm": False})
            push_firebase_history("DISARM", "Người dùng tắt báo động Đột nhập.")

        elif action == "DISARM_DOOR":
            if global_ser_conn and global_ser_conn.is_open:
                global_ser_conn.write(b"OP\n")
                print("-> [Serial] Đã gửi lệnh 'OP' xuống Proteus tắt còi Cửa đêm.")
            update_firebase_status({"isDoorAlarm": False})
            push_firebase_history("DISARM", "Người dùng tắt báo động Cửa ban đêm.")
                
    except Exception as e:
        print(f"[MQTT MESSAGE ERROR] Lỗi phân tích cú pháp lệnh: {e}")

mqtt_c.on_connect = on_connect
mqtt_c.on_message = on_message

# ── LUỒNG ĐỌC CAMERA & CHẠY YOLO ──
def global_camera_yolo_loop():
    global current_detected_objects, running, output_frame
    video_path = "tests/video_test.mp4" 
    
    print("[YOLO THREAD] Đang tải mô hình YOLOv11/YOLOv8...")
    try:
        model_wf1 = YOLO("models/yolo11n.pt")
        model_wf2 = YOLO("models/best.pt")
        print("[YOLO THREAD] Đã tải thành công các Weights mô hình AI.")
    except Exception as e:
        print(f"[YOLO CRITICAL] Không thể load file models: {e}")
        return

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[YOLO CRITICAL] Không tìm thấy video test tại đường dẫn: {video_path}")
        return

    target_labels = {'person': (0, 255, 0), 'fire': (0, 0, 255), 'smoke': (255, 0, 0)}
    print("[YOLO THREAD] Luồng nhận diện AI Core đang CHẠY NGẦM...")

    while running:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        results_wf1 = model_wf1(frame, verbose=False)
        results_wf2 = model_wf2(frame, verbose=False)
        found_this_frame = set()

        # Vẽ bounding box trực tiếp lên frame
        for r in results_wf1:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                label = model_wf1.names[cls_id]
                if label in target_labels:
                    found_this_frame.add(label)
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), target_labels[label], 2)
                    cv2.putText(frame, f"AI: {label}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, target_labels[label], 2)

        for r in results_wf2:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                label = model_wf2.names[cls_id]
                if label in target_labels:
                    found_this_frame.add(label)
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), target_labels[label], 2)
                    cv2.putText(frame, f"AI: {label}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, target_labels[label], 2)

        current_detected_objects = found_this_frame
        
        # Ghi đè frame đã xử lý vào bộ nhớ đệm luồng chung toàn cục
        with frame_lock:
            output_frame = frame.copy()

        # Hiển thị tại máy local kiểm thử
        cv2.imshow("Sentinel AI - Video Test Execution", frame)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# ── BỔ SUNG: LOGIC STREAM VIDEO QUA FLASK HTTP ──────────────────────────────
def generate_frames():
    global output_frame, frame_lock
    while running:
        with frame_lock:
            if output_frame is None:
                time.sleep(0.05)
                continue
            # Mã hóa frame thành đuôi .jpg chất lượng cao gửi đi
            ret, buffer = cv2.imencode('.jpg', output_frame)
            if not ret:
                continue
            frame_bytes = buffer.tobytes()
        
        # Đóng gói dữ liệu dạng Multipart MJPEG Stream
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.04)

@app.route('/api/control', methods=['POST'])
def web_control_api():
    try:
        data = request.get_json()
        action = data.get("action")
        code = data.get("code")  # Nhận 'KF' hoặc 'OP' từ Web gửi lên
        
        print(f"\n[HTTP API] Nhận lệnh từ giao diện Web: {action} -> Mã: {code}")
        
        global global_ser_conn
        if global_ser_conn and global_ser_conn.is_open:
            if code in ["KF", "OP"]:
                # Gửi chuỗi byte lệnh thô kèm ký tự xuống dòng qua cổng COM sang Proteus
                global_ser_conn.write(f"{code}\n".encode())
                print(f"-> [Serial Out] Đã bắn thành công mã '{code}' sang mạch Proteus.")
                
                # Cập nhật hạ trạng thái chuông trên Firebase ngay lập tức để Web tắt chớp đỏ
                if firebase_ready:
                    if code == "KF":
                        update_firebase_status({"isIntruderAlarm": False})
                    elif code == "OP":
                        update_firebase_status({"isDoorAlarm": False})
                        
                return jsonify({"status": "success", "message": f"Đã gửi {code} xuống mạch thành công"}), 200
        else:
            print("[Serial Error] Không thể gửi lệnh do cổng COM nối tiếp đang đóng!")
            return jsonify({"status": "error", "message": "Cổng nối tiếp phần cứng đang đóng"}), 500
            
    except Exception as e:
        print(f"[API ERROR] Lỗi xử lý lệnh điều khiển: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/video_feed')
def video_feed():
    """Endpoint cấp luồng dữ liệu camera thời gian thực cho Web/App"""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')



# ── LUỒNG LẮNG NGHE CHÍNH TỪ CỔNG SERIAL PROTEUS ──────────────────────────
def hardware_serial_loop():
    global global_ser_conn, running
    print("[HỆ THỐNG] Luồng lắng nghe Mạch Proteus bắt đầu chạy...")
    try:
        while running:
            if global_ser_conn and global_ser_conn.is_open and global_ser_conn.in_waiting > 0:
                raw_line = global_ser_conn.readline()
                decoded_line = raw_line.decode('utf-8', errors='ignore').strip()
                
                if not decoded_line:
                    continue

                if decoded_line == "K":
                    print(f"\n[Mạch -> Python] Nhận mã '{decoded_line}' -> Kích hoạt PIR (Workflow 1)")
                    def wf1_wrapper():
                        handle_workflow_1(global_ser_conn, lambda: current_detected_objects, mqtt_c)
                        if 'person' in current_detected_objects:
                            update_firebase_status({"isIntruderAlarm": True})
                            push_firebase_history("INTRUDER", "Cảnh báo: Phát hiện trộm đột nhập trái phép!")
                    t = threading.Thread(target=wf1_wrapper)
                    t.daemon = True
                    t.start()

                elif decoded_line == "M" or decoded_line == "N":
                    print(f"\n[Mạch -> Python] Nhận mã '{decoded_line}' -> Kích hoạt Cảnh báo cháy (Workflow 2)")
                    def wf2_wrapper():
                        handle_workflow_2(decoded_line, global_ser_conn, lambda: current_detected_objects, mqtt_c)
                        if 'fire' in current_detected_objects or 'smoke' in current_detected_objects:
                            update_firebase_status({"isFireAlarm": True})
                            push_firebase_history("FIRE", "Báo động: Phát hiện khói hoặc lửa trong căn hộ!")
                    t = threading.Thread(target=wf2_wrapper)
                    t.daemon = True
                    t.start()

                elif decoded_line == "O":
                    print(f"\n[Mạch -> Python] Nhận mã '{decoded_line}' -> Cửa mở ban đêm (Workflow 3)")
                    handle_workflow_3(global_ser_conn, mqtt_c)
                    update_firebase_status({"isDoorAlarm": True})
                    push_firebase_history("DOOR_BREACH", "Cảnh báo: Cửa ban đêm bị mở bất thường!")

            time.sleep(0.05)
    except Exception as e:
        print(f"[SERIAL LOOP ERROR] Gặp sự cố: {e}")

if __name__ == '__main__':
    # 1. Khởi chạy Camera YOLO trước độc lập
    cam_thread = threading.Thread(target=global_camera_yolo_loop)
    cam_thread.daemon = True
    cam_thread.start()

    # 2. Kết nối MQTT Broker
    try:
        mqtt_c.connect("localhost", 1883, 60)
        mqtt_c.loop_start()
    except Exception as e:
        print(f"[MQTT CRITICAL] Lỗi kết nối Broker Mosquitto: {e}")

    # 3. Đặt trạng thái ban đầu sạch sẽ cho Web
    update_firebase_status({
        "isIntruderAlarm": False,
        "isFireAlarm": False,
        "isDoorAlarm": False
    })

    # 4. Mở cổng kết nối mạch Proteus
    try:
        global_ser_conn = serial.Serial('COM2', 9600, timeout=1)
        print(f"[SERIAL] Kết nối thành công tới Proteus qua cổng COM.")
    except Exception as e:
        print(f"\n[SERIAL ERROR] Không thể mở cổng kết nối phần cứng: {e}")
        print("[HỆ THỐNG CẢNH BÁO] -> Tự động chuyển chế độ AI Emulation.\n")

    # 5. Tách luồng đọc Serial để nhường luồng chính (Main Thread) chạy Flask
    serial_thread = threading.Thread(target=hardware_serial_loop)
    serial_thread.daemon = True
    serial_thread.start()

    print("[HỆ THỐNG] Gateway trung gian IoT-AI đã sẵn sàng...")
    print("[FLASK SERVER] Đang khởi chạy máy chủ phát luồng Stream Camera tại port 5000...")

    # 6. KHỞI CHẠY SERVER STREAM TRÊN LUỒNG CHÍNH (Host 0.0.0.0 cho phép mọi thiết bị trong mạng LAN truy cập)
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n[HỆ THỐNG] Đang dừng Gateway...")
    finally:
        running = False
        mqtt_c.loop_stop()
        if global_ser_conn and global_ser_conn.is_open:
            global_ser_conn.close()