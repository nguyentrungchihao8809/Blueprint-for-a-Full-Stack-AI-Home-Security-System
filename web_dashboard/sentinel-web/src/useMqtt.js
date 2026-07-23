// src/useMqtt.js
import { ref, onUnmounted } from 'vue'
import mqtt from 'mqtt'

export function useMqttSentinel() {
  const isIntruderAlarm = ref(false)
  const isFireAlarm = ref(false)
  const isDoorAlarm = ref(false)
  const connectionStatus = ref('Đang kết nối MQTT...')

  // Kết nối tới Broker (Nếu chạy máy ảo/máy cục bộ đổi thành địa chỉ IP máy tính hoặc broker public)
  const client = mqtt.connect('ws://localhost:9001') // Lưu ý: Web sử dụng giao thức WebSocket (Port mặc định Mosquitto là 9001)

  client.on('connect', () => {
    connectionStatus.value = 'Đã kết nối Broker'
    // Đăng ký nhận toàn bộ cảnh báo căn hộ
    client.subscribe('apartment/alerts/#')
  })

  client.on('message', (topic, message) => {
    try {
      const payload = JSON.parse(message.toString())
      const eventType = payload.event_type
      const status = payload.status

      if (topic.startsWith('apartment/alerts/')) {
        if (eventType === 'INTRUDER_DETECTED') {
          isIntruderAlarm.value = (status === 'ALARM_TRIGGERED')
        } else if (eventType === 'FIRE_ALERT') {
          isFireAlarm.value = (status === 'CRITICAL')
        } else if (eventType === 'DOOR_BREACH') {
          isDoorAlarm.value = (status === 'ALARM_TRIGGERED')
        }
      }
    } catch (e) {
      console.error('Lỗi giải mã gói tin MQTT trên Web:', e)
    }
  })

  // Hàm bấm nút tắt còi từ Giao diện Web gửi xuống Python
  const sendControlCommand = (actionName) => {
    const commandPayload = {
      action: actionName,
      sender: "WEB_DASHBOARD",
      timestamp: Date.now().toString()
    }
    client.publish('apartment/control/commands', JSON.stringify(commandPayload), { qos: 1 })
  }

  onUnmounted(() => {
    if (client) client.end()
  })

  return { isIntruderAlarm, isFireAlarm, isDoorAlarm, connectionStatus, sendControlCommand }
}