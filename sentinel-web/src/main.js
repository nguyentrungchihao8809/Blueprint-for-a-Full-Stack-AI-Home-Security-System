import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import DashboardView from './views/DashboardView.vue'
import SecurityLogsView from './views/SecurityLogsView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: DashboardView },
    { path: '/logs', component: SecurityLogsView }
  ]
})

createApp(App).use(router).mount('#app')