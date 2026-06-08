package com.example.sentinelai.screens

import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.sentinelai.data.FirebaseRepository
import com.example.sentinelai.data.SecurityLog
import java.text.SimpleDateFormat
import java.util.*

private val PageBg    = Color(0xFFFAF9F5)
private val Primary   = Color(0xFF1C1B1B)
private val Secondary = Color(0xFF5E5F5C)
private val Muted     = Color(0xFF8C8880)
private val SoftCard  = Color(0xFFE9E8E4)
private val ErrorRed  = Color(0xFFBA1A1A)
private val White     = Color.White

@Composable
fun SecurityLogsScreen(onNavigateToDashboard: () -> Unit) {
    val repo = remember { FirebaseRepository() }
    val allLogs by repo.observeLogs().collectAsState(initial = emptyList())

    var selectedFilter by remember { mutableStateOf("TẤT CẢ") }
    val filters = listOf("TẤT CẢ", "CHÁY", "XÂM NHẬP", "AN TOÀN")

    val filteredLogs = when (selectedFilter) {
        "CHÁY"     -> allLogs.filter { it.isFire }
        "XÂM NHẬP" -> allLogs.filter { it.isIntrusion }
        "AN TOÀN"  -> allLogs.filter { !it.isFire && !it.isIntrusion && !it.tempWarning }
        else       -> allLogs
    }

    Box(modifier = Modifier.fillMaxSize().background(PageBg)) {
        Column(modifier = Modifier.fillMaxSize()) {

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
                        Icon(Icons.Filled.Security, contentDescription = null,
                            tint = White, modifier = Modifier.size(20.dp))
                        Spacer(Modifier.width(8.dp))
                        Text("Sentinel AI", color = White, fontSize = 20.sp,
                            fontWeight = FontWeight.Bold, letterSpacing = (-0.5).sp)
                    }
                    Row(
                        modifier = Modifier
                            .clip(RoundedCornerShape(20.dp))
                            .background(Color(0xFF2C2B2B))
                            .padding(horizontal = 10.dp, vertical = 5.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Box(Modifier.size(6.dp).clip(CircleShape).background(Color(0xFF4CAF50)))
                        Spacer(Modifier.width(6.dp))
                        Text("HỆ THỐNG HOẠT ĐỘNG", color = Color(0xFF4CAF50),
                            fontSize = 9.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp)
                    }
                }
            }

            // ── Danh sách ─────────────────────────────────────────────
            LazyColumn(
                modifier = Modifier.weight(1f).padding(horizontal = 20.dp),
                contentPadding = PaddingValues(top = 20.dp, bottom = 100.dp)
            ) {
                item {
                    Text("Nhật ký\nSự kiện", color = Primary, fontSize = 28.sp,
                        fontWeight = FontWeight.Bold, lineHeight = 32.sp, letterSpacing = (-0.5).sp)
                    Spacer(Modifier.height(4.dp))
                    Text("${allLogs.size} bản ghi — cập nhật realtime",
                        color = Secondary, fontSize = 14.sp)
                    Spacer(Modifier.height(16.dp))
                }

                // Bộ lọc
                item {
                    Row(
                        modifier = Modifier.horizontalScroll(rememberScrollState()),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        filters.forEach { filter ->
                            val isSelected = selectedFilter == filter
                            Box(
                                modifier = Modifier
                                    .clip(RoundedCornerShape(20.dp))
                                    .background(if (isSelected) Primary else SoftCard)
                                    .clickable { selectedFilter = filter }
                                    .padding(horizontal = 16.dp, vertical = 8.dp)
                            ) {
                                Text(filter,
                                    color = if (isSelected) White else Secondary,
                                    fontSize = 11.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp)
                            }
                        }
                    }
                    Spacer(Modifier.height(16.dp))
                }

                item {
                    Text("${filteredLogs.size} SỰ KIỆN", color = Muted, fontSize = 10.sp,
                        fontWeight = FontWeight.Bold, letterSpacing = 2.sp)
                    Spacer(Modifier.height(10.dp))
                }

                if (filteredLogs.isEmpty()) {
                    item {
                        Box(
                            modifier = Modifier.fillMaxWidth().padding(vertical = 60.dp),
                            contentAlignment = Alignment.Center
                        ) {
                            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                Icon(Icons.Outlined.Shield, contentDescription = null,
                                    tint = Color(0xFFD9D7D0), modifier = Modifier.size(48.dp))
                                Spacer(Modifier.height(10.dp))
                                Text("Không có sự kiện", color = Muted, fontSize = 14.sp,
                                    fontWeight = FontWeight.Bold)
                            }
                        }
                    }
                } else {
                    items(filteredLogs, key = { it.id }) { log ->
                        LogCard(log = log)
                        Spacer(Modifier.height(10.dp))
                    }
                }

                item {
                    Column(
                        modifier = Modifier.fillMaxWidth().padding(vertical = 20.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Icon(Icons.Outlined.Shield, contentDescription = null,
                            tint = Color(0xFFD9D7D0), modifier = Modifier.size(24.dp))
                        Spacer(Modifier.height(6.dp))
                        Text("CUỐI NHẬT KÝ", color = Muted, fontSize = 9.sp,
                            fontWeight = FontWeight.Bold, letterSpacing = 2.sp)
                    }
                }
            }
        }

        BottomNav(
            modifier = Modifier.align(Alignment.BottomCenter),
            currentScreen = "events",
            onMonitor = onNavigateToDashboard,
            onEvents = {}
        )
    }
}

