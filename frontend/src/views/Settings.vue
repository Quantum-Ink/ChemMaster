<template>
  <div class="fade-in">
    <div class="page-header">
      <h1 class="page-title">⚙️ 设置</h1>
      <p class="page-subtitle">应用配置与系统信息</p>
    </div>

    <!-- General -->
    <div class="card">
      <div class="card-title">🎨 通用设置</div>
      <div style="display: flex; align-items: center; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid var(--border);">
        <div>
          <div style="font-weight: 500;">深色主题</div>
          <div style="font-size: 12px; color: var(--text-muted);">使用 Clash 风格深色主题</div>
        </div>
        <div class="toggle active"></div>
      </div>
      <div style="display: flex; align-items: center; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid var(--border);">
        <div>
          <div style="font-weight: 500;">窗口置顶</div>
          <div style="font-size: 12px; color: var(--text-muted);">保持窗口在最前面</div>
        </div>
        <div class="toggle" :class="{ active: alwaysOnTop }" @click="alwaysOnTop = !alwaysOnTop"></div>
      </div>
      <div style="display: flex; align-items: center; justify-content: space-between; padding: 12px 0;">
        <div>
          <div style="font-weight: 500;">最小化到托盘</div>
          <div style="font-size: 12px; color: var(--text-muted);">关闭窗口时最小化到系统托盘</div>
        </div>
        <div class="toggle" :class="{ active: minimizeToTray }" @click="minimizeToTray = !minimizeToTray"></div>
      </div>
    </div>

    <!-- Export -->
    <div class="card">
      <div class="card-title">📤 导出设置</div>
      <div class="input-group">
        <label class="input-label">默认导出格式</label>
        <div class="tab-bar">
          <div class="tab-item" :class="{ active: exportFormat === 'unicode' }" @click="exportFormat = 'unicode'">Unicode</div>
          <div class="tab-item" :class="{ active: exportFormat === 'latex' }" @click="exportFormat = 'latex'">LaTeX</div>
          <div class="tab-item" :class="{ active: exportFormat === 'html' }" @click="exportFormat = 'html'">HTML</div>
        </div>
      </div>
      <div class="input-group">
        <label class="input-label">PNG 导出分辨率</label>
        <div class="tab-bar">
          <div class="tab-item" :class="{ active: pngScale === '2x' }" @click="pngScale = '2x'">2x</div>
          <div class="tab-item" :class="{ active: pngScale === '4x' }" @click="pngScale = '4x'">4x</div>
        </div>
      </div>
    </div>

    <!-- Security -->
    <div class="card">
      <div class="card-title">🔒 安全设置</div>
      <div style="display: flex; align-items: center; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid var(--border);">
        <div>
          <div style="font-weight: 500;">AES-256 加密</div>
          <div style="font-size: 12px; color: var(--text-muted);">所有敏感数据使用 AES-256-GCM 加密存储</div>
        </div>
        <span class="chip" style="background: rgba(74,222,128,0.15); color: var(--success);">已启用</span>
      </div>
      <div style="display: flex; align-items: center; justify-content: space-between; padding: 12px 0;">
        <div>
          <div style="font-weight: 500;">凭证存储</div>
          <div style="font-size: 12px; color: var(--text-muted);">API Key 和 Cookie 使用加密存储</div>
        </div>
        <span class="chip" style="background: rgba(74,222,128,0.15); color: var(--success);">AES-256</span>
      </div>
    </div>

    <!-- Database -->
    <div class="card">
      <div class="card-title">🗄️ 数据库</div>
      <div class="input-group">
        <label class="input-label">数据库引擎</label>
        <div class="tab-bar">
          <div class="tab-item active">SQLite (默认)</div>
          <div class="tab-item">MySQL (可选)</div>
        </div>
      </div>
      <div style="margin-top: 12px;">
        <button class="btn btn-secondary btn-sm">备份数据库</button>
        <button class="btn btn-secondary btn-sm" style="margin-left: 8px;">导入数据</button>
      </div>
    </div>

    <!-- About -->
    <div class="card">
      <div class="card-title">ℹ️ 关于</div>
      <table class="data-table">
        <tbody>
          <tr><td style="color: var(--text-secondary);">应用名称</td><td>ChemMaster</td></tr>
          <tr><td style="color: var(--text-secondary);">版本</td><td>1.0.0</td></tr>
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
import { ref } from 'vue'

const alwaysOnTop = ref(false)
const minimizeToTray = ref(true)
const exportFormat = ref('unicode')
const pngScale = ref('2x')
</script>
