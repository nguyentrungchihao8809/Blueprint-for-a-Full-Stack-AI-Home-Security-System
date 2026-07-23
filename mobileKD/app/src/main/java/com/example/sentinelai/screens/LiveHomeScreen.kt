package com.example.sentinelai.screens

import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.sentinelai.data.FirebaseRepository
import com.example.sentinelai.data.SentinelStatus
import com.example.sentinelai.screens.viewmodel.MainViewModel // Import MainViewModel mới
import kotlinx.coroutines.launch

private val PageBg      = Color(0xFFFAF9F5)
private val Primary     = Color(0xFF1C1B1B)
private val Secondary   = Color(0xFF5E5F5C)
private val Muted       = Color(0xFF8C8880)
private val SoftCard    = Color(0xFFE9E8E4)
private val ErrorRed    = Color(0xFFBA1A1A)
private val AccentStart = Color(0xFFFF416C)
private val AccentEnd   = Color(0xFFFF4B2B)
private val White       = Color.White

@Composable
fun LiveHomeScreen(
    onNavigateToLogs: () -> Unit,
    viewModel: MainViewModel = viewModel() // 1. Gọi nhúng MainViewModel xử lý MQTT vào đây
) {
    // Giữ lại Firebase đề phòng bạn muốn lưu lịch sử song song, nhưng trạng thái Live sẽ ưu tiên MQTT
    val repo   = remember { FirebaseRepository() }
    val firebaseStatus by repo.observeStatus().collectAsState(initial = SentinelStatus())
    val scope  = rememberCoroutineScope()

    // 2. Đọc trạng thái phản ứng thời gian thực (Realtime) từ MQTT Broker đổ về thông qua ViewModel
    val isIntruderActive by viewModel.isIntruderAlarm
    val isFireActive by viewModel.isFireAlarm
    val isDoorActive by viewModel.isDoorAlarm
    val MQTT_SystemStatus by viewModel.systemStatus

    // Hệ thống kích hoạt cảnh báo chung nếu 1 trong các luồng trộm, cháy, cửa bị kích hoạt
    val isAlertActive = isIntruderActive || isFireActive || isDoorActive

    Box(modifier = Modifier.fillMaxSize().background(PageBg)) {

        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(bottom = 80.dp)
        ) {

            // ── Header ───────────────────────────────────────────────
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(Primary)
                    .statusBarsPadding()
                    .padding(horizontal = 20.dp, vertical = 14.dp)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            Icons.Filled.Security,
                            contentDescription = null,
                            tint = White,
                            modifier = Modifier.size(20.dp)
                        )
                        Spacer(Modifier.width(8.dp))
                        Column {
                            Text(
                                "Sentinel AI",
                                color = White,
                                fontSize = 20.sp,
                                fontWeight = FontWeight.Bold,
                                letterSpacing = (-0.5).sp
                            )
                            // Hiển thị trạng thái Heartbeat kết nối sống chết của Python
                            Text(
                                "MQTT: $MQTT_SystemStatus",
                                color = if (MQTT_SystemStatus == "Đang hoạt động") Color(0xFF4CAF50) else Muted,
                                fontSize = 10.sp
                            )
                        }
                    }
                    Row(
                        modifier = Modifier
                            .clip(RoundedCornerShape(20.dp))
                            .background(Color(0xFF2C2B2B))
                            .padding(horizontal = 10.dp, vertical = 5.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Box(
                            modifier = Modifier
                                .size(6.dp)
                                .clip(CircleShape)
                                .background(if (isAlertActive) ErrorRed else Color(0xFF4CAF50))
                        )
                        Spacer(Modifier.width(6.dp))
                        Text(
                            if (isAlertActive) "CẢNH BÁO" else "AN TOÀN",
                            color = if (isAlertActive) ErrorRed else Color(0xFF4CAF50),
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold,
                            letterSpacing = 1.sp
                        )
                    }
                }
            }

            // ── Banner cảnh báo động từ mạng MQTT ───────────────────────────────────────
            if (isAlertActive) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(Brush.horizontalGradient(listOf(AccentStart, AccentEnd)))
                        .padding(horizontal = 20.dp, vertical = 10.dp)
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            Icons.Filled.Warning, contentDescription = null,
                            tint = White, modifier = Modifier.size(14.dp)
                        )
                        Spacer(Modifier.width(6.dp))
                        Text(
                            "CẢNH BÁO KHẨN — ${when {
                                isFireActive -> "PHÁT HIỆN LỬA / KHÓI (AI)"
                                isIntruderActive -> "PHÁT HIỆN XÂM NHẬP (AI)"
                                isDoorActive -> "VI PHẠM CỬA BAN ĐÊM"
                                else -> "SỰ CỐ CHƯA XÁC ĐỊNH"
                            }}",
                            color = White, fontSize = 11.sp,
                            fontWeight = FontWeight.Bold, letterSpacing = 1.sp
                        )
                    }
                }
            }

            // ── Body ─────────────────────────────────────────────────
            Column(modifier = Modifier.padding(horizontal = 20.dp, vertical = 20.dp)) {

                Text(
                    "Trung tâm\nGiám sát",
                    color = Primary, fontSize = 28.sp,
                    fontWeight = FontWeight.Bold,
                    lineHeight = 32.sp, letterSpacing = (-0.5).sp
                )
                Spacer(Modifier.height(4.dp))
                Text(
                    if (isAlertActive) "Hệ thống đang có cảnh báo — kiểm tra ngay!"
                    else "Tất cả điểm ra vào được bảo vệ.",
                    color = Secondary, fontSize = 14.sp
                )

                Spacer(Modifier.height(20.dp))

                // ── Camera WebView ────────────────────────────────────
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(200.dp)
                        .clip(RoundedCornerShape(20.dp))
                ) {
                    // ĐÃ SỬA: Thêm chữ 'A' thành AndroidView và bọc đóng mở ngoặc chuẩn xác
                    AndroidView(
                        factory = { context ->
                            android.webkit.WebView(context).apply {
                                layoutParams = android.view.ViewGroup.LayoutParams(
                                    android.view.ViewGroup.LayoutParams.MATCH_PARENT,
                                    android.view.ViewGroup.LayoutParams.MATCH_PARENT
                                )

                                // Cấu hình tối ưu WebView
                                settings.javaScriptEnabled = true
                                settings.loadWithOverviewMode = true
                                settings.useWideViewPort = true

                                isHorizontalScrollBarEnabled = false
                                isVerticalScrollBarEnabled = false
                                settings.setSupportZoom(false)

                                // 1. Sử dụng chính xác IP cấu hình mạng trong MqttRepository của bạn
                                val cameraUrl = "http://172.20.10.6:5000/video_feed"

                                // 2. Bọc link stream vào ảnh HTML tránh lỗi WebView kén render nhị phân trực tiếp
                                val htmlData = """
                                    <html>
                                    <head>
                                        <style>
                                            html, body { margin: 0; padding: 0; background: #000000; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; }
                                            img { width: 100%; height: 100%; object-fit: contain; }
                                        </style>
                                    </head>
                                    <body>
                                        <img src="$cameraUrl" />
                                    </body>
                                    </html>
                                """.trimIndent()

                                // 3. Tiến hành render
                                loadDataWithBaseURL(null, htmlData, "text/html", "UTF-8", null)
                            }
                        },
                        modifier = Modifier.fillMaxSize()
                    )
                }

                Spacer(Modifier.height(16.dp))

                // ── 2 thẻ cảm biến (Đọc đồng bộ song song từ Firebase/Mạch về) ───────────────────────────────────
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    SensorCard(
                        modifier = Modifier.weight(1f),
                        icon = Icons.Outlined.Thermostat,
                        label = "NHIỆT ĐỘ",
                        value = "${firebaseStatus.temperature}°C",
                        statusText = if (firebaseStatus.temperature > 45 || isFireActive) "CAO/CHÁY" else "ỔN ĐỊNH",
                        isWarning = firebaseStatus.temperature > 45 || isFireActive,
                        progress = (firebaseStatus.temperature / 100.0).coerceIn(0.0, 1.0).toFloat()
                    )
                    SensorCard(
                        modifier = Modifier.weight(1f),
                        icon = Icons.Outlined.Air,
                        label = "KHÍ GAS (PPM)",
                        value = "${firebaseStatus.gasLevel}%",
                        statusText = if (firebaseStatus.gasLevel > 1.0) "NGUY HIỂM" else "AN TOÀN",
                        isWarning = firebaseStatus.gasLevel > 1.0,
                        progress = (firebaseStatus.gasLevel / 5.0).coerceIn(0.0, 1.0).toFloat()
                    )
                }

                Spacer(Modifier.height(20.dp))

                // ── BỘ ĐIỀU KHIỂN CHUYỂN QUA MQTT ───────────────────────────────────────
                Text(
                    "ĐIỀU KHIỂN QUA MQTT", color = Muted, fontSize = 10.sp,
                    fontWeight = FontWeight.Bold, letterSpacing = 2.sp
                )
                Spacer(Modifier.height(10.dp))

                // Nút điều khiển Tắt/Mở luồng báo động trộm bất đồng bộ
                ControlButton(
                    label = if (isIntruderActive) "TẮT CÒI BÁO TRỘM" else "HỆ THỐNG TRỘM SẴN SÀNG",
                    icon = if (isIntruderActive) Icons.Filled.NotificationsOff else Icons.Filled.NotificationsActive,
                    isActive = isIntruderActive,
                    onClick = { viewModel.sendDisarmIntruderCommand() } // Gọi lệnh MQTT bắn chuỗi "DISARM_INTRUDER"
                )
                Spacer(Modifier.height(10.dp))

                // Nút điều khiển Tắt/Mở luồng báo động vi phạm cửa đêm bất đồng bộ
                ControlButton(
                    label = if (isDoorActive) "TẮT CÒI CỬA BAN ĐÊM" else "CỬA BAN ĐÊM AN TOÀN",
                    icon = if (isDoorActive) Icons.Filled.NoEncryptionGmailerrorred else Icons.Filled.Lock,
                    isActive = isDoorActive,
                    onClick = { viewModel.sendDisarmDoorCommand() } // Gọi lệnh MQTT bắn chuỗi "DISARM_DOOR"
                )
                Spacer(Modifier.height(10.dp))

                // Giữ lại nút khẩn cấp Firebase của bạn cũ nếu cần kích hoạt thủ công mạng ngoài
                Button(
                    onClick = { scope.launch { repo.triggerEmergency(!firebaseStatus.emergency) } },
                    modifier = Modifier.fillMaxWidth().height(56.dp),
                    shape = RoundedCornerShape(16.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = if (firebaseStatus.emergency) ErrorRed else SoftCard,
                        contentColor   = if (firebaseStatus.emergency) White else Primary
                    )
                ) {
                    Icon(
                        if (firebaseStatus.emergency) Icons.Filled.Shield else Icons.Outlined.Shield,
                        contentDescription = null,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(Modifier.width(8.dp))
                    Text(
                        if (firebaseStatus.emergency) "ĐANG PHÁT KHẨN CẤP — BẤM ĐỂ TẮT"
                        else "PHÁT CẢNH BÁO KHẨN CẤP FIREGBASE",
                        fontSize = 12.sp, fontWeight = FontWeight.Bold, letterSpacing = 0.5.sp
                    )
                }

                Spacer(Modifier.height(8.dp))
            }
        }

        BottomNav(
            modifier = Modifier.align(Alignment.BottomCenter),
            currentScreen = "monitor",
            onMonitor = {},
            onEvents = onNavigateToLogs
        )
    }
}

