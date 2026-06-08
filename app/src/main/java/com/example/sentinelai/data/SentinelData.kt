package com.example.sentinelai.data

data class SentinelStatus(
    val temperature: Double = 0.0,
    val gasLevel: Double = 0.0,
    val alert: String = "SAFE",
    val personCount: Int = 0,
    val objectCount: Int = 0,
    val fireDetected: Boolean = false,
    val muted: Boolean = false,
    val emergency: Boolean = false,
    val timestamp: Long = 0L
)

data class SecurityLog(
    val id: String = "",
    val alert: String = "",
    val isFire: Boolean = false,
    val isIntrusion: Boolean = false,
    val tempWarning: Boolean = false,
    val temperature: Double = 0.0,
    val personCount: Int = 0,
    val objectCount: Int = 0,
    val timestamp: Long = 0L
)