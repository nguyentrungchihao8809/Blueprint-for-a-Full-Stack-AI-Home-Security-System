// sentinel-web/src/useSentinel.js
import { ref as vueRef, onUnmounted } from 'vue'
import { db } from './firebase.js'
import { ref as dbRef, onValue } from 'firebase/database'

// ── Đọc trạng thái realtime từ Firebase ──────────────────────────────────────
export function useSentinelStatus() {
  const status = vueRef({
    temperature: '—',
    gas_ppm: '—',
    alert: 'SAFE'
  })
  
  const unsubscribe = onValue(dbRef(db, 'sentinel/status'), snap => {
    const data = snap.val()
    if (data) {
      // Áp dụng map dữ liệu từ Firebase về cấu trúc giao diện Dashboard dùng
      status.value = {
        temperature: data.temperature ?? '—',
        gas_ppm: data.gas_ppm ?? '—',
        // Ánh xạ trạng thái còi báo động từ Firebase sang nhãn giao diện
        alert: data.isFireAlarm ? 'FIRE' : (data.isIntruderAlarm ? 'KL' : (data.isDoorAlarm ? 'O' : 'SAFE'))
      }
    }
  })
  
  onUnmounted(unsubscribe)
  return { status }
}

// ── Đọc lịch sử sự kiện từ Firebase ──────────────────────────────────────────
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
    } else {
      history.value = []
    }
    loading.value = false
  })
  
  onUnmounted(unsubscribe)
  return { history, loading }
}

// ── Định dạng thời gian hiển thị ─────────────────────────────────────────────
export function formatTime(timestamp) {
  if (!timestamp) return '—'
  const date = new Date(timestamp)
  return date.toLocaleTimeString('vi-VN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// ── Gửi lệnh điều khiển trực tiếp tới Python Service thông qua HTTP API ──────
export async function sendActionToService(data) {
  try {
    const response = await fetch('http://localhost:5000/api/control', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
    
    if (!response.ok) {
      throw new Error(`Server Python phản hồi lỗi: ${response.status}`)
    }
    
    return await response.json()
  } catch (error) {
    console.error("[Web Control Error] Không thể gửi lệnh tới Python Service:", error)
    throw error
  }
}