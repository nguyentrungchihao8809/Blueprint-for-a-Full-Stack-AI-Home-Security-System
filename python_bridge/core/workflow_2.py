# core/workflow_2.py
import time
import json
from datetime import datetime

def handle_workflow_2(source_trigger, ser, get_current_objects_func, mqtt_client=None):
    # B1: Định danh cảm biến nguồn gửi tín hiệu ('M' hoặc 'N') về service
    sensor_name = "Cảm biến Nhiệt độ DHT11" if source_trigger == "M" else "Cảm biến Khói MQ-2"
    print(f"\n[WORKFLOW 2] Tín hiệu từ {sensor_name} kích hoạt!")
    print(f"[WORKFLOW 2] Bắt đầu mở cửa sổ 30 giây để AI xác thực thực tế Khói/Lửa qua Camera...")

    start_time = time.time()
    timeout = 30  # Chờ 30 giây để AI xác thực hình ảnh
    is_confirmed = False
    detected_danger = None

    while time.time() - start_time < timeout:
        active_objects = get_current_objects_func()

        # B1: YOLO quét tìm hình ảnh khói hoặc lửa thực tế
        if 'fire' in active_objects:
            is_confirmed = True
            detected_danger = 'fire'
            break
        elif 'smoke' in active_objects:
            is_confirmed = True
            detected_danger = 'smoke'
            break

        time.sleep(0.3)

    if is_confirmed:
        print(f"\n[WORKFLOW 2 XÁC NHẬN] AI XÁC NHẬN: CÓ CHÁY THẬT! Phát hiện nhãn [{detected_danger.upper()}] trong khung hình.")
        print("[Hệ thống] -> Mạch Proteus đã tự động bật còi/đèn ở chế độ khẩn cấp tại chỗ.")
        
        # B2: Gửi tín hiệu thông báo JSON đồng bộ đến Web/App qua MQTT Broker
        if mqtt_client and mqtt_client.is_connected():
            topic = "apartment/alerts/fire"
            timestamp_iso = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            
            alert_payload = {
                "event_type": "FIRE_ALERT",
                "status": "CRITICAL",
                "priority": "CRITICAL",
                "timestamp": timestamp_iso,
                "message": f"CẢNH BÁO: Phát hiện đám cháy/khói ({detected_danger}) kích hoạt bởi {sensor_name}!"
            }
            
            mqtt_client.publish(topic, json.dumps(alert_payload, ensure_ascii=False), qos=2)
            print(f"[MQTT PUBLISH] Đã bắn gói tin FIRE_ALERT lên topic {topic} (QoS=2)")
            
    else:
        print(f"\n[WORKFLOW 2 THẤT BẠI] AI XÁC NHẬN: BÁO ĐỘNG GIẢ! Qua 30s không phát hiện hình ảnh khói hoặc lửa thực tế.")