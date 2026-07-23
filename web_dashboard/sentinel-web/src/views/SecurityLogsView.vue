<!-- sentinel-web/src/views/SecurityLogsView.vue -->
<template>
  <div class="min-h-screen bg-[#FAF9F5] text-[#1c1b1b] font-[Helvetica,Arial,sans-serif]">

    <!-- Top Nav -->
    <header class="fixed top-0 w-full z-50 bg-black/90 backdrop-blur-2xl h-20 shadow-md border-b border-white/10">
      <div class="flex justify-between items-center px-10 h-full max-w-[1728px] mx-auto">
        <div class="flex items-center gap-16">
          <span class="text-[32px] font-bold text-white tracking-tight">Sentinel AI</span>
          <nav class="flex gap-8">
            <router-link to="/" class="text-[#8C8880] hover:text-white transition-colors text-[15px]">Bảng điều khiển</router-link>
            <router-link to="/logs" class="text-white border-b-2 border-[#FF416C] pb-1 text-[15px]">Nhật ký sự kiện</router-link>
          </nav>
        </div>
        <div class="flex items-center gap-2">

          <!-- CHUÔNG THÔNG BÁO -->
          <div class="relative">
            <button
              @click="toggleNotif"
              class="w-10 h-10 flex items-center justify-center rounded-full hover:bg-white/10 transition-all text-white relative">
              <span class="material-symbols-outlined">notifications</span>
              <span v-if="unreadCount > 0"
                class="absolute top-1.5 right-1.5 w-4 h-4 bg-[#FF416C] rounded-full text-[9px] font-bold text-white flex items-center justify-center">
                {{ unreadCount > 9 ? '9+' : unreadCount }}
              </span>
            </button>

            <!-- Dropdown thông báo -->
            <div v-if="showNotif"
              class="absolute right-0 top-12 w-80 bg-[#1b1b1b] border border-white/10 rounded-2xl shadow-2xl z-50 overflow-hidden">
              <div class="flex justify-between items-center px-4 py-3 border-b border-white/10">
                <span class="text-[12px] font-bold uppercase tracking-widest text-white">Thông báo</span>
                <button @click="markAllRead" class="text-[10px] text-[#8C8880] hover:text-white uppercase tracking-wider transition-colors">
                  Đánh dấu đã đọc
                </button>
              </div>
              <div class="max-h-80 overflow-y-auto">
                <div v-if="recentAlerts.length === 0" class="px-4 py-6 text-center text-[#858383] text-sm">
                  Không có thông báo mới
                </div>
                <div v-for="item in recentAlerts" :key="item.id"
                  class="px-4 py-3 border-b border-white/5 hover:bg-white/5 transition-colors flex items-start gap-3"
                  :class="readIds.has(item.id) ? 'opacity-50' : ''">
                  <span class="text-lg mt-0.5">{{ item.alert === 'FIRE' ? '🔥' : '🚨' }}</span>
                  <div class="flex-1 min-w-0">
                    <p class="text-[12px] font-semibold text-white">
                      {{ item.alert === 'FIRE' ? 'Cảnh báo cháy' : 'Phát hiện xâm nhập' }}
                    </p>
                    <p class="text-[11px] text-[#858383] mt-0.5">{{ formatTime(item.timestamp) }}</p>
                    <p class="text-[11px] text-[#858383]">Nhiệt độ: {{ item.temperature }}°C</p>
                  </div>
                  <span v-if="!readIds.has(item.id)" class="w-2 h-2 rounded-full bg-[#FF416C] mt-1 flex-shrink-0"></span>
                </div>
              </div>
              <div class="px-4 py-3 border-t border-white/10">
                <button @click="showNotif = false" class="w-full text-[11px] text-[#858383] hover:text-white transition-colors uppercase tracking-wider">
                  Đóng
                </button>
              </div>
            </div>
          </div>

        </div>
      </div>
    </header>

    <!-- Click ngoài để đóng dropdown -->
    <div v-if="showNotif" @click="showNotif = false" class="fixed inset-0 z-40"></div>

    <main class="pt-20">
      <div class="max-w-[1728px] mx-auto px-10 py-10">

        <!-- Page Header -->
        <div class="mb-10">
          <div class="flex items-center gap-2 mb-4">
            <span class="w-2 h-2 rounded-full bg-green-500"></span>
            <span class="text-[10px] font-bold uppercase tracking-widest text-[#8C8880]">Hệ thống đang hoạt động</span>
          </div>
          <h1 class="text-[48px] font-bold tracking-tight leading-tight mb-4">Nhật ký sự kiện</h1>
          <p class="text-[15px] text-[#444748] max-w-lg leading-relaxed">
            Toàn bộ lịch sử sự kiện của hệ thống. Lọc và phân tích các sự kiện xâm nhập,
            bất thường môi trường và cập nhật trạng thái bảo mật trên tất cả các khu vực giám sát.
          </p>
        </div>

        <!-- Filters Row -->
        <div class="flex flex-wrap items-center gap-4 mb-10">
          <!-- Time filter -->
          <div class="flex bg-[#E9E8E4] rounded-full p-1">
            <button v-for="t in timeOptions" :key="t.value"
              @click="timeFilter = t.value"
              class="px-4 py-2 rounded-full text-[12px] font-semibold uppercase tracking-wider transition-all"
              :class="timeFilter === t.value ? 'bg-[#1b1b1b] text-white' : 'text-[#8C8880] hover:text-[#1c1b1b]'">
              {{ t.label }}
            </button>
          </div>
          <!-- Event type -->
          <select v-model="typeFilter"
            class="bg-white border border-[#D9D7D0] rounded-full px-5 py-2.5 text-[12px] font-semibold uppercase tracking-wider text-[#1c1b1b] outline-none cursor-pointer">
            <option value="">Loại sự kiện</option>
            <option value="FIRE">Cảnh báo cháy</option>
            <option value="PERSON">Xâm nhập</option>
            <option value="SAFE">An toàn</option>
          </select>

          <div class="ml-auto flex gap-3">
            <!-- XUẤT CSV -->
            <button
              @click="exportCSV"
              :disabled="exporting"
              class="flex items-center gap-2 bg-white border border-[#D9D7D0] rounded-full px-5 py-2.5 text-[12px] font-semibold uppercase tracking-wider text-[#1c1b1b] hover:bg-[#F0EFEB] transition-all disabled:opacity-50">
              <span class="material-symbols-outlined text-base">{{ exporting ? 'hourglass_empty' : 'download' }}</span>
              {{ exporting ? 'Đang xuất...' : 'Xuất CSV' }}
            </button>

            <!-- IN PDF -->
            <button
              @click="printPDF"
              class="flex items-center gap-2 bg-[#1b1b1b] rounded-full px-5 py-2.5 text-[12px] font-semibold uppercase tracking-wider text-white hover:bg-black transition-all">
              <span class="material-symbols-outlined text-base">print</span>
              In PDF
            </button>
          </div>
        </div>

        <!-- Table -->
        <div id="print-area" class="bg-[#1b1b1b] rounded-2xl overflow-hidden mb-10">
          <!-- Table Head -->
          <div class="grid grid-cols-[180px_1fr_1fr_120px_120px_80px] px-6 py-4 border-b border-white/10">
            <span class="text-[10px] font-bold uppercase tracking-widest text-[#8C8880]">Thời gian</span>
            <span class="text-[10px] font-bold uppercase tracking-widest text-[#8C8880]">Loại sự kiện</span>
            <span class="text-[10px] font-bold uppercase tracking-widest text-[#8C8880]">Vị trí</span>
            <span class="text-[10px] font-bold uppercase tracking-widest text-[#8C8880]">Mức độ</span>
            <span class="text-[10px] font-bold uppercase tracking-widest text-[#8C8880]">Trạng thái</span>
            <span class="text-[10px] font-bold uppercase tracking-widest text-[#8C8880]">Xem</span>
          </div>

          <!-- Loading -->
          <div v-if="loading" class="px-6 py-8 text-[#8C8880] text-sm">Đang tải dữ liệu...</div>

          <!-- Rows -->
          <div v-for="item in filteredHistory" :key="item.id"
            class="grid grid-cols-[180px_1fr_1fr_120px_120px_80px] px-6 py-5 border-b border-white/5 hover:bg-white/5 transition-colors items-center">
            <span class="text-[15px] text-[#c8c6c5]">{{ formatTime(item.timestamp) }}</span>
            <span class="flex items-center gap-2">
              <span class="text-[20px]">{{ item.alert === 'FIRE' ? '🔥' : item.alert === 'PERSON' ? '🚨' : '✅' }}</span>
              <span class="text-[12px] font-semibold uppercase tracking-wider"
                :class="item.alert === 'FIRE' ? 'text-[#f43864]' : item.alert === 'PERSON' ? 'text-orange-400' : 'text-[#858383]'">
                {{ item.alert === 'FIRE' ? 'Cảnh báo cháy' : item.alert === 'PERSON' ? 'Phát hiện xâm nhập' : 'Hệ thống an toàn' }}
              </span>
            </span>
            <span class="text-[15px] text-[#858383]">CAM-01 · {{ item.temperature }}°C</span>
            <span>
              <span class="text-[10px] font-bold uppercase px-3 py-1 rounded-full"
                :class="item.alert === 'FIRE' ? 'bg-[#f43864]/20 text-[#f43864]'
                       : item.alert === 'PERSON' ? 'bg-orange-500/20 text-orange-400'
                       : 'bg-white/10 text-[#858383]'">
                {{ item.alert === 'FIRE' ? 'Cao' : item.alert === 'PERSON' ? 'Trung bình' : 'Thấp' }}
              </span>
            </span>
            <span class="flex items-center gap-1.5">
              <span class="w-1.5 h-1.5 rounded-full"
                :class="item.alert !== 'SAFE' ? 'bg-[#f43864]' : 'bg-green-400'"></span>
              <span class="text-[15px] text-[#858383]">{{ item.alert !== 'SAFE' ? 'Đang xử lý' : 'Đã giải quyết' }}</span>
            </span>
            <button class="text-[#858383] hover:text-white transition-colors">
              <span class="material-symbols-outlined text-lg">open_in_new</span>
            </button>
          </div>

          <!-- Empty -->
          <div v-if="!loading && filteredHistory.length === 0"
            class="px-6 py-10 text-center text-[#858383] text-sm">
            Không có sự kiện nào phù hợp
          </div>

          <!-- Pagination -->
          <div class="flex justify-between items-center px-6 py-4 border-t border-white/10">
            <span class="text-[12px] text-[#858383]">Hiển thị 1–{{ filteredHistory.length }} trong tổng số {{ history.length }} sự kiện</span>
            <div class="flex items-center gap-2">
              <button class="w-8 h-8 rounded-full border border-white/10 flex items-center justify-center text-[#858383] hover:bg-white/10 transition-all">
                <span class="material-symbols-outlined text-sm">chevron_left</span>
              </button>
              <button class="w-8 h-8 rounded-full bg-white text-[#1c1b1b] flex items-center justify-center text-[12px] font-bold">1</button>
              <button class="w-8 h-8 rounded-full border border-white/10 flex items-center justify-center text-[#858383] hover:bg-white/10 transition-all text-[12px]">2</button>
              <button class="w-8 h-8 rounded-full border border-white/10 flex items-center justify-center text-[#858383] hover:bg-white/10 transition-all">
                <span class="material-symbols-outlined text-sm">chevron_right</span>
              </button>
            </div>
          </div>
        </div>

      </div>
    </main>

    <!-- Footer -->
    <footer class="w-full py-8 border-t border-[#D9D7D0] bg-[#FAF9F5]">
      <div class="flex flex-col md:flex-row justify-between items-center px-10 max-w-[1728px] mx-auto gap-4">
        <span class="text-[32px] font-semibold text-[#1c1b1b]">Sentinel AI</span>
        <span class="text-[10px] font-bold uppercase tracking-widest text-[#8C8880]">© 2024 Sentinel AI. Hệ thống giám sát Lumio Clarity.</span>
        <div class="flex gap-8">
          <a href="#" class="text-[10px] font-bold uppercase tracking-widest text-[#8C8880] hover:text-[#1c1b1b] transition-colors">Bảo mật</a>
          <a href="#" class="text-[10px] font-bold uppercase tracking-widest text-[#8C8880] hover:text-[#1c1b1b] transition-colors">Điều khoản</a>
          <a href="#" class="text-[10px] font-bold uppercase tracking-widest text-[#8C8880] hover:text-[#1c1b1b] transition-colors">Hỗ trợ</a>
        </div>
      </div>
    </footer>

    <!-- Emergency Broadcast -->
    <div class="fixed bottom-6 right-6 z-50">
      <button class="flex items-center gap-3 bg-[#1b1b1b] text-white px-6 py-4 rounded-full shadow-2xl hover:bg-black transition-all active:scale-95">
        <span class="text-[#FF416C] font-bold text-sm">SOS</span>
        <span class="text-[12px] font-semibold uppercase tracking-widest">Phát cảnh báo khẩn cấp</span>
      </button>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useSentinelHistory, formatTime } from '../useSentinel.js'

