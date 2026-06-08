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
import com.example.sentinelai.data.FirebaseRepository
import com.example.sentinelai.data.SentinelStatus
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
fun LiveHomeScreen(onNavigateToLogs: () -> Unit) {
    val repo   = remember { FirebaseRepository() }
    val status by repo.observeStatus().collectAsState(initial = SentinelStatus())
    val scope  = rememberCoroutineScope()
    val isAlertActive = status.alert != "SAFE"

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
                        Text(
                            "Sentinel AI",
                            color = White,
                            fontSize = 20.sp,
                            fontWeight = FontWeight.Bold,
                            letterSpacing = (-0.5).sp
                        )
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

            // ── Banner cảnh báo ───────────────────────────────────────
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
                            "CẢNH BÁO KHẨN — ${when (status.alert) {
                                "FIRE"   -> "PHÁT HIỆN LỬA / KHÓI"
                                "PERSON" -> "PHÁT HIỆN XÂM NHẬP"
                                else     -> status.alert
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
                val streamUrl = "http://172.20.10.7:5000/video_feed"
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(200.dp)
                        .clip(RoundedCornerShape(20.dp))
                ) {
                    AndroidView(
                        factory = { ctx ->
                            android.webkit.WebView(ctx).apply {
                                settings.javaScriptEnabled = true
                                settings.loadWithOverviewMode = true
                                settings.useWideViewPort = true
                                settings.builtInZoomControls = false
                                loadUrl(streamUrl)
                            }
                        },
                        modifier = Modifier.fillMaxSize()
                    )
                    // Badge LIVE
                    Row(
                        modifier = Modifier
                            .padding(12.dp)
                            .clip(RoundedCornerShape(20.dp))
                            .background(ErrorRed)
                            .padding(horizontal = 10.dp, vertical = 5.dp)
                            .align(Alignment.TopStart),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Box(Modifier.size(5.dp).clip(CircleShape).background(White))
                        Spacer(Modifier.width(5.dp))
                        Text(
                            "LIVE", color = White, fontSize = 9.sp,
                            fontWeight = FontWeight.Bold, letterSpacing = 1.sp
                        )
                    }
                }

                Spacer(Modifier.height(16.dp))

                // ── 2 thẻ cảm biến ───────────────────────────────────
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    SensorCard(
                        modifier = Modifier.weight(1f),
                        icon = Icons.Outlined.Thermostat,
                        label = "NHIỆT ĐỘ",
                        value = "${status.temperature}°C",
                        statusText = if (status.temperature > 50) "CAO" else "ỔN ĐỊNH",
                        isWarning = status.temperature > 50,
                        progress = (status.temperature / 100.0).coerceIn(0.0, 1.0).toFloat()
                    )
                    SensorCard(
                        modifier = Modifier.weight(1f),
                        icon = Icons.Outlined.Air,
                        label = "KHÍ GAS (PPM)",
                        value = "${status.gasLevel}%",
                        statusText = if (status.gasLevel > 1.0) "NGUY HIỂM" else "AN TOÀN",
                        isWarning = status.gasLevel > 1.0,
                        progress = (status.gasLevel / 5.0).coerceIn(0.0, 1.0).toFloat()
                    )
                }

                Spacer(Modifier.height(20.dp))

                // ── Điều khiển ───────────────────────────────────────
                Text(
                    "ĐIỀU KHIỂN", color = Muted, fontSize = 10.sp,
                    fontWeight = FontWeight.Bold, letterSpacing = 2.sp
                )
                Spacer(Modifier.height(10.dp))

                ControlButton(
                    label = if (status.muted) "BẬT BÁO ĐỘNG" else "TẮT BÁO ĐỘNG",
                    icon = if (status.muted) Icons.Filled.NotificationsActive else Icons.Filled.NotificationsOff,
                    isActive = status.muted,
                    onClick = { scope.launch { repo.muteAlarm(!status.muted) } }
                )
                Spacer(Modifier.height(10.dp))

                ControlButton(
                    label = "ĐẶT LẠI CẢM BIẾN",
                    icon = Icons.Filled.Refresh,
                    isActive = false,
                    onClick = { scope.launch { repo.resetSensors() } }
                )
                Spacer(Modifier.height(10.dp))

                Button(
                    onClick = { scope.launch { repo.triggerEmergency(!status.emergency) } },
                    modifier = Modifier.fillMaxWidth().height(56.dp),
                    shape = RoundedCornerShape(16.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = if (status.emergency) ErrorRed else SoftCard,
                        contentColor   = if (status.emergency) White else Primary
                    )
                ) {
                    Icon(
                        if (status.emergency) Icons.Filled.Shield else Icons.Outlined.Shield,
                        contentDescription = null,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(Modifier.width(8.dp))
                    Text(
                        if (status.emergency) "ĐANG PHÁT KHẨN CẤP — BẤM ĐỂ TẮT"
                        else "PHÁT CẢNH BÁO KHẨN CẤP",
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