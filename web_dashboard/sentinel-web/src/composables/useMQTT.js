// sentinel-web/src/composables/useMQTT.js
import { ref, onUnmounted } from 'vue'
import mqtt from 'mqtt' // Đảm bảo bạn đã cài: npm install mqtt

export function useMQTTSystem() {
  // Trạng thái hệ thống kết nối (Heartbeat)
  const isSystemOnline = ref(false)
  const systemUptime = ref(0)
  
  // Trạng thái cảnh báo Realtime nhận từ MQTT
  const alertStatus = ref({
    isIntruderAlarm: false,
    isFireAlarm: false,
    isDoorAlarm: false,
    message: 'Hệ thống an toàn'
  })

  // Danh sách log sự kiện nhận trực tiếp từ MQTT
  const mqttLogs = ref([])

  // Khởi tạo kết nối MQTT qua WebSockets (Mosquitto mặc định mở cổng websocket ở 9001)
  // Thay 'localhost' bằng IP của máy chạy Python/Mosquitto nếu chạy thiết bị thật
  const client = mqtt.connect('ws://localhost:9001', {
    clientId: 'sentinel_web_' + Math.random().toString(16).substr(2, 8),
    clean: true,
    connectTimeout: 4000,
    reconnectPeriod: 1000,
  })

  let heartbeatTimeout = null

  client.on('connect', () => {
    console.log('[MQTT Web] Kết nối thành công tới Broker!')
    
    // Subscribe toàn bộ luồng thông báo đi từ Python biên
    client.subscribe('apartment/alerts/+/+', { qos: 1 })
    client.subscribe('apartment/alerts/+', { qos: 1 })
    client.subscribe('apartment/status', { qos: 0 })
  })

  client.on('message', (topic, message) => {
    try {
      const payload = JSON.parse(message.toString())
      console.log(`[MQTT Receive] Topic: ${topic}`, payload)

      // 1. Xử lý giữ nhịp hệ thống (Heartbeat) từ topic: apartment/status
      if (topic === 'apartment/status') {
        isSystemOnline.value = payload.gateway_status === 'ONLINE'
        systemUptime.value = payload.uptime_seconds || 0
        
        // Cơ chế Timeout: Nếu quá 25 giây không thấy Python gửi Heartbeat -> Báo mất kết nối
        clearTimeout(heartbeatTimeout)
        heartbeatTimeout = setTimeout(() => {
          isSystemOnline.value = false
        }, 25000)
      }

      // 2. Xử lý các luồng Cảnh báo từ Python biên (Chiều đi)
      if (topic.startsWith('apartment/alerts/')) {
        // Thêm vào danh sách nhật ký hiển thị trên màn hình
        mqttLogs.value.unshift({
          id: Date.now(),
          timestamp: payload.timestamp || new Date().toISOString(),
          event_type: payload.event_type,
          priority: payload.priority,
          message: payload.message,
          status: payload.status
        })

        // Cập nhật trạng thái bật đèn/còi giao diện trực quan
        if (payload.event_type === 'INTRUDER_DETECTED') {
          alertStatus.value.isIntruderAlarm = (payload.status === 'ALARM_TRIGGERED')
          alertStatus.value.message = payload.message
        } else if (payload.event_type === 'FIRE_ALERT') {
          alertStatus.value.isFireAlarm = (payload.status === 'CRITICAL')
          alertStatus.value.message = payload.message
        } else if (payload.event_type === 'DOOR_BREACH') {
          alertStatus.value.isDoorAlarm = (payload.status === 'ALARM_TRIGGERED')
          alertStatus.value.message = payload.message
        }
      }
    } catch (e) {
      console.error('[MQTT Parse Error]', e)
    }
  })

  // 3. Hàm gửi lệnh điều khiển (Chiều về từ Web -> Python -> C Code vi điều khiển)
  const sendControlCommand = (actionName) => {
    const topic = 'apartment/control/commands'
    const commandPayload = {
      action: actionName,
      sender: 'SENTINEL_WEB_DASHBOARD',
      timestamp: new Date().toISOString()
    }
    
    client.publish(topic, JSON.stringify(commandPayload), { qos: 1 }, (err) => {
      if (err) {
        console.error(`[MQTT Publish Error] Không thể gửi lệnh ${actionName}`, err)
      } else {
        console.log(`[MQTT Publish Success] Đã bắn lệnh thành công: ${actionName} lên topic ${topic}`)
        
        // Tối ưu UI: Tạm thời tắt trạng thái cảnh báo cục bộ trên Web ngay khi bấm nút dập lệnh
        if (actionName === 'DISARM_INTRUDER') alertStatus.value.isIntruderAlarm = false
        if (actionName === 'DISARM_DOOR') alertStatus.value.isDoorAlarm = false
        if (actionName === 'DISARM_FIRE') alertStatus.value.isFireAlarm = false // Nếu có kịch bản tắt hỏa hoạn
      }
    })
  }

  // Hủy kết nối khi component bị unmount khỏi Vue
  onUnmounted(() => {
    clearTimeout(heartbeatTimeout)
    if (client) client.end()
  })

  return {
    isSystemOnline,
    systemUptime,
    alertStatus,
    mqttLogs,
    sendControlCommand
  }
}