@Composable
fun LogCard(log: SecurityLog) {
    // Xác định loại sự kiện từ đúng field Firebase
    val isFire      = log.isFire
    val isIntrusion = log.isIntrusion
    val isTempWarn  = log.tempWarning
    val isSafe      = !isFire && !isIntrusion && !isTempWarn

    val cardIcon: ImageVector = when {
        isFire      -> Icons.Outlined.LocalFireDepartment
        isIntrusion -> Icons.Outlined.PersonSearch
        isTempWarn  -> Icons.Outlined.Thermostat
        else        -> Icons.Outlined.Shield
    }

    val eventTitle = when {
        isFire      -> "Phát hiện lửa / khói"
        isIntrusion -> "Phát hiện xâm nhập"
        isTempWarn  -> "Nhiệt độ cao"
        else        -> "Hệ thống an toàn"
    }

    val eventDesc = buildString {
        append("Nhiệt độ: ${log.temperature}°C")
        if (log.personCount > 0) append(" · ${log.personCount} người")
        if (log.objectCount > 0) append(" · ${log.objectCount} vật thể")
    }

    val isActive = isFire || isIntrusion || isTempWarn

    val timeStr = remember(log.timestamp) {
        if (log.timestamp > 0)
            SimpleDateFormat("HH:mm:ss", Locale.getDefault()).format(Date(log.timestamp * 1000))
        else "--:--:--"
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = White),
        elevation = CardDefaults.cardElevation(0.dp)
    ) {
        Row(modifier = Modifier.padding(14.dp), verticalAlignment = Alignment.Top) {
            Box(
                modifier = Modifier
                    .size(44.dp)
                    .clip(RoundedCornerShape(12.dp))
                    .background(if (isFire) Color(0x1FBA1A1A) else SoftCard),
                contentAlignment = Alignment.Center
            ) {
                Icon(cardIcon, contentDescription = null,
                    tint = if (isFire) ErrorRed else Primary,
                    modifier = Modifier.size(20.dp))
            }

            Spacer(Modifier.width(12.dp))

            Column(modifier = Modifier.weight(1f)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(timeStr, color = Muted, fontSize = 10.sp,
                        fontWeight = FontWeight.Bold, letterSpacing = 1.sp)
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(20.dp))
                            .background(if (isActive) Color(0x1FBA1A1A) else SoftCard)
                            .padding(horizontal = 8.dp, vertical = 3.dp)
                    ) {
                        Text(
                            if (isActive) "ĐANG XỬ LÝ" else "AN TOÀN",
                            color = if (isActive) ErrorRed else Secondary,
                            fontSize = 9.sp, fontWeight = FontWeight.Bold, letterSpacing = 0.5.sp
                        )
                    }
                }
                Spacer(Modifier.height(4.dp))
                Text(eventTitle, color = Primary, fontSize = 15.sp, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(2.dp))
                Text(eventDesc, color = Secondary, fontSize = 13.sp, lineHeight = 18.sp)
            }
        }
    }
}