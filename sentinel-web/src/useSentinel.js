// sentinel-web/src/useSentinel.js
// Thêm vào file useSentinel.js hiện có của bạn — paste 3 hàm này vào cuối file

import { ref as vueRef, onUnmounted } from 'vue'
import { db } from './firebase.js'
import { ref as dbRef, onValue, set, push } from 'firebase/database'

// ── Đọc trạng thái realtime ──────────────────────────────────────────────────
export function useSentinelStatus() {
  const status = vueRef(null)
  const unsubscribe = onValue(dbRef(db, 'sentinel/status'), snap => {
    status.value = snap.val()
  })
  onUnmounted(unsubscribe)
  return { status }
}

// ── Đọc lịch sử sự kiện ──────────────────────────────────────────────────────
export function useSentinelHistory(limit = 20) {
  const history = vueRef([])
  const loading = vueRef(true)
  const unsubscribe = onValue(dbRef(db, 'sentinel/history'), snap => {
    const raw = snap.val()
    if (raw) {
      history.value = Object.entries(raw)
        .map(([id, val]) => ({ id, ...val }))
        .sort((a, b) => b.timestamp - a.timestamp)
        .slice(0, limit)
    }
    loading.value = false
  })
  onUnmounted(unsubscribe)
  return { history, loading }
}

// ── Điều khiển phần cứng ─────────────────────────────────────────────────────

/**
 * TẮT BÁO ĐỘNG
 * Ghi mute_alarm: true/false lên Firebase.
 * Python đọc và ngừng gửi tín hiệu 'A' xuống 8051 → còi/đèn tắt.
 */
export async function setMuteAlarm(value) {
  await set(dbRef(db, 'sentinel/commands/mute_alarm'), value)
}

/**
 * ĐẶT LẠI CẢM BIẾN
 * Ghi reset_sensors: true lên Firebase.
 * Python đọc, reset biến nhiệt độ & đếm người về 0, rồi tự xóa lệnh.
 */
export async function resetSensors() {
  await set(dbRef(db, 'sentinel/commands/reset_sensors'), true)
}

/**
 * PHÁT CẢNH BÁO KHẨN CẤP
 * Ghi emergency: true lên Firebase.
 * Python gửi tín hiệu 'F' liên tục xuống 8051 dù camera không phát hiện gì.
 * Gọi lại với false để tắt.
 */
export async function setEmergency(value) {
  await set(dbRef(db, 'sentinel/commands/emergency'), value)
}

// ── Format thời gian ─────────────────────────────────────────────────────────
export function formatTime(timestamp) {
  if (!timestamp) return '—'
  return new Date(timestamp * 1000).toLocaleString('vi-VN', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit', second: '2-digit'
  })
}