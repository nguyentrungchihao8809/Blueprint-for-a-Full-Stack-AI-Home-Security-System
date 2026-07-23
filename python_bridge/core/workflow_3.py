# core/workflow_3.py
import time
import json
from datetime import datetime

def handle_workflow_3(ser, mqtt_client):
    # B3: Service nhận tín hiệu "O" từ Proteus gửi về liền tiến hành đóng gói JSON gửi Web/App
    print("[WORKFLOW 3] Xử lý đóng gói tin và phát cảnh báo cửa mở ban đêm lên hệ thống...")
    timestamp_iso = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    
    alert_payload = {
        "event_type": "DOOR_BREACH",
        "status": "ALARM_TRIGGERED",
        "priority": "MEDIUM",
        "timestamp": timestamp_iso,
        "message": "Cảnh báo: Cửa ban đêm bị mở ngoài khung giờ cho phép (22:00 - 06:00)!"
    }
    
    topic = "apartment/alerts/security"
    try:
        if mqtt_client and mqtt_client.is_connected():
            mqtt_client.publish(topic, json.dumps(alert_payload, ensure_ascii=False), qos=1)
            print(f"[MQTT PUBLISH] Đã bắn gói tin DOOR_BREACH lên topic {topic} (QoS=1)")
    except Exception as e:
        print(f"[MQTT ERROR] Lỗi khi publish Workflow 3: {e}")