const { history, loading } = useSentinelHistory(100)
const timeFilter = ref('today')
const typeFilter = ref('')
const exporting  = ref(false)
const showNotif  = ref(false)
const readIds    = ref(new Set())

const timeOptions = [
  { value: 'today', label: 'Hôm nay' },
  { value: 'week',  label: 'Tuần này' },
  { value: 'month', label: 'Tháng này' },
]

// ── Lọc dữ liệu ─────────────────────────────────────────────────────────────
const filteredHistory = computed(() => {
  const now = Date.now() / 1000
  return history.value.filter(item => {
    if (typeFilter.value && item.alert !== typeFilter.value) return false
    if (timeFilter.value === 'today') return now - item.timestamp < 86400
    if (timeFilter.value === 'week')  return now - item.timestamp < 604800
    return true
  })
})

// ── Thông báo — chỉ FIRE và PERSON ──────────────────────────────────────────
const recentAlerts = computed(() =>
  history.value.filter(i => i.alert !== 'SAFE').slice(0, 10)
)

const unreadCount = computed(() =>
  recentAlerts.value.filter(i => !readIds.value.has(i.id)).length
)

function toggleNotif() {
  showNotif.value = !showNotif.value
}

function markAllRead() {
  recentAlerts.value.forEach(i => readIds.value.add(i.id))
  readIds.value = new Set(readIds.value)
}

