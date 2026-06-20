<template>
  <div class="fade-in">
    <div class="page-header">
      <h1 class="page-title">⚙️ 设置</h1>
      <p class="page-subtitle">应用配置与系统信息</p>
    </div>

    <!-- Theme -->
    <div class="card">
      <div class="card-title">🎨 主题设置</div>
      <div class="setting-row">
        <div>
          <div style="font-weight: 500;">主题色</div>
          <div style="font-size: 12px; color: var(--text-muted);">选择界面强调色</div>
        </div>
        <div class="color-picker">
          <div
            v-for="c in themeColors"
            :key="c.value"
            class="color-dot"
            :class="{ active: accentColor === c.value }"
            :style="{ background: c.value }"
            :title="c.name"
            @click="setAccentColor(c.value)"
          ></div>
        </div>
      </div>
    </div>

    <!-- General -->
    <div class="card">
      <div class="card-title">🏠 通用设置</div>
      <div class="setting-row">
        <div>
          <div style="font-weight: 500;">窗口置顶</div>
          <div style="font-size: 12px; color: var(--text-muted);">保持窗口在最前面</div>
        </div>
        <div class="toggle" :class="{ active: alwaysOnTop }" @click="toggleSetting('alwaysOnTop', alwaysOnTop, v => alwaysOnTop = v)"></div>
      </div>
      <div class="setting-row">
        <div>
          <div style="font-weight: 500;">最小化到托盘</div>
          <div style="font-size: 12px; color: var(--text-muted);">关闭窗口时最小化到系统托盘</div>
        </div>
        <div class="toggle" :class="{ active: minimizeToTray }" @click="toggleSetting('minimizeToTray', minimizeToTray, v => minimizeToTray = v)"></div>
      </div>
    </div>

    <!-- Export -->
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
      <div class="input-group">
        <label class="input-label">PNG 导出分辨率</label>
        <div class="tab-bar">
          <div class="tab-item" :class="{ active: pngScale === '2x' }" @click="setPngScale('2x')">2x</div>
          <div class="tab-item" :class="{ active: pngScale === '4x' }" @click="setPngScale('4x')">4x</div>
        </div>
      </div>
    </div>

    <!-- Database -->
    <div class="card">
      <div class="card-title">🗄️ 数据库</div>
      <div class="setting-row">
        <div>
          <div style="font-weight: 500;">数据库路径</div>
          <div style="font-size: 12px; color: var(--text-muted); font-family: var(--font-mono);">{{ dbPath }}</div>
        </div>
        <span class="chip" style="background: rgba(74,222,128,0.15); color: var(--success);">已连接</span>
      </div>
      <div class="setting-row">
        <div>
          <div style="font-weight: 500;">元素数据</div>
          <div style="font-size: 12px; color: var(--text-muted);">已收录 {{ elementCount }} 种元素</div>
        </div>
        <span class="chip">118 元素</span>
      </div>
      <div style="margin-top: 12px;">
        <button class="btn btn-secondary btn-sm" @click="backupDB">备份数据库</button>
        <button class="btn btn-secondary btn-sm" style="margin-left: 8px;" @click="exportData">导出数据</button>
      </div>
    </div>

    <!-- Security -->
    <div class="card">
      <div class="card-title">🔒 安全设置</div>
      <div class="setting-row">
        <div>
          <div style="font-weight: 500;">AES-256 加密</div>
          <div style="font-size: 12px; color: var(--text-muted);">所有敏感数据使用 AES-256-GCM 加密存储</div>
        </div>
        <span class="chip" style="background: rgba(74,222,128,0.15); color: var(--success);">已启用</span>
      </div>
    </div>

    <!-- About -->
    <div class="card">
      <div class="card-title">ℹ️ 关于</div>
      <table class="data-table">
        <tbody>
          <tr><td style="color: var(--text-secondary);">应用名称</td><td>ChemMaster</td></tr>
          <tr><td style="color: var(--text-secondary);">版本</td><td>1.0.2</td></tr>
          <tr><td style="color: var(--text-secondary);">技术栈</td><td>Go + Wails v2 + Vue3 + TypeScript</td></tr>
          <tr><td style="color: var(--text-secondary);">数据库</td><td>SQLite (modernc.org/sqlite)</td></tr>
          <tr><td style="color: var(--text-secondary);">加密</td><td>AES-256-GCM</td></tr>
          <tr><td style="color: var(--text-secondary);">作者</td><td>Quantum-Ink</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getSetting, setSetting, getAllElements } from '../wails/app'

const alwaysOnTop = ref(false)
const minimizeToTray = ref(true)
const exportFormat = ref('unicode')
const pngScale = ref('2x')
const accentColor = ref('#6c6cf0')
const dbPath = ref('加载中...')
const elementCount = ref(0)

const themeColors = [
  { name: '靛蓝', value: '#6c6cf0' },
  { name: '天蓝', value: '#3b82f6' },
  { name: '翠绿', value: '#10b981' },
  { name: '琥珀', value: '#f59e0b' },
  { name: '玫红', value: '#ec4899' },
  { name: '青色', value: '#06b6d4' },
  { name: '紫色', value: '#8b5cf6' },
  { name: '橙色', value: '#f97316' },
]

onMounted(async () => {
  alwaysOnTop.value = (await getSetting('alwaysOnTop')) === 'true'
  minimizeToTray.value = (await getSetting('minimizeToTray')) !== 'false'
  exportFormat.value = (await getSetting('exportFormat')) || 'unicode'
  pngScale.value = (await getSetting('pngScale')) || '2x'
  accentColor.value = (await getSetting('accentColor')) || '#6c6cf0'
  dbPath.value = (await getSetting('dbPath')) || '~/.chemmaster/chemmaster.db'

  // Apply saved accent color
  applyAccentColor(accentColor.value)

  // Load element count
  const elements = await getAllElements() as any[]
  if (elements && elements.length) {
    elementCount.value = elements.length
  }
})

function toggleSetting(key: string, current: boolean, setter: (v: boolean) => void) {
  const newVal = !current
  setter(newVal)
  setSetting(key, String(newVal))
}

function setExportFormat(fmt: string) {
  exportFormat.value = fmt
  setSetting('exportFormat', fmt)
}

function setPngScale(scale: string) {
  pngScale.value = scale
  setSetting('pngScale', scale)
}

function setAccentColor(color: string) {
  accentColor.value = color
  setSetting('accentColor', color)
  applyAccentColor(color)
}

function applyAccentColor(color: string) {
  const root = document.documentElement
  root.style.setProperty('--accent', color)
  root.style.setProperty('--accent-hover', color + 'dd')
  root.style.setProperty('--accent-dim', color + '26')
}

function backupDB() {
  // Trigger a database backup via the backend
  alert('数据库备份功能即将开放')
}

function exportData() {
  alert('数据导出功能即将开放')
}
</script>

<style scoped>
.setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 0;
  border-bottom: 1px solid var(--border);
}

.setting-row:last-child {
  border-bottom: none;
}

.color-picker {
  display: flex;
  gap: 8px;
  align-items: center;
}

.color-dot {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
}

.color-dot:hover {
  transform: scale(1.15);
}

.color-dot.active {
  border-color: var(--text-primary);
  box-shadow: 0 0 0 2px var(--bg-primary), 0 0 0 4px var(--text-primary);
}
</style>
