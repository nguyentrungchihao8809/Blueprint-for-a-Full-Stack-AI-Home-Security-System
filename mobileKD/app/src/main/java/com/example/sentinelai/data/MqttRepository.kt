package com.example.sentinelai.data // <-- ĐÃ SỬA CHÍNH XÁC THEO DỰ ÁN CỦA BẠN

import android.content.Context
import android.util.Log
import org.eclipse.paho.client.mqttv3.*
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence
import java.util.UUID

class SentinelMqttRepository(private val context: Context) {

    private val TAG = "MqttRepository"

    // --- CẤU HÌNH THÔNG SỐ MQTT ---
    // Thay đổi IP này thành IP máy tính chạy Mosquitto của bạn (Xem bằng lệnh ipconfig)
    private val IP_MAY_TINH = "10.0.2.2"
    private val BROKER_URL = "tcp://$IP_MAY_TINH:1883"
    private val CLIENT_ID = "Android_App_" + UUID.randomUUID().toString().substring(0, 5)

    private val TOPIC_ALERTS = "apartment/alerts/#"
    private val TOPIC_CONTROL = "apartment/control/commands"

    private var mqttClient: MqttClient? = null
    private var messageListener: ((topic: String, message: String) -> Unit)? = null

    fun setOnMessageListener(listener: (topic: String, message: String) -> Unit) {
        this.messageListener = listener
    }

    fun connect() {
        if (mqttClient?.isConnected == true) return

        try {
            mqttClient = MqttClient(BROKER_URL, CLIENT_ID, MemoryPersistence())

            val options = MqttConnectOptions().apply {
                isCleanSession = true
                keepAliveInterval = 60
                connectionTimeout = 10
                isAutomaticReconnect = true
            }

            mqttClient?.setCallback(object : MqttCallback {
                override fun connectionLost(cause: Throwable?) {
                    Log.w(TAG, "Mất kết nối với MQTT Broker: ${cause?.message}")
                }

                override fun messageArrived(topic: String?, message: MqttMessage?) {
                    val payload = message?.payload?.let { String(it) } ?: ""
                    Log.d(TAG, "Nhận tin nhắn mới từ Topic [$topic]: $payload")
                    topic?.let { messageListener?.invoke(it, payload) }
                }

                override fun deliveryComplete(token: IMqttDeliveryToken?) {}
            })

            Log.d(TAG, "Đang kết nối tới Broker: $BROKER_URL ...")
            mqttClient?.connect(options)
            Log.i(TAG, "Kết nối MQTT THÀNH CÔNG!")

            subscribeToAlerts()

        } catch (e: MqttException) {
            Log.e(TAG, "Lỗi khi kết nối MQTT: ${e.message}")
            e.printStackTrace()
        }
    }

    private fun subscribeToAlerts() {
        try {
            mqttClient?.subscribe(TOPIC_ALERTS, 1)
            Log.i(TAG, "Đã Subscribe thành công vào topic: $TOPIC_ALERTS")
        } catch (e: MqttException) {
            Log.e(TAG, "Lỗi khi Subscribe: ${e.message}")
        }
    }

    fun publishCommand(action: String) {
        if (mqttClient?.isConnected != true) {
            Log.w(TAG, "Chưa kết nối MQTT, không thể gửi lệnh!")
            return
        }

        try {
            val jsonPayload = """
                {
                    "action": "$action",
                    "sender": "MOBILE_APP",
                    "timestamp": "${System.currentTimeMillis()}"
                }
            """.trimIndent()

            val message = MqttMessage(jsonPayload.toByteArray()).apply {
                qos = 1
            }

            Log.d(TAG, "Đang gửi lệnh tới [$TOPIC_CONTROL]: $jsonPayload")
            mqttClient?.publish(TOPIC_CONTROL, message)
            Log.i(TAG, "Gửi lệnh $action THÀNH CÔNG!")

        } catch (e: Exception) {
            Log.e(TAG, "Lỗi khi gửi tin nhắn MQTT: ${e.message}")
        }
    }

    fun disconnect() {
        try {
            if (mqttClient?.isConnected == true) {
                mqttClient?.disconnect()
                Log.i(TAG, "Đã ngắt kết nối MQTT an toàn.")
            }
        } catch (e: MqttException) {
            Log.e(TAG, "Lỗi khi ngắt kết nối MQTT: ${e.message}")
        }
    }
}