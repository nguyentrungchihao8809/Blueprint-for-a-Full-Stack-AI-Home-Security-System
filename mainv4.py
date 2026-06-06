import cv2
from ultralytics import YOLO
import serial
import time
import os
import firebase_admin
from firebase_admin import credentials, db
from flask import Flask, Response
import threading

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# ─── CẤU HÌNH ──────────────────────────────────────────────────────────────────
FIREBASE_URL    = 'https://sentinel-edeb5-default-rtdb.asia-southeast1.firebasedatabase.app'
SERVICE_KEY     = 'serviceAccountKey.json'
SERIAL_PORT     = 'COM3'
VIDEO_SOURCE    = 'trom.mp4'
BASE_TEMP       = 30.0
TEMP_PER_OBJ    = 2.5
SEND_INTERVAL   = 0.3
GAS_THRESHOLD   = 500
TEMP_THRESHOLD  = 40.0
# ───────────────────────────────────────────────────────────────────────────────

# ─── FLASK STREAM ──────────────────────────────────────────────────────────────
flask_app    = Flask(__name__)
output_frame = None
frame_lock   = threading.Lock()

@flask_app.route('/video_feed')
def video_feed():
    def generate():
        global output_frame
        while True:
            with frame_lock:
                if output_frame is None:
                    continue
                _, buffer = cv2.imencode('.jpg', output_frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.03)
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@flask_app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

def run_flask():
    flask_app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
# ───────────────────────────────────────────────────────────────────────────────


def push_history(ref, alert_type, temperature, person_count, object_count, timestamp):
    try:
        ref.child('history').push({
            'alert':        alert_type,
            'temperature':  round(temperature, 1),
            'person_count': person_count,
            'object_count': object_count,
            'timestamp':    timestamp,
            'is_intrusion': alert_type == 'PERSON',
            'is_fire':      alert_type == 'FIRE',
            'temp_warning': temperature > TEMP_THRESHOLD,
        })
    except Exception as e:
        print(f"\n[Firebase] Lỗi ghi history: {e}")