// ───────────────────────────────────────────────────────────────────────
// DÁN TOÀN BỘ ĐOẠN NÀY VÀO DƯỚI CÙNG FILE LiveHomeScreen.kt CỦA BẠN
// ───────────────────────────────────────────────────────────────────────

@Composable
fun SensorCard(
    modifier: Modifier = Modifier,
    icon: ImageVector,
    label: String,
    value: String,
    statusText: String,
    isWarning: Boolean,
    progress: Float
) {
    Card(
        modifier = modifier,
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = White),
        elevation = CardDefaults.cardElevation(0.dp)
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier
                        .size(32.dp)
                        .clip(RoundedCornerShape(10.dp))
                        .background(SoftCard),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(icon, contentDescription = null,
                        tint = Primary, modifier = Modifier.size(16.dp))
                }
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(20.dp))
                        .background(if (isWarning) Color(0x1FBA1A1A) else Color(0xFFEBEBE8))
                        .padding(horizontal = 8.dp, vertical = 3.dp)
                ) {
                    Text(
                        statusText,
                        color = if (isWarning) ErrorRed else Secondary,
                        fontSize = 9.sp, fontWeight = FontWeight.Bold, letterSpacing = 0.5.sp
                    )
                }
            }
            Spacer(Modifier.height(10.dp))
            Text(label, color = Muted, fontSize = 9.sp,
                fontWeight = FontWeight.Bold, letterSpacing = 1.5.sp)
            Spacer(Modifier.height(2.dp))
            Text(value, color = Primary, fontSize = 22.sp,
                fontWeight = FontWeight.Bold, letterSpacing = (-0.5).sp)
            Spacer(Modifier.height(8.dp))
            LinearProgressIndicator(
                progress = { progress },
                modifier = Modifier.fillMaxWidth().height(3.dp).clip(RoundedCornerShape(2.dp)),
                color = if (isWarning) ErrorRed else Primary,
                trackColor = SoftCard
            )
        }
    }
}

