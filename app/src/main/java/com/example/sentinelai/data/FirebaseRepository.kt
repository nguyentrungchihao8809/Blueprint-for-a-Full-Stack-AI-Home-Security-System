package com.example.sentinelai.data

import com.google.firebase.database.DataSnapshot
import com.google.firebase.database.DatabaseError
import com.google.firebase.database.FirebaseDatabase
import com.google.firebase.database.ValueEventListener
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow

class FirebaseRepository {
    private val db = FirebaseDatabase.getInstance(
        "https://sentinel-edeb5-default-rtdb.asia-southeast1.firebasedatabase.app"
    )
    private val statusRef   = db.getReference("sentinel/status")
    private val historyRef  = db.getReference("sentinel/history")
    private val commandsRef = db.getReference("sentinel/commands")

    fun observeStatus(): Flow<SentinelStatus> = callbackFlow {
        val listener = object : ValueEventListener {
            override fun onDataChange(snapshot: DataSnapshot) {
                trySend(SentinelStatus(
                    temperature  = snapshot.child("temperature").getValue(Double::class.java) ?: 0.0,
                    gasLevel     = snapshot.child("gas_level").getValue(Double::class.java) ?: 0.0,
                    alert        = snapshot.child("alert").getValue(String::class.java) ?: "SAFE",
                    personCount  = snapshot.child("person_count").getValue(Int::class.java) ?: 0,
                    objectCount  = snapshot.child("object_count").getValue(Int::class.java) ?: 0,
                    fireDetected = snapshot.child("fire_detected").getValue(Boolean::class.java) ?: false,
                    muted        = snapshot.child("muted").getValue(Boolean::class.java) ?: false,
                    emergency    = snapshot.child("emergency").getValue(Boolean::class.java) ?: false,
                    timestamp    = snapshot.child("timestamp").getValue(Long::class.java) ?: 0L
                ))
            }
            override fun onCancelled(error: DatabaseError) {}
        }
        statusRef.addValueEventListener(listener)
        awaitClose { statusRef.removeEventListener(listener) }
    }

    fun observeLogs(): Flow<List<SecurityLog>> = callbackFlow {
        val listener = object : ValueEventListener {
            override fun onDataChange(snapshot: DataSnapshot) {
                val logs = snapshot.children.mapNotNull { child ->
                    SecurityLog(
                        id          = child.key ?: "",
                        alert       = child.child("alert").getValue(String::class.java) ?: "",
                        isFire      = child.child("is_fire").getValue(Boolean::class.java) ?: false,
                        isIntrusion = child.child("is_intrusion").getValue(Boolean::class.java) ?: false,
                        tempWarning = child.child("temp_warning").getValue(Boolean::class.java) ?: false,
                        temperature = child.child("temperature").getValue(Double::class.java) ?: 0.0,
                        personCount = child.child("person_count").getValue(Int::class.java) ?: 0,
                        objectCount = child.child("object_count").getValue(Int::class.java) ?: 0,
                        timestamp   = child.child("timestamp").getValue(Long::class.java) ?: 0L
                    )
                }.sortedByDescending { it.timestamp }
                trySend(logs)
            }
            override fun onCancelled(error: DatabaseError) {}
        }
        // limitToLast(100) để không load hết 916 bản ghi, chỉ lấy 100 mới nhất
        historyRef.limitToLast(100).addValueEventListener(listener)
        awaitClose { historyRef.removeEventListener(listener) }
    }

    fun muteAlarm(mute: Boolean) {
        commandsRef.child("mute_alarm").setValue(mute)
    }

    fun resetSensors() {
        commandsRef.child("reset_sensors").setValue(true)
    }

    fun triggerEmergency(active: Boolean) {
        commandsRef.child("emergency").setValue(active)
    }
}