def main():
    # ── 1. FIREBASE ──────────────────────────────────────────────────────────────
    try:
        cred = credentials.Certificate(SERVICE_KEY)
        firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_URL})
        ref = db.reference('sentinel')
        print("✅ Firebase kết nối thành công!")
    except Exception as e:
        print(f"❌ Lỗi Firebase: {e}")
        return

    # ── 2. SERIAL ────────────────────────────────────────────────────────────────
    ser = None
    try:
        ser = serial.Serial(SERIAL_PORT, 9600, timeout=1)
        print(f"✅ Serial {SERIAL_PORT} kết nối thành công!")
    except Exception:
        print("⚠️  Không tìm thấy cổng Serial — chạy không mạch cứng")

    # ── 3. MODELS ────────────────────────────────────────────────────────────────
    try:
        print("--- Đang tải model AI... ---")
        model_fire = YOLO('best.pt')
        model_base = YOLO('yolo11n.pt')
        print("✅ Tải model xong!")
    except Exception as e:
        print(f"❌ Lỗi tải model: {e}")
        return

    # ── 4. VIDEO ─────────────────────────────────────────────────────────────────
    cap = cv2.VideoCapture(VIDEO_SOURCE)
    if not cap.isOpened():
        print(f"❌ Không mở được video: {VIDEO_SOURCE}")
        return

    # ── 5. FLASK STREAM THREAD ───────────────────────────────────────────────────
    threading.Thread(target=run_flask, daemon=True).start()
    print("✅ Stream server: http://localhost:5000/video_feed")
    print("\n--- HỆ THỐNG ĐANG CHẠY — nhấn 'q' để thoát ---\n")

    last_send_time = 0
    prev_alert     = None
    global output_frame

    try:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                # Loop lại video khi hết
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            # ── Nhận diện ────────────────────────────────────────────────────
            results_b = model_base.predict(frame, classes=[0], conf=0.4, verbose=False)
            results_f = model_fire.predict(frame, conf=0.4, verbose=False)

            person_detected = False
            fire_detected   = False
            person_count    = 0
            object_count    = 0

            for r in results_b:
                for box in r.boxes:
                    person_detected = True
                    person_count   += 1
                    object_count   += 1
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, "NGUOI", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            for r in results_f:
                for box in r.boxes:
                    fire_detected = True
                    object_count += 1
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    label = model_fire.names[int(box.cls[0])].upper()
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                    cv2.putText(frame, f"!!! {label} !!!", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # ── Cập nhật frame cho stream ─────────────────────────────────────
            with frame_lock:
                output_frame = frame.copy()

            # ── Tính toán ─────────────────────────────────────────────────────
            calculated_temp = BASE_TEMP + (object_count * TEMP_PER_OBJ)

            curr_time = time.time()
            if curr_time - last_send_time > SEND_INTERVAL:

                # ── Đọc lệnh từ web dashboard ─────────────────────────────────
                cmd_ref  = ref.child('commands')
                commands = cmd_ref.get() or {}

                # 1. TẮT BÁO ĐỘNG
                # Web ghi mute_alarm: true → Python không gửi tín hiệu xuống 8051
                mute_alarm = commands.get('mute_alarm', False)

                # 2. ĐẶT LẠI CẢM BIẾN
                # Web ghi reset_sensors: true → Python reset biến đếm & nhiệt độ về 0
                if commands.get('reset_sensors', False):
                    person_count    = 0
                    fire_detected   = False
                    calculated_temp = BASE_TEMP
                    cmd_ref.child('reset_sensors').delete()  # tự xóa lệnh sau khi thực hiện
                    print("\n[CMD] Cảm biến đã đặt lại về 0")

                # 3. PHÁT CẢNH BÁO KHẨN CẤP
                # Web ghi emergency: true → Python gửi 'F' liên tục dù camera không thấy gì
                emergency = commands.get('emergency', False)

                # ── Gửi tín hiệu Serial xuống 8051 ───────────────────────────
                if not mute_alarm:
                    if emergency or fire_detected:
                        if ser and ser.is_open:
                            ser.write(b'F')
                        print(f"\r[FIRE]   {'KHẨN CẤP' if emergency else 'Lửa!'} obj={object_count} | {calculated_temp:.1f}°C", end="")
                    elif person_detected:
                        if ser and ser.is_open:
                            ser.write(b'A')
                        print(f"\r[PERSON] {person_count} người | {calculated_temp:.1f}°C", end="")
                    else:
                        print(f"\r[SAFE]   An toàn | {calculated_temp:.1f}°C", end="")
                else:
                    print(f"\r[MUTED]  Báo động tắt | {calculated_temp:.1f}°C", end="")

                # ── Xác định trạng thái alert ─────────────────────────────────
                alert = (
                    'FIRE'   if (fire_detected or emergency) else
                    'PERSON' if person_detected else
                    'SAFE'
                )

                # ── Đẩy trạng thái lên Firebase ──────────────────────────────
                ts = int(curr_time)
                try:
                    ref.child('status').update({
                        'person_count':  person_count,
                        'object_count':  object_count,
                        'fire_detected': fire_detected,
                        'temperature':   round(calculated_temp, 1),
                        'timestamp':     ts,
                        'alert':         alert,
                        'temp_warning':  calculated_temp > TEMP_THRESHOLD,
                        'muted':         mute_alarm,
                        'emergency':     emergency,
                    })
                except Exception:
                    pass

                # ── Lưu lịch sử khi trạng thái thay đổi ──────────────────────
                if alert != prev_alert:
                    push_history(ref, alert, calculated_temp, person_count, object_count, ts)
                    prev_alert = alert

                last_send_time = curr_time

            cv2.imshow("SentinelAI Monitor", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\n[System] Thoát.")
                break

    except KeyboardInterrupt:
        print("\n\n[System] Dừng Ctrl+C.")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        if ser:
            ser.close()
        print("[System] Đã đóng an toàn.")


if __name__ == '__main__':
    main()