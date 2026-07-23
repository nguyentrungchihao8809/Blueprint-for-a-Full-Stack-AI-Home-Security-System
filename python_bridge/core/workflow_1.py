# core/workflow_1.py
import time
import json
from datetime import datetime

def handle_workflow_1(ser, get_current_objects_func, mqtt_client=None):
    # B3: Python nhận mã 'K' và hiển thị log terminal
    print("\n[WORKFLOW 1] PIR kích hoạt! Bắt đầu mở cửa sổ 1 PHÚT (60s) để AI xác thực...")
    
    start_time = time.time()
    timeout = 60  # Đợi 60 giây theo kịch bản B4
    is_confirmed = False

    while time.time() - start_time < timeout:
        active_objects = get_current_objects_func()

        # B4: YOLO quét tìm nhãn 'person'
        if 'person' in active_objects: 
            is_confirmed = True
            break
            
        time.sleep(0.3)

    if is_confirmed:
        print("[WORKFLOW 1 XÁC NHẬN] AI đã nhìn thấy con người trong vòng 1 phút quy định! Kích hoạt Proteus.")
        # B5: Gửi lệnh 'KL' ngược về Proteus để phát còi/đèn tại chỗ
        if ser and ser.is_open:
            ser.write(b"KL\n")
            print("-> [Serial] Đã gửi lệnh 'KL' xuống Proteus thành công.")
        
        # B5: Đóng gói và gửi tín hiệu chuẩn định dạng JSON lên Web/App qua MQTT
        if mqtt_client and mqtt_client.is_connected():
            topic = "apartment/alerts/intruder"
            timestamp_iso = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            
            alert_payload = {
                "event_type": "INTRUDER_DETECTED",
                "status": "ALARM_TRIGGERED",
                "priority": "HIGH",
                "timestamp": timestamp_iso,
                "message": "Phát hiện có người xâm nhập bất hợp pháp!"
            }
            
            mqtt_client.publish(topic, json.dumps(alert_payload, ensure_ascii=False), qos=1)
            print(f"[MQTT PUBLISH] Đã bắn gói tin INTRUDER_DETECTED lên topic {topic} (QoS=1)")

    else:
        print("[WORKFLOW 1 THẤT BẠI] Đã quá 1 phút chờ đợi - Không phát hiện thực thể người nào đi qua.")