// ── Xuất CSV — tạo file .csv từ filteredHistory và tải về máy ───────────────
function exportCSV() {
  if (filteredHistory.value.length === 0) return
  exporting.value = true
  try {
    const headers = ['Thời gian', 'Loại sự kiện', 'Nhiệt độ (°C)', 'Số người', 'Mức độ', 'Trạng thái']
    const rows = filteredHistory.value.map(item => [
      formatTime(item.timestamp),
      item.alert === 'FIRE'   ? 'Cảnh báo cháy'
        : item.alert === 'PERSON' ? 'Phát hiện xâm nhập'
        : 'Hệ thống an toàn',
      item.temperature,
      item.person_count ?? 0,
      item.alert === 'FIRE' ? 'Cao' : item.alert === 'PERSON' ? 'Trung bình' : 'Thấp',
      item.alert !== 'SAFE' ? 'Đang xử lý' : 'Đã giải quyết',
    ])
    const csvContent = [headers, ...rows]
      .map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
      .join('\n')
    // BOM để Excel đọc được tiếng Việt
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const url  = URL.createObjectURL(blob)
    const link = document.createElement('a')
    const date = new Date().toLocaleDateString('vi-VN').replace(/\//g, '-')
    link.href     = url
    link.download = `SentinelAI_NhatKy_${date}.csv`
    link.click()
    URL.revokeObjectURL(url)
  } finally {
    exporting.value = false
  }
}

// ── In PDF — mở hộp thoại in trình duyệt, CSS print chỉ in bảng ─────────────
function printPDF() {
  window.print()
}
</script>

<style>
@media print {
  body * { visibility: hidden; }
  #print-area, #print-area * { visibility: visible; }
  #print-area {
    position: absolute;
    top: 0; left: 0;
    width: 100%;
    background: white !important;
    color: black !important;
    border-radius: 0 !important;
  }
  #print-area span,
  #print-area div { color: black !important; }
}
</style>