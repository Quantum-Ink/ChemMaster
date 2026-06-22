<template>
  <div class="fade-in">
    <div class="page-header">
      <h1 class="page-title">⚙️ 设置</h1>
      <p class="page-subtitle">应用配置与系统信息</p>
    </div>

    <div class="card">
      <div class="card-title">🎨 主题设置</div>
      <div class="setting-row">
        <div>
          <div style="font-weight: 500;">深色/浅色模式</div>
          <div style="font-size: 12px; color: var(--text-muted);">切换界面明暗风格</div>
        </div>
        <div class="toggle" :class="{ active: isDark }" @click="toggleTheme"></div>
      </div>
      <div class="setting-row">
        <div>
          <div style="font-weight: 500;">主题色</div>
          <div style="font-size: 12px; color: var(--text-muted);">选择界面强调色</div>
        </div>
        <div class="color-picker">
          <div v-for="c in themeColors" :key="c.value" class="color-dot"
            :class="{ active: accentColor === c.value }"
            :style="{ background: c.value }" :title="c.name"
            @click="setAccentColor(c.value)"></div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-title">📤 导出设置</div>
      <div class="input-group">
        <label class="input-label">默认导出格式</label>
        <div class="tab-bar">
          <div class="tab-item" :class="{ active: exportFormat === 'unicode' }" @click="setExportFormat('unicode')">Unicode</div>
          <div class="tab-item" :class="{ active: exportFormat === 'latex' }" @click="setExportFormat('latex')">LaTeX</div>
          <div class="tab-item" :class="{ active: exportFormat === 'html' }" @click="setExportFormat('html')">HTML</div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-title">ℹ️ 关于</div>
      <table class="data-table">
        <tbody>
          <tr><td style="color: var(--text-secondary);">应用名称</td><td>ChemMaster</td></tr>
          <tr><td style="color: var(--text-secondary);">版本</td><td>1.1.0</td></tr>
          <tr><td style="color: var(--text-secondary);">技术栈</td><td>Go + Wails v2 + Vue3 + TypeScript</td></tr>
          <tr><td style="color: var(--text-secondary);">数据库</td><td>SQLite</td></tr>
          <tr><td style="color: var(--text-secondary);">作者</td><td>Quantum-Ink</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getSetting, setSetting } from '../wails/app'

const isDark = ref(true)
const accentColor = ref('#6c6cf0')
const exportFormat = ref('unicode')

const themeColors = [
  { name: '靛蓝', value: '#6c6cf0' },
  { name: '天蓝', value: '#3b82f6' },
  { name: '翠绿', value: '#10b981' },
  { name: '琥珀', value: '#f59e0b' },
  { name: '玫红', value: '#ec4899' },
  { name: '紫色', value: '#8b5cf6' },
]

onMounted(async () => {
  const theme = await getSetting('theme')
  isDark.value = theme !== 'light'
  accentColor.value = (await getSetting('accentColor')) || '#6c6cf0'
  exportFormat.value = (await getSetting('exportFormat')) || 'unicode'
  applyAccent(accentColor.value)
})

function toggleTheme() {
  isDark.value = !isDark.value
  const theme = isDark.value ? 'dark' : 'light'
  document.documentElement.setAttribute('data-theme', theme)
  setSetting('theme', theme)
}

function setAccentColor(color: string) {
  accentColor.value = color
  applyAccent(color)
  setSetting('accentColor', color)
}

function applyAccent(color: string) {
  const r = document.documentElement.style
  r.setProperty('--accent', color)
  r.setProperty('--accent-hover', color + 'dd')
  r.setProperty('--accent-dim', color + '26')
}

function setExportFormat(fmt: string) {
  exportFormat.value = fmt
  setSetting('exportFormat', fmt)
}
</script>

<style scoped>
.setting-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 0; border-bottom: 1px solid var(--border);
}
.setting-row:last-child { border-bottom: none; }
.color-picker { display: flex; gap: 8px; align-items: center; }
.color-dot {
  width: 28px; height: 28px; border-radius: 50%; cursor: pointer;
  border: 2px solid transparent; transition: all 0.2s;
}
.color-dot:hover { transform: scale(1.15); }
.color-dot.active {
  border-color: var(--text-primary);
  box-shadow: 0 0 0 2px var(--bg-primary), 0 0 0 4px var(--text-primary);
}
</style>
