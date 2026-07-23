<template>
  <div class="min-h-screen bg-[#FAF9F5] text-[#1c1b1b] font-[Helvetica,Arial,sans-serif]">

    <header class="fixed top-0 w-full z-50 bg-black/90 backdrop-blur-2xl h-20 shadow-md border-b border-white/10">
      <div class="flex justify-between items-center px-10 h-full max-w-[1728px] mx-auto">
        <div class="flex items-center gap-16">
          <span class="text-[32px] font-bold text-white tracking-tight">Sentinel AI</span>
          <nav class="flex gap-8">
            <router-link to="/" class="text-white border-b-2 border-[#FF416C] pb-1 text-[15px]">Bảng điều khiển</router-link>
            <router-link to="/logs" class="text-[#8C8880] hover:text-white transition-colors text-[15px]">Nhật ký sự kiện</router-link>
          </nav>
        </div>
        <div class="flex items-center gap-4">
          <button class="w-10 h-10 flex items-center justify-center rounded-full hover:bg-white/10 transition-all text-white">
            <span class="material-symbols-outlined">notifications</span>
          </button>
          <button class="w-10 h-10 flex items-center justify-center rounded-full hover:bg-white/10 transition-all text-white">
            <span class="material-symbols-outlined">settings</span>
          </button>
          <div class="w-10 h-10 rounded-full bg-white/20 border border-white/20 flex items-center justify-center text-white font-bold">A</div>
        </div>
      </div>
    </header>

    <main class="pt-20">
      <section v-if="hasActiveAlert" class="w-full bg-red-100/60 border-b border-red-200/50 py-2 overflow-hidden whitespace-nowrap">
        <div class="inline-block animate-marquee">
          <span v-for="n in 3" :key="n" class="inline-flex items-center gap-2 mr-32 text-[#ba1a1a] text-[12px] font-semibold uppercase tracking-widest">
            <span class="material-symbols-outlined text-sm animate-bounce">warning</span>
            CẢNH BÁO HỆ THỐNG: {{ currentAlertMessage }} — GIÁM SÁT REALTIME VIA PYTHON MULTI-WORKFLOW
          </span>
        </div>
      </section>

      <div class="max-w-[1728px] mx-auto px-10 py-8 space-y-8">

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

          <div class="lg:col-span-8 relative rounded-2xl overflow-hidden glass-card group">
            <img
              src="http://localhost:5000/video_feed"
              class="w-full h-[540px] object-cover"
              alt="YOLO Live Stream"
              @error="streamError = true"
              v-if="!streamError"
            />
            <div v-if="streamError" class="w-full h-[540px] bg-[#1a1a1a] flex items-center justify-center">
              <div class="text-center text-white/30">
                <span class="material-symbols-outlined text-6xl">videocam_off</span>
                <p class="text-xs uppercase tracking-widest mt-2">Camera AI Offline</p>
                <p class="text-xs text-white/20 mt-1">Vui lòng khởi chạy Python Gateway Service để lấy luồng Video</p>
              </div>
            </div>
            
            <div class="absolute inset-0 pointer-events-none"
              style="background-image: radial-gradient(circle, rgba(255,255,255,0.05) 1px, transparent 1px); background-size: 30px 30px;"></div>
            
            <div class="absolute top-4 left-4 flex items-center gap-2">
              <span class="w-2 h-2 rounded-full animate-pulse" :class="streamError ? 'bg-gray-500' : 'bg-red-500'"></span>
              <span class="text-white text-[10px] uppercase bg-black/50 px-2 py-1 rounded tracking-widest font-bold">
                {{ streamError ? 'CAM OFFLINE' : 'YOLOv8 Edge Monitoring: LIVE' }}
              </span>
            </div>

            <div v-if="status?.alert === 'KL' || status?.alert === 'FIRE'" class="absolute inset-0 border-4 border-red-500/60 rounded-2xl pointer-events-none animate-pulse"></div>
            <div v-if="status?.alert === 'O'" class="absolute inset-0 border-4 border-orange-500/60 rounded-2xl pointer-events-none animate-pulse"></div>

            <div class="absolute bottom-4 right-4">
              <div class="flex items-center gap-2 bg-black/40 backdrop-blur-md px-3 py-2 rounded-full border border-white/20">
                <span class="material-symbols-outlined text-white text-lg">psychology</span>
                <span class="text-white text-[12px] font-semibold uppercase">AI Processing Gateway</span>
              </div>
            </div>
          </div>

          <div class="lg:col-span-4 flex flex-col gap-6">

            <div class="glass-card p-4 rounded-2xl flex flex-col justify-between h-[150px]">
              <div class="flex justify-between items-start">
                <div>
                  <span class="text-[#8C8880] text-[12px] font-semibold uppercase tracking-widest">Nhiệt độ (DHT11)</span>
                  <h3 class="text-[32px] font-semibold mt-1 leading-none"
                    :class="Number(status?.temperature) > 45 ? 'text-[#ba1a1a] font-bold animate-pulse' : 'text-[#1c1b1b]'">
                    {{ status?.temperature ?? '—' }}°C
                  </h3>
                  <p v-if="Number(status?.temperature) > 45" class="text-[11px] text-red-600 font-medium mt-1 uppercase tracking-tight">HỎA HOẠN: Vượt ngưỡng nguy hiểm (>45°C)</p>
                </div>
                <span class="material-symbols-outlined" :class="Number(status?.temperature) > 45 ? 'text-red-600' : 'text-[#1c1b1b]'">thermostat</span>
              </div>
              <div class="w-full h-6 relative">
                <div class="w-full h-px bg-[#D9D7D0]/30 relative">
                  <div class="absolute bottom-0 left-0 w-full h-[25px]"
                    style="background: linear-gradient(90deg, transparent 0%, #FF416C 50%, transparent 100%);
                           clip-path: polygon(0 80%, 20% 70%, 40% 90%, 60% 40%, 80% 60%, 100% 50%, 100% 100%, 0 100%);"></div>
                </div>
              </div>
            </div>

            <div class="glass-card p-4 rounded-2xl flex flex-col justify-between h-[150px]">
              <div class="flex justify-between items-start">
                <div>
                  <span class="text-[#8C8880] text-[12px] font-semibold uppercase tracking-widest">Nồng độ khói khí ga (MQ-2)</span>
                  <h3 class="text-[32px] font-semibold mt-1 leading-none"
                    :class="Number(status?.gas_ppm) > 300 ? 'text-[#ba1a1a] font-bold animate-pulse' : 'text-[#1c1b1b]'">
                    {{ status?.gas_ppm ?? '—' }} PPM
                  </h3>
                  <p v-if="Number(status?.gas_ppm) > 300" class="text-[11px] text-red-600 font-medium mt-1 uppercase tracking-tight">Phát hiện khí độc / Khói (>300ppm)</p>
                </div>
                <span class="material-symbols-outlined" :class="Number(status?.gas_ppm) > 300 ? 'text-red-600' : 'text-[#1c1b1b]'">gas_meter</span>
              </div>
              <div class="w-full h-6 relative">
                <div class="w-full h-px bg-[#D9D7D0]/30 relative">
                  <div class="absolute bottom-0 left-0 w-full h-[20px]"
                    style="background: linear-gradient(90deg, transparent 0%, #000 50%, transparent 100%);
                           clip-path: polygon(0 90%, 20% 85%, 40% 92%, 60% 88%, 80% 91%, 100% 89%, 100% 100%, 0 100%);"></div>
                </div>
              </div>
            </div>

            <div class="bg-[#1b1b1b] p-5 rounded-2xl flex flex-col gap-4 mt-auto shadow-xl">
              <span class="text-[#858383] text-[11px] font-bold uppercase tracking-widest block border-b border-white/5 pb-2">ĐIỀU KHIỂN HỆ THỐNG PHẦN CỨNG</span>
              
              <div class="flex flex-col gap-3">
                
                <button
                  @click="handleDisarmIntruder"
                  :disabled="cmdLoading.intruder || status?.alert !== 'KL'"
                  class="w-full flex items-center justify-between px-4 py-3.5 rounded-xl border transition-all active:scale-[0.98]"
                  :class="status?.alert === 'KL' 
                    ? 'bg-red-600 border-red-500 text-white hover:bg-red-700 font-bold animate-pulse' 
                    : 'border-white/10 bg-white/5 text-white/40 cursor-not-allowed'">
                  <div class="flex items-center gap-3">
                    <span class="material-symbols-outlined text-[22px]">
                      {{ cmdLoading.intruder ? 'progress_activity' : 'gpp_bad' }}
                    </span>
                    <div class="text-left">
                      <p class="text-[12px] uppercase tracking-wider">Tắt chuông báo trộm</p>
                      <p class="text-[10px] text-white/60 font-normal">Gửi mã sự kiện "KF" về Proteus</p>
                    </div>
                  </div>
                  <span class="material-symbols-outlined text-sm">chevron_right</span>
                </button>

                <button
                  @click="handleDisarmDoor"
                  :disabled="cmdLoading.door || status?.alert !== 'O'"
                  class="w-full flex items-center justify-between px-4 py-3.5 rounded-xl border transition-all active:scale-[0.98]"
                  :class="status?.alert === 'O' 
                    ? 'bg-orange-500 border-orange-400 text-white hover:bg-orange-600 font-bold' 
                    : 'border-white/10 bg-white/5 text-white/40 cursor-not-allowed'">
                  <div class="flex items-center gap-3">
                    <span class="material-symbols-outlined text-[22px]">
                      {{ cmdLoading.door ? 'progress_activity' : 'door_sliding' }}
                    </span>
                    <div class="text-left">
                      <p class="text-[12px] uppercase tracking-wider">Tắt báo động cửa đêm</p>
                      <p class="text-[10px] text-white/60 font-normal">Gửi mã sự kiện "OP" về Proteus</p>
                    </div>
                  </div>
                  <span class="material-symbols-outlined text-sm">chevron_right</span>
                </button>

              </div>

              <div v-if="feedbackMsg"
                class="text-[11px] text-center font-semibold uppercase tracking-wider py-2.5 rounded-lg transition-all border mt-2"
                :class="feedbackMsg.type === 'success' ? 'text-green-400 bg-green-400/10 border-green-500/20' : 'text-red-400 bg-red-400/10 border-red-500/20'">
                {{ feedbackMsg.text }}
              </div>
            </div>

          </div>
        </div>

        <div class="glass-card rounded-2xl overflow-hidden mb-20">
          <div class="px-8 py-5 border-b border-[#D9D7D0]/40 flex justify-between items-center">
            <div>
              <h2 class="text-[24px] font-bold text-[#1c1b1b] tracking-tight">Giám sát sự kiện thời gian thực</h2>
              <p class="text-xs text-[#8C8880] mt-0.5">Dữ liệu phân tích đồng bộ từ Mạch Proteus & AI Service Python</p>
            </div>
            <router-link to="/logs" class="text-[12px] font-semibold text-[#1c1b1b] uppercase border-b border-[#1c1b1b] tracking-wider hover:text-black">
              Xem toàn bộ nhật ký
            </router-link>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="bg-[#f7f3f2]">
                  <th class="px-8 py-4 text-[11px] font-bold text-[#8C8880] uppercase tracking-widest">Thời gian xảy ra</th>
                  <th class="px-8 py-4 text-[11px] font-bold text-[#8C8880] uppercase tracking-widest">Mã ký tự</th>
                  <th class="px-8 py-4 text-[11px] font-bold text-[#8C8880] uppercase tracking-widest">Loại Sự Kiện / Định Danh</th>
                  <th class="px-8 py-4 text-[11px] font-bold text-[#8C8880] uppercase tracking-widest">Trạng thái Cảnh Báo</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[#D9D7D0]/30">
                <tr v-if="loading">
                  <td colspan="4" class="px-8 py-6 text-[#8C8880] text-sm text-center">Đang tải và đồng bộ luồng dữ liệu...</td>
                </tr>
                <tr v-else-if="history.length === 0">
                  <td colspan="4" class="px-8 py-6 text-[#8C8880] text-sm text-center">Hệ thống an toàn. Không phát hiện bất thường.</td>
                </tr>
                <tr v-for="item in history.slice(0, 5)" :key="item.id" class="hover:bg-white/40 transition-colors">
                  <td class="px-8 py-6 text-[14px] text-[#4a4a4a]">{{ formatTime(item.timestamp) }}</td>
                  <td class="px-8 py-6">
                    <span class="font-mono bg-black/5 px-2 py-1 rounded text-xs font-bold text-[#1c1b1b]">
                      {{ item.raw_code || item.alert || 'SAFE' }}
                    </span>
                  </td>
                  <td class="px-8 py-6">
                    <div class="flex items-center gap-2 text-[13px] font-semibold uppercase"
                      :class="getAlertColorClass(item.alert)">
                      <span class="w-2 h-2 rounded-full" :class="getAlertBgClass(item.alert)"></span>
                      {{ getAlertTitle(item.alert) }}
                    </div>
                    <p class="text-xs text-[#8C8880] mt-0.5 font-normal">{{ item.description || 'Hệ thống vận hành trong ngưỡng bình thường' }}</p>
                  </td>
                  <td class="px-8 py-6">
                    <span class="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full border"
                      :class="getAlertBadgeClass(item.alert)">
                      {{ item.status_text || (item.alert !== 'SAFE' ? 'Đang kích hoạt' : 'An toàn') }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </main>

    <footer class="w-full py-8 border-t border-[#D9D7D0] bg-[#FAF9F5]">
      <div class="flex flex-col md:flex-row justify-between items-center px-10 max-w-[1728px] mx-auto gap-4">
        <span class="text-[24px] font-bold text-[#1c1b1b]">Sentinel AI</span>
        <span class="text-[10px] font-bold uppercase tracking-widest text-[#8C8880]">© 2026 Sentinel AI. Hệ thống tích hợp Proteus VSPE & YOLO.</span>
        <div class="flex gap-8">
          <a href="#" class="text-[10px] font-bold uppercase tracking-widest text-[#8C8880] hover:text-[#1c1b1b]">Mạch Vi Điều Khiển</a>
          <a href="#" class="text-[10px] font-bold uppercase tracking-widest text-[#8C8880] hover:text-[#1c1b1b]">Cấu Hình Serial</a>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  useSentinelStatus,
  useSentinelHistory,
  formatTime,
  sendActionToService
} from '../useSentinel.js'

// Khởi tạo lấy dữ liệu từ phần cứng qua Composable
const { status } = useSentinelStatus()
const { history, loading } = useSentinelHistory(10)

const streamError = ref(false)
const cmdLoading = ref({ intruder: false, door: false })
const feedbackMsg = ref(null)

// Kiểm tra xem hệ thống có bất kỳ cảnh báo nguy hiểm nào đang diễn ra không
const hasActiveAlert = computed(() => {
  return status.value?.alert === 'KL' || 
         status.value?.alert === 'FIRE' || 
         status.value?.alert === 'O' ||
         Number(status.value?.temperature) > 45 ||
         Number(status.value?.gas_ppm) > 300
})

// Xử lý thông tin hiển thị chạy chữ trên Marquee Banner đầu trang web
const currentAlertMessage = computed(() => {
  if (!status.value) return ''
  if (status.value.alert === 'KL') return 'PHÁT HIỆN ĐỘT NHẬP (PIR + YOLO XÁC NHẬN CÓ NGƯỜI TRONG KHUNG HÌNH)'
  if (status.value.alert === 'FIRE' || Number(status.value?.temperature) > 45 || Number(status.value?.gas_ppm) > 300) {
    return `CẢNH BÁO CHÁY / KHÓI (Nhiệt độ hiện tại: ${status.value.temperature}°C [Ngưỡng >45°C] — Khói: ${status.value.gas_ppm} PPM)`
  }
  if (status.value.alert === 'O') return 'VI PHẠM AN NINH: PHÁT HIỆN CỬA BAN ĐÊM BỊ MỞ TRONG KHUNG GIỜ 22h-6h'
  return 'Hệ thống đang ở trạng thái an toàn'
})

function showFeedback(text, type = 'success', duration = 3500) {
  feedbackMsg.value = { text, type }
  setTimeout(() => { feedbackMsg.value = null }, duration)
}

// ── WORKFLOW 1: Web tắt báo trộm -> bắn lệnh "DISARM_INTRUDER" để gửi mã "KF" xuống mạch
async function handleDisarmIntruder() {
  cmdLoading.value.intruder = true
  try {
    await sendActionToService({ action: 'DISARM_INTRUDER', code: 'KF' })
    showFeedback('✓ Đã tắt báo trộm. Service Python đang truyền mã "KF" xuống Proteus để ngắt còi.', 'success')
  } catch (e) {
    showFeedback('✗ Không thể kết nối tới Service Python', 'error')
  } finally {
    cmdLoading.value.intruder = false
  }
}

// ── WORKFLOW 3: Web tắt báo động cửa đêm -> bắn lệnh "DISARM_DOOR" để gửi mã "OP" xuống mạch
async function handleDisarmDoor() {
  cmdLoading.value.door = true
  try {
    await sendActionToService({ action: 'DISARM_DOOR', code: 'OP' })
    showFeedback('✓ Đã dập tắt cảnh báo cửa đêm. Lệnh "OP" đang được truyền xuống vi điều khiển.', 'success')
  } catch (e) {
    showFeedback('✗ Lỗi gửi yêu cầu điều khiển ngoại vi', 'error')
  } finally {
    cmdLoading.value.door = false
  }
}

// ── Các hàm xử lý giao diện màu sắc tương ứng mã định danh ──
function getAlertTitle(alertType) {
  if (alertType === 'KL') return 'Đột nhập nguy hiểm'
  if (alertType === 'FIRE') return 'Hỏa hoạn / Khói'
  if (alertType === 'O') return 'Cửa mở ban đêm'
  return 'An toàn'
}

function getAlertColorClass(alertType) {
  if (alertType === 'KL') return 'text-red-600'
  if (alertType === 'FIRE') return 'text-red-700'
  if (alertType === 'O') return 'text-orange-500'
  return 'text-green-600'
}

function getAlertBgClass(alertType) {
  if (alertType === 'KL') return 'bg-red-600 animate-ping'
  if (alertType === 'FIRE') return 'bg-red-700 animate-bounce'
  if (alertType === 'O') return 'bg-orange-500'
  return 'bg-green-500'
}

function getAlertBadgeClass(alertType) {
  if (alertType === 'KL') return 'text-red-600 border-red-500 bg-red-50'
  if (alertType === 'FIRE') return 'text-red-700 border-red-600 bg-red-50'
  if (alertType === 'O') return 'text-orange-500 border-orange-400 bg-orange-50'
  return 'text-gray-500 border-gray-300 bg-gray-50'
}
</script>

<style scoped>
.glass-card {
  background: rgba(255, 255, 255, 0.45);
  backdrop-filter: blur(24px) saturate(160%);
  border: 1px solid rgba(255, 255, 255, 0.5);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.glass-card:hover {
  background: rgba(255, 255, 255, 0.6);
  box-shadow: 0 10px 30px -10px rgba(0,0,0,0.05);
}
@keyframes marquee {
  0%   { transform: translateX(45%); }
  100% { transform: translateX(-100%); }
}
.animate-marquee {
  animation: marquee 22s linear infinite;
}
</style>