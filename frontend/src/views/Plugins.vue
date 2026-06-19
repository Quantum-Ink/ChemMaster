<template>
  <div class="fade-in">
    <div class="page-header">
      <h1 class="page-title">🧩 插件管理</h1>
      <p class="page-subtitle">管理化学计算插件 — 启用/禁用/查看详情</p>
    </div>

    <!-- Plugin Stats -->
    <div class="grid-3" style="margin-bottom: 16px;">
      <div class="card" style="text-align: center;">
        <div style="font-size: 28px; font-weight: 700; color: var(--accent);">{{ plugins.length }}</div>
        <div style="font-size: 12px; color: var(--text-secondary);">总插件数</div>
      </div>
      <div class="card" style="text-align: center;">
        <div style="font-size: 28px; font-weight: 700; color: var(--success);">{{ plugins.filter(p => p.enabled).length }}</div>
        <div style="font-size: 12px; color: var(--text-secondary);">已启用</div>
      </div>
      <div class="card" style="text-align: center;">
        <div style="font-size: 28px; font-weight: 700; color: var(--text-muted);">{{ plugins.filter(p => !p.enabled).length }}</div>
        <div style="font-size: 12px; color: var(--text-secondary);">已禁用</div>
      </div>
    </div>

    <!-- Plugins List -->
    <div class="card">
      <div class="card-title">📦 已安装插件</div>
      <div v-for="(p, i) in plugins" :key="i" style="display: flex; align-items: center; justify-content: space-between; padding: 14px 0; border-bottom: 1px solid var(--border);">
        <div style="display: flex; align-items: center; gap: 12px;">
          <span style="font-size: 24px;">{{ categoryIcon(p.category) }}</span>
          <div>
            <div style="font-weight: 500;">{{ p.name }}</div>
            <div style="font-size: 12px; color: var(--text-muted);">{{ p.description }}</div>
            <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">
              v{{ p.version }} · {{ p.category }}
              <span v-if="p.initialized" style="color: var(--success);"> · ✓ 已初始化</span>
              <span v-else style="color: var(--error);"> · ✗ 未初始化</span>
            </div>
          </div>
        </div>
        <div style="display: flex; align-items: center; gap: 12px;">
          <span class="chip" :style="{ background: p.enabled ? 'rgba(74,222,128,0.15)' : 'rgba(248,113,113,0.15)', color: p.enabled ? 'var(--success)' : 'var(--error)' }">
            {{ p.enabled ? '启用' : '禁用' }}
          </span>
          <div class="toggle" :class="{ active: p.enabled }" @click="togglePlugin(p)"></div>
        </div>
      </div>
    </div>

    <!-- Plugin Categories -->
    <div class="card">
      <div class="card-title">📂 插件分类</div>
      <div class="chip-group">
        <span class="chip">🔬 parser</span>
        <span class="chip">⚖️ solver</span>
        <span class="chip">🗄️ database</span>
        <span class="chip">📤 export</span>
        <span class="chip">🤖 ai</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { listPlugins, setPluginEnabled } from '../wails/app'

const plugins = ref<any[]>([])

onMounted(async () => {
  plugins.value = await listPlugins() as any[]
  if (!plugins.value.length) {
    plugins.value = [
      { name: 'formula-parser', version: '1.0.0', description: 'Chemical formula parser', category: 'parser', enabled: true, initialized: true },
      { name: 'equation-balancer', version: '1.0.0', description: 'Chemical equation balancer', category: 'solver', enabled: true, initialized: true },
      { name: 'ion-engine', version: '1.0.0', description: 'Ionic equation analyzer', category: 'solver', enabled: true, initialized: true },
      { name: 'latex-export', version: '1.0.0', description: 'LaTeX export plugin', category: 'export', enabled: true, initialized: true },
      { name: 'png-export', version: '1.0.0', description: 'PNG export via SVG/Canvas', category: 'export', enabled: true, initialized: true },
      { name: 'local-database', version: '1.0.0', description: 'Local SQLite chemistry database', category: 'database', enabled: true, initialized: true },
      { name: 'pubchem-provider', version: '1.0.0', description: 'PubChem API data provider', category: 'database', enabled: true, initialized: true },
    ]
  }
})

function categoryIcon(cat: string): string {
  const icons: Record<string, string> = { parser: '🔬', solver: '⚖️', database: '🗄️', export: '📤', ai: '🤖' }
  return icons[cat] || '📦'
}

async function togglePlugin(p: any) {
  p.enabled = !p.enabled
  await setPluginEnabled(p.name, p.enabled)
}
</script>
