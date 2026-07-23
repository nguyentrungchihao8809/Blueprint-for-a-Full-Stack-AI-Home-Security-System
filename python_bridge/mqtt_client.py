# core/mqtt_client.py
from datetime import datetime
import json
import paho.mqtt.client as mqtt 

_global_mqtt_client = None 
shared_serial_conn = None

MQTT_BROKER = "localhost"
MQTT_PORT = 1883

# Lắng nghe các Topic lệnh từ Web Frontend gửi xuống
TOPIC_CONTROL_INTRUDER = "apartment/control/intruder"
TOPIC_CONTROL_DOOR = "apartment/control/door"

def on_connect(client, userdata, flags, rc, properties=None):
    """Callback API v2 khi kết nối thành công tới Mosquitto Broker"""
    if rc == 0:
        print("[MQTT SUCCESS] Đã kết nối thành công tới Mosquitto Broker!")
        # Đăng ký lắng nghe (Subscribe) các kênh điều khiển từ Web xuống
        client.subscribe(TOPIC_CONTROL_INTRUDER, qos=1)
        client.subscribe(TOPIC_CONTROL_DOOR, qos=1)
        print(f"[MQTT SUB] Đã đăng ký lắng nghe thành công lệnh điều khiển.")
    else:
        print(f"[MQTT ERROR] Lỗi kết nối Broker với mã phản hồi: {rc}")

def on_message(client, userdata, msg):
    """Callback API v2 xử lý gói tin điều khiển từ Web Frontend đẩy về qua Broker"""
    global shared_serial_conn
    try:
        topic = msg.topic
        payload_str = msg.payload.decode('utf-8')
        print(f"\n[MQTT INCOMING] Nhận dữ liệu điều khiển từ Topic [{topic}]: {payload_str}")
        
        # Phân rã gói dữ liệu JSON
        control_data = json.loads(payload_str)
        action = control_data.get("action")
        code_to_send = control_data.get("code") # Ví dụ: 'KF' hoặc 'OP'

        # Kiểm tra tính sẵn sàng của kết nối Serial kết nối sang mạch mô phỏng Proteus
        if not shared_serial_conn or not shared_serial_conn.is_open:
            print("[SERIAL ERROR] Cổng nối tiếp sang Proteus đang đóng. Không thể chuyển tiếp lệnh.")
            return

        # ── WORKFLOW 1: Xử lý dập còi/đèn báo trộm đột nhập ─────────────────
        if topic == TOPIC_CONTROL_INTRUDER and action == "DISARM_INTRUDER":
            if code_to_send == "KF":
                # Bắn chuỗi mã lệnh thô xuống cổng COM ảo của mạch
                shared_serial_conn.write(b"KF\n")
                print("-> [Serial Out] Đã truyền mã 'KF' xuống Proteus -> Ngắt còi báo trộm.")

        # ── WORKFLOW 3: Xử lý dập còi/đèn báo động cửa ban đêm ─────────────
        elif topic == TOPIC_CONTROL_DOOR and action == "DISARM_DOOR":
            if code_to_send == "OP":
                # Bắn chuỗi mã lệnh thô xuống cổng COM ảo của mạch
                shared_serial_conn.write(b"OP\n")
                print("-> [Serial Out] Đã truyền mã 'OP' xuống Proteus -> Ngắt còi cửa đêm.")

    except json.JSONDecodeError:
        print("[MQTT ERROR] Định dạng payload nhận được không phải là chuỗi JSON hợp lệ.")
    except Exception as e:
        print(f"[MQTT ERROR] Phát sinh lỗi ngoài dự kiến khi xử lý gói tin: {e}")

def init_mqtt(ser_connection):
    """Hàm khởi tạo kết nối MQTT chạy luồng nền (Thread)"""
    global shared_serial_conn, _global_mqtt_client
    shared_serial_conn = ser_connection 
    
    # Khởi tạo sử dụng Callback API v2 
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id="Gateway_Python_Edge")
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        print("[MQTT] Đang thiết lập cấu hình kết nối tới Broker...")
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        client.loop_start() # Chạy tiến trình ngầm không nghẽn luồng chính
        
        _global_mqtt_client = client 
        return client
    except Exception as e:
        print(f"[MQTT CRITICAL] Không thể khởi động dịch vụ MQTT: {e}")
        return None

def publish_alert_helper(topic, event_type, status, priority, message, qos=1):
    """Hàm Helper phục vụ đóng gói định dạng JSON và bắn tin báo động (Upstream) lên giao diện Web/App"""
    global _global_mqtt_client
    if _global_mqtt_client is None:
        print(f"[MQTT ERROR] Chưa khởi tạo client, không thể gửi tin tới {topic}")
        return False
        
    try:
        # Lấy mốc thời gian chuẩn quốc tế theo định dạng ISO 8601
        timestamp_iso = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        payload_data = {
            "event_type": event_type,
            "status": status,
            "priority": priority,
            "timestamp": timestamp_iso,
            "message": message
        }
        json_payload = json.dumps(payload_data, ensure_ascii=False)
        _global_mqtt_client.publish(topic, json_payload, qos=qos)
        return True
    except Exception as e:
        print(f"[MQTT ERROR] Thất bại khi gửi gói tin: {e}")
        return False