<!-- sentinel-web/src/views/DashboardView.vue -->
<template>
  <div class="min-h-screen bg-[#FAF9F5] text-[#1c1b1b] font-[Helvetica,Arial,sans-serif]">

    <!-- Top Nav -->
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
      <!-- Alert Marquee — chỉ hiện khi có cảnh báo -->
      <section v-if="status?.alert !== 'SAFE'" class="w-full bg-red-100/40 border-b border-red-200/30 py-2 overflow-hidden whitespace-nowrap">
        <div class="inline-block animate-marquee">
          <span v-for="n in 3" :key="n" class="inline-flex items-center gap-2 mr-32 text-[#ba1a1a] text-[12px] font-semibold uppercase tracking-widest">
            <span class="material-symbols-outlined text-sm">warning</span>
            CẢNH BÁO KHẨN: {{ status?.alert === 'FIRE' ? 'PHÁT HIỆN LỬA/KHÓI' : 'PHÁT HIỆN XÂM NHẬP' }} — {{ status?.temperature }}°C
          </span>
        </div>
      </section>

      <div class="max-w-[1728px] mx-auto px-10 py-8 space-y-8">

        <!-- Main Grid: Camera + Sensors -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

          <!-- Live Feed -->
          <div class="lg:col-span-8 relative rounded-2xl overflow-hidden glass-card group">
            <img
              src="http://localhost:5000/video_feed"
              class="w-full h-[540px] object-cover"
              alt="Camera trực tiếp"
              @error="streamError = true"
              v-if="!streamError"
            />
            <div v-if="streamError" class="w-full h-[540px] bg-[#1a1a1a] flex items-center justify-center">
              <div class="text-center text-white/30">
                <span class="material-symbols-outlined text-6xl">videocam_off</span>
                <p class="text-xs uppercase tracking-widest mt-2">Camera ngoại tuyến</p>
                <p class="text-xs text-white/20 mt-1">Chạy mainv4.py để xem trực tiếp</p>
              </div>
            </div>
            <div class="absolute inset-0 pointer-events-none"
              style="background-image: radial-gradient(circle, rgba(255,255,255,0.05) 1px, transparent 1px); background-size: 30px 30px;"></div>
            <div class="absolute top-4 left-4 flex items-center gap-2">
              <span class="w-2 h-2 rounded-full animate-pulse" :class="streamError ? 'bg-gray-500' : 'bg-red-500'"></span>
              <span class="text-white text-[10px] uppercase bg-black/50 px-2 py-1 rounded tracking-widest font-bold">
                {{ streamError ? 'Camera ngoại tuyến' : 'Trực tiếp: CAM-01' }}
              </span>
            </div>
            <div v-if="status?.alert === 'FIRE'" class="absolute inset-0 border-4 border-red-500/60 rounded-2xl pointer-events-none animate-pulse"></div>
            <div v-if="status?.alert === 'PERSON'" class="absolute inset-0 border-4 border-orange-400/60 rounded-2xl pointer-events-none animate-pulse"></div>
            <div class="absolute bottom-4 right-4">
              <div class="flex items-center gap-2 bg-black/40 backdrop-blur-md px-3 py-2 rounded-full border border-white/20">
                <span class="material-symbols-outlined text-white text-lg">videocam</span>
                <span class="text-white text-[12px] font-semibold uppercase">Độ phân giải 4K</span>
              </div>
            </div>
          </div>

          <!-- Sensor + Controls -->
          <div class="lg:col-span-4 flex flex-col gap-6">

            <!-- Nhiệt độ -->
            <div class="glass-card p-4 rounded-2xl flex flex-col justify-between h-[160px]">
              <div class="flex justify-between items-start">
                <div>
                  <span class="text-[#8C8880] text-[12px] font-semibold uppercase tracking-widest">Nhiệt độ</span>
                  <h3 class="text-[32px] font-semibold mt-1 leading-none"
                    :class="status?.temp_warning ? 'text-[#ba1a1a]' : 'text-[#1c1b1b]'">
                    {{ status?.temperature ?? '—' }}°C
                  </h3>
                </div>
                <span class="material-symbols-outlined text-[#1c1b1b]">thermostat</span>
              </div>
              <div class="w-full h-8 relative">
                <div class="w-full h-px bg-[#D9D7D0]/30 relative">
                  <div class="absolute bottom-0 left-0 w-full h-[30px]"
                    style="background: linear-gradient(90deg, transparent 0%, #FF416C 50%, transparent 100%);
                           clip-path: polygon(0 80%, 20% 70%, 40% 90%, 60% 40%, 80% 60%, 100% 50%, 100% 100%, 0 100%);"></div>
                </div>
              </div>
            </div>

            <!-- Nồng độ khí -->
            <div class="glass-card p-4 rounded-2xl flex flex-col justify-between h-[160px]">
              <div class="flex justify-between items-start">
                <div>
                  <span class="text-[#8C8880] text-[12px] font-semibold uppercase tracking-widest">Nồng độ khí (PPM)</span>
                  <h3 class="text-[32px] font-semibold mt-1 leading-none text-[#1c1b1b]">
                    {{ status?.gas_ppm ?? '0.02' }} PPM
                  </h3>
                </div>
                <span class="material-symbols-outlined text-[#1c1b1b]">air</span>
              </div>
              <div class="w-full h-8 relative">
                <div class="w-full h-px bg-[#D9D7D0]/30 relative">
                  <div class="absolute bottom-0 left-0 w-full h-[20px]"
                    style="background: linear-gradient(90deg, transparent 0%, #000 50%, transparent 100%);
                           clip-path: polygon(0 90%, 20% 85%, 40% 92%, 60% 88%, 80% 91%, 100% 89%, 100% 100%, 0 100%);"></div>
                </div>
              </div>
            </div>

            <!-- Điều khiển phần cứng -->
            <div class="bg-[#1b1b1b] p-4 rounded-2xl flex flex-col gap-4 mt-auto">
              <span class="text-[#858383] text-[12px] font-semibold uppercase tracking-widest">Điều khiển phần cứng</span>
              <div class="grid grid-cols-2 gap-4">

                <!-- NÚT TẮT BÁO ĐỘNG -->
                <!-- Công dụng: ghi mute_alarm lên Firebase → Python ngừng gửi tín hiệu 'A' xuống 8051 → còi/đèn tắt -->
                <button
                  @click="handleMuteAlarm"
                  :disabled="cmdLoading.mute"
                  class="flex flex-col items-center justify-center py-6 rounded-xl border transition-all active:scale-95 relative"
                  :class="muteAlarm
                    ? 'bg-red-600 border-red-600 text-white'
                    : 'border-white/10 hover:bg-white/5 text-[#858383]'">
                  <span v-if="cmdLoading.mute" class="material-symbols-outlined mb-2 animate-spin text-[22px]">progress_activity</span>
                  <span v-else class="material-symbols-outlined mb-2 text-[22px]">
                    {{ muteAlarm ? 'notifications_active' : 'notifications_off' }}
                  </span>
                  <span class="text-[11px] font-bold uppercase tracking-wide">
                    {{ muteAlarm ? 'Bật lại báo động' : 'Tắt báo động' }}
                  </span>
                  <!-- tooltip -->
                  <span class="absolute -top-8 left-1/2 -translate-x-1/2 bg-black text-white text-[10px] px-2 py-1 rounded whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity">
                    Ngừng tín hiệu xuống 8051
                  </span>
                </button>

                <!-- NÚT ĐẶT LẠI CẢM BIẾN -->
                <!-- Công dụng: ghi reset_sensors lên Firebase → Python reset nhiệt độ & đếm người về 0 -->
                <button
                  @click="handleResetSensors"
                  :disabled="cmdLoading.reset"
                  class="flex flex-col items-center justify-center py-6 rounded-xl border border-white/10 hover:bg-white/5 transition-all active:scale-95 text-[#858383]"
                  :class="cmdLoading.reset ? 'opacity-60' : ''">
                  <span class="material-symbols-outlined mb-2 text-[22px]"
                    :class="cmdLoading.reset ? 'animate-spin' : ''">
                    {{ cmdLoading.reset ? 'progress_activity' : 'restart_alt' }}
                  </span>
                  <span class="text-[11px] font-bold uppercase tracking-wide">Đặt lại cảm biến</span>
                </button>

              </div>

              <!-- Thông báo phản hồi -->
              <div v-if="feedbackMsg"
                class="text-[11px] text-center font-semibold uppercase tracking-wider py-2 rounded-lg transition-all"
                :class="feedbackMsg.type === 'success' ? 'text-green-400 bg-green-400/10' : 'text-red-400 bg-red-400/10'">
                {{ feedbackMsg.text }}
              </div>
            </div>

          </div>
        </div>

        <!-- Bảng sự kiện gần đây -->
        <div class="glass-card rounded-2xl overflow-hidden mb-40">
          <div class="px-8 py-4 border-b border-white/20 flex justify-between items-center">
            <h2 class="text-[32px] font-semibold text-[#1c1b1b]">Sự kiện gần đây</h2>
            <router-link to="/logs" class="text-[12px] font-semibold text-[#1c1b1b] uppercase border-b border-[#1c1b1b]">
              Xem tất cả nhật ký
            </router-link>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="bg-[#f7f3f2]">
                  <th class="px-8 py-4 text-[12px] font-semibold text-[#8C8880] uppercase tracking-widest">Thời gian</th>
                  <th class="px-8 py-4 text-[12px] font-semibold text-[#8C8880] uppercase tracking-widest">Loại sự kiện</th>
                  <th class="px-8 py-4 text-[12px] font-semibold text-[#8C8880] uppercase tracking-widest">Mô tả</th>
                  <th class="px-8 py-4 text-[12px] font-semibold text-[#8C8880] uppercase tracking-widest">Trạng thái</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[#D9D7D0]/30">
                <tr v-if="loading">
                  <td colspan="4" class="px-8 py-6 text-[#8C8880] text-sm">Đang tải...</td>
                </tr>
                <tr v-for="item in history.slice(0, 5)" :key="item.id"
                  class="hover:bg-white/20 transition-colors">
                  <td class="px-8 py-6 text-[15px]">{{ formatTime(item.timestamp) }}</td>
                  <td class="px-8 py-6">
                    <span class="flex items-center gap-2 text-[12px] font-semibold uppercase"
                      :class="item.alert === 'FIRE' ? 'text-[#ba1a1a]' : item.alert === 'PERSON' ? 'text-orange-500' : 'text-[#1c1b1b]'">
                      <span class="w-1.5 h-1.5 rounded-full"
                        :class="item.alert === 'FIRE' ? 'bg-[#ba1a1a]' : item.alert === 'PERSON' ? 'bg-orange-500' : 'bg-green-500'"></span>
                      {{ item.alert === 'FIRE' ? 'Cảnh báo cháy' : item.alert === 'PERSON' ? 'Phát hiện xâm nhập' : 'Hệ thống an toàn' }}
                    </span>
                  </td>
                  <td class="px-8 py-6 text-[15px]">
                    {{ item.alert === 'FIRE'
                      ? `Phát hiện lửa/khói. Nhiệt độ: ${item.temperature}°C. Số vật thể: ${item.object_count}.`
                      : item.alert === 'PERSON'
                      ? `Phát hiện ${item.person_count} người. Nhiệt độ: ${item.temperature}°C.`
                      : 'Hệ thống hoạt động bình thường.' }}
                  </td>
                  <td class="px-8 py-6">
                    <span class="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full border"
                      :class="item.alert === 'FIRE' ? 'text-[#ba1a1a] border-[#ba1a1a]'
                             : item.alert === 'PERSON' ? 'text-orange-500 border-orange-400'
                             : 'text-[#8C8880] border-[#D9D7D0]'">
                      {{ item.alert === 'FIRE' ? 'Đang xử lý' : item.alert === 'PERSON' ? 'Đang điều tra' : 'Đã giải quyết' }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
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

    <!-- NÚT PHÁT CẢNH BÁO KHẨN CẤP -->
    <!-- Công dụng: ghi emergency: true lên Firebase → Python gửi tín hiệu 'F' liên tục xuống 8051 dù camera không phát hiện gì -->
    <div class="fixed bottom-6 right-6 z-50">
      <button
        @click="handleEmergency"
        :disabled="cmdLoading.emergency"
        class="flex items-center gap-3 px-6 py-4 rounded-full shadow-2xl transition-all active:scale-95 font-semibold"
        :class="emergencyActive
          ? 'bg-red-600 text-white animate-pulse'
          : 'bg-[#1b1b1b] text-white hover:bg-black'">
        <span class="font-bold text-sm" :class="emergencyActive ? 'text-white' : 'text-[#FF416C]'">SOS</span>
        <span class="text-[12px] uppercase tracking-widest">
          {{ emergencyActive ? 'Đang phát — Nhấn để tắt' : 'Phát cảnh báo khẩn cấp' }}
        </span>
      </button>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import {
  useSentinelStatus,
  useSentinelHistory,
  formatTime,
  setMuteAlarm,
  resetSensors,
  setEmergency
} from '../useSentinel.js'

const { status } = useSentinelStatus()
const { history, loading } = useSentinelHistory(20)
const streamError = ref(false)

// Trạng thái nút
const muteAlarm = ref(false)
const emergencyActive = ref(false)
const cmdLoading = ref({ mute: false, reset: false, emergency: false })
const feedbackMsg = ref(null)

function showFeedback(text, type = 'success', duration = 3000) {
  feedbackMsg.value = { text, type }
  setTimeout(() => { feedbackMsg.value = null }, duration)
}

// ── Xử lý Tắt báo động ──────────────────────────────────────────────────────
// Ghi mute_alarm lên Firebase → Python ngừng gửi tín hiệu 'A' xuống 8051
async function handleMuteAlarm() {
  cmdLoading.value.mute = true
  try {
    muteAlarm.value = !muteAlarm.value
    await setMuteAlarm(muteAlarm.value)
    showFeedback(muteAlarm.value ? '✓ Báo động đã tắt — 8051 không nhận tín hiệu' : '✓ Báo động đã bật lại')
  } catch (e) {
    muteAlarm.value = !muteAlarm.value
    showFeedback('✗ Lỗi kết nối Firebase', 'error')
  } finally {
    cmdLoading.value.mute = false
  }
}

// ── Xử lý Đặt lại cảm biến ──────────────────────────────────────────────────
// Ghi reset_sensors lên Firebase → Python reset nhiệt độ & đếm người về 0
async function handleResetSensors() {
  cmdLoading.value.reset = true
  try {
    await resetSensors()
    showFeedback('✓ Cảm biến đã đặt lại — dữ liệu bắt đầu từ 0')
  } catch (e) {
    showFeedback('✗ Lỗi kết nối Firebase', 'error')
  } finally {
    cmdLoading.value.reset = false
  }
}

// ── Xử lý Phát cảnh báo khẩn cấp ───────────────────────────────────────────
// Ghi emergency lên Firebase → Python gửi 'F' liên tục xuống 8051
async function handleEmergency() {
  cmdLoading.value.emergency = true
  try {
    emergencyActive.value = !emergencyActive.value
    await setEmergency(emergencyActive.value)
    showFeedback(
      emergencyActive.value
        ? '🚨 KHẨN CẤP đang phát — 8051 nhận tín hiệu F liên tục'
        : '✓ Đã tắt cảnh báo khẩn cấp',
      emergencyActive.value ? 'error' : 'success'
    )
  } catch (e) {
    emergencyActive.value = !emergencyActive.value
    showFeedback('✗ Lỗi kết nối Firebase', 'error')
  } finally {
    cmdLoading.value.emergency = false
  }
}
</script>

<style scoped>
.glass-card {
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(24px) saturate(150%);
  border: 1px solid rgba(255, 255, 255, 0.4);
}
.glass-card:hover {
  background: rgba(255, 255, 255, 0.5);
}
@keyframes marquee {
  0%   { transform: translateX(100%); }
  100% { transform: translateX(-100%); }
}
.animate-marquee {
  animation: marquee 20s linear infinite;
}
</style>