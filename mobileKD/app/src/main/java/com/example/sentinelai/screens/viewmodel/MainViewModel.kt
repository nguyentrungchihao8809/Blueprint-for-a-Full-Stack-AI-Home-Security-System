package com.example.sentinelai.screens.viewmodel

import android.app.Application
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.AndroidViewModel
import com.example.sentinelai.data.SentinelMqttRepository
import org.json.JSONObject
import android.util.Log

class MainViewModel(application: Application) : AndroidViewModel(application) {

    private val mqttRepository = SentinelMqttRepository(application.applicationContext)

    // Trạng thái các luồng cảnh báo để UI lắng nghe thay đổi
    var isIntruderAlarm = mutableStateOf(false)
    var isFireAlarm = mutableStateOf(false)
    var isDoorAlarm = mutableStateOf(false)
    var systemStatus = mutableStateOf("Đang kết nối...")

    init {
        // Thiết lập lắng nghe tin nhắn đổ về từ Broker
        mqttRepository.setOnMessageListener { topic, message ->
            try {
                Log.d("MQTT_VM", "Nhận dữ liệu từ $topic: $message")

                // 1. Kiểm tra nếu là các topic cảnh báo độc lập
                if (topic.startsWith("apartment/alerts/")) {
                    val json = JSONObject(message)
                    val eventType = json.optString("event_type")
                    val status = json.optString("status")

                    when (eventType) {
                        // XỬ LÝ WORKFLOW 1: Trộm đột nhập
                        "INTRUDER_DETECTED" -> {
                            isIntruderAlarm.value = (status == "ALARM_TRIGGERED")
                        }
                        // XỬ LÝ WORKFLOW 2: Hỏa hoạn
                        "FIRE_ALERT" -> {
                            isFireAlarm.value = (status == "CRITICAL")
                        }
                        // XỬ LÝ WORKFLOW 3: Cửa đêm bị cạy
                        "DOOR_BREACH" -> {
                            isDoorAlarm.value = (status == "ALARM_TRIGGERED")
                        }
                    }
                }
            } catch (e: Exception) {
                Log.e("MQTT_VM", "Lỗi giải mã JSON: ${e.message}")
            }
        }

        // Kích hoạt kết nối mạng nội bộ
        mqttRepository.connect()
        systemStatus.value = "Đang hoạt động"
    }

    // --- CÁC NÚT ĐIỀU KHIỂN GỬI LỆNH XUỐNG PYTHON (CHIỀU VỀ) ---
    fun sendDisarmIntruderCommand() {
        // Gửi lệnh tắt còi trộm, đồng thời chủ động hạ cờ cảnh báo trên App xuống
        mqttRepository.publishCommand("DISARM_INTRUDER")
        isIntruderAlarm.value = false
    }

    fun sendDisarmDoorCommand() {
        // Gửi lệnh tắt còi cửa đêm, hạ cờ cảnh báo trên App
        mqttRepository.publishCommand("DISARM_DOOR")
        isDoorAlarm.value = false
    }

    override fun onCleared() {
        super.onCleared()
        mqttRepository.disconnect()
    }
}