@Composable
fun ControlButton(
    label: String,
    icon: ImageVector,
    isActive: Boolean,
    onClick: () -> Unit
) {
    Button(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth().height(52.dp),
        shape = RoundedCornerShape(14.dp),
        colors = ButtonDefaults.buttonColors(
            containerColor = if (isActive) Primary else SoftCard,
            contentColor   = if (isActive) White else Primary
        ),
        elevation = ButtonDefaults.buttonElevation(0.dp)
    ) {
        Icon(icon, contentDescription = null, modifier = Modifier.size(16.dp))
        Spacer(Modifier.width(8.dp))
        Text(label, fontSize = 12.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp)
    }
}

@Composable
fun BottomNav(
    modifier: Modifier = Modifier,
    currentScreen: String,
    onMonitor: () -> Unit,
    onEvents: () -> Unit
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(topStart = 20.dp, topEnd = 20.dp))
            .background(Primary)
            .navigationBarsPadding()
            .padding(horizontal = 40.dp, vertical = 14.dp),
        horizontalArrangement = Arrangement.SpaceAround
    ) {
        NavItem(
            icon = Icons.Outlined.Visibility,
            iconFilled = Icons.Filled.Visibility,
            label = "MONITOR",
            isActive = currentScreen == "monitor",
            onClick = onMonitor
        )
        NavItem(
            icon = Icons.Outlined.History,
            iconFilled = Icons.Filled.History,
            label = "EVENTS",
            isActive = currentScreen == "events",
            onClick = onEvents
        )
    }
}

@Composable
fun NavItem(
    icon: ImageVector,
    iconFilled: ImageVector,
    label: String,
    isActive: Boolean,
    onClick: () -> Unit
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = Modifier
            .clip(RoundedCornerShape(12.dp))
            .clickable(onClick = onClick)
            .padding(horizontal = 20.dp, vertical = 6.dp)
    ) {
        Icon(
            if (isActive) iconFilled else icon,
            contentDescription = label,
            tint = if (isActive) White else Color(0xFF858383),
            modifier = Modifier.size(22.dp)
        )
        Spacer(Modifier.height(3.dp))
        Text(
            label,
            color = if (isActive) White else Color(0xFF858383),
            fontSize = 9.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.5.sp
        )
    }
}