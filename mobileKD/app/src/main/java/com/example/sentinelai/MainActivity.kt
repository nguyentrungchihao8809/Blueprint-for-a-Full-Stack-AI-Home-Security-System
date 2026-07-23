package com.example.sentinelai

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.runtime.*
import androidx.compose.ui.graphics.Color
import androidx.core.view.WindowCompat
import com.example.sentinelai.screens.LiveHomeScreen
import com.example.sentinelai.screens.SecurityLogsScreen
import com.example.sentinelai.ui.theme.SentinelAITheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        WindowCompat.setDecorFitsSystemWindows(window, false)
        enableEdgeToEdge()
        setContent {
            SentinelAITheme {
                SentinelApp()
            }
        }
    }
}

@Composable
fun SentinelApp() {
    var currentScreen by remember { mutableStateOf("monitor") }

    when (currentScreen) {
        "monitor" -> LiveHomeScreen(
            onNavigateToLogs = { currentScreen = "events" }
        )
        "events" -> SecurityLogsScreen(
            onNavigateToDashboard = { currentScreen = "monitor" }
        )
    }
}