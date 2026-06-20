<template>
  <div class="app-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <span class="sidebar-logo">⚗️</span>
        <span class="sidebar-brand">ChemMaster</span>
      </div>
      <nav class="sidebar-nav">
        <div class="nav-section">
          <div class="nav-section-title">主页</div>
          <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
            <span class="nav-item-icon">🏠</span><span>首页</span>
          </router-link>
        </div>
        <div class="nav-section">
          <div class="nav-section-title">化学计算</div>
          <router-link to="/formula" class="nav-item" :class="{ active: $route.path === '/formula' }">
            <span class="nav-item-icon">🔬</span><span>化学式解析</span>
          </router-link>
          <router-link to="/equation" class="nav-item" :class="{ active: $route.path === '/equation' }">
            <span class="nav-item-icon">⚖️</span><span>方程式配平</span>
          </router-link>
          <router-link to="/reaction" class="nav-item" :class="{ active: $route.path === '/reaction' }">
            <span class="nav-item-icon">🧪</span><span>化学反应表达</span>
          </router-link>
          <router-link to="/ion" class="nav-item" :class="{ active: $route.path === '/ion' }">
            <span class="nav-item-icon">⚡</span><span>离子方程式</span>
          </router-link>
        </div>
        <div class="nav-section">
          <div class="nav-section-title">工具</div>
          <router-link to="/mol-editor" class="nav-item" :class="{ active: $route.path === '/mol-editor' }">
            <span class="nav-item-icon">🧬</span><span>分子编辑器</span>
          </router-link>
        </div>
        <div class="nav-section">
          <div class="nav-section-title">数据</div>
          <router-link to="/database" class="nav-item" :class="{ active: $route.path === '/database' }">
            <span class="nav-item-icon">🗄️</span><span>化学数据库</span>
          </router-link>
          <router-link to="/providers" class="nav-item" :class="{ active: $route.path === '/providers' }">
            <span class="nav-item-icon">🌐</span><span>数据源管理</span>
          </router-link>
        </div>
        <div class="nav-section">
          <div class="nav-section-title">系统</div>
          <router-link to="/plugins" class="nav-item" :class="{ active: $route.path === '/plugins' }">
            <span class="nav-item-icon">🧩</span><span>插件管理</span>
          </router-link>
          <router-link to="/settings" class="nav-item" :class="{ active: $route.path === '/settings' }">
            <span class="nav-item-icon">⚙️</span><span>设置</span>
          </router-link>
        </div>
      </nav>
    </aside>

    <div class="main-area">
      <div class="titlebar">
        <span class="titlebar-title">ChemMaster v1.0.2</span>
        <div class="titlebar-controls">
          <button class="titlebar-btn minimize" @click="windowMinimize">─</button>
          <button class="titlebar-btn maximize" @click="windowMaximize">□</button>
          <button class="titlebar-btn close" @click="windowClose">✕</button>
        </div>
      </div>
      <main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
      <div class="status-bar">
        <span><span class="status-dot online"></span> 就绪</span>
        <span>{{ currentTime }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { getSetting } from './wails/app'

const currentTime = ref('')
let timer: number

onMounted(async () => {
  updateTime()
  timer = window.setInterval(updateTime, 1000)

  // Apply saved theme
  const theme = await getSetting('theme')
  if (theme) document.documentElement.setAttribute('data-theme', theme)

  // Apply saved accent color
  const accent = await getSetting('accentColor')
  if (accent) {
    document.documentElement.style.setProperty('--accent', accent)
    document.documentElement.style.setProperty('--accent-hover', accent + 'dd')
    document.documentElement.style.setProperty('--accent-dim', accent + '26')
  }
})

onUnmounted(() => clearInterval(timer))

function updateTime() {
  currentTime.value = new Date().toLocaleTimeString('zh-CN', { hour12: false })
}

function windowMinimize() {
  (window as any).runtime?.WindowMinimise()
}
function windowMaximize() {
  (window as any).runtime?.WindowToggleMaximise()
}
function windowClose() {
  (window as any).runtime?.WindowClose()
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.15s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
