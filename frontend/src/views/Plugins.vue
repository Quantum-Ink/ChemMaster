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
      <div v-for="(p, i) in plugins" :key="i" class="plugin-item">
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
        <span class="chip" @click="filterCategory = filterCategory === 'parser' ? '' : 'parser'">
          🔬 parser <span v-if="filterCategory === 'parser'" style="color: var(--success);">✓</span>
        </span>
        <span class="chip" @click="filterCategory = filterCategory === 'solver' ? '' : 'solver'">
          ⚖️ solver <span v-if="filterCategory === 'solver'" style="color: var(--success);">✓</span>
        </span>
        <span class="chip" @click="filterCategory = filterCategory === 'database' ? '' : 'database'">
          🗄️ database <span v-if="filterCategory === 'database'" style="color: var(--success);">✓</span>
        </span>
        <span class="chip" @click="filterCategory = filterCategory === 'export' ? '' : 'export'">
          📤 export <span v-if="filterCategory === 'export'" style="color: var(--success);">✓</span>
        </span>
        <span class="chip" @click="filterCategory = filterCategory === 'ai' ? '' : 'ai'">
          🤖 ai <span v-if="filterCategory === 'ai'" style="color: var(--success);">✓</span>
        </span>
      </div>
      <div v-if="filterCategory" style="margin-top: 8px; font-size: 12px; color: var(--text-muted);">
        显示 {{ filteredPlugins.length }} 个 {{ filterCategory }} 插件
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { listPlugins, setPluginEnabled } from '../wails/app'

const plugins = ref<any[]>([])
const filterCategory = ref('')

const filteredPlugins = computed(() => {
  if (!filterCategory.value) return plugins.value
  return plugins.value.filter(p => p.category === filterCategory.value)
})

onMounted(async () => {
  const result = await listPlugins() as any[]
  if (result && result.length) {
    plugins.value = result
  } else {
    plugins.value = [
      { name: 'formula-parser', version: '1.0.0', description: '化学式解析引擎', category: 'parser', enabled: true, initialized: true },
      { name: 'equation-balancer', version: '1.0.0', description: '方程式配平（矩阵法）', category: 'solver', enabled: true, initialized: true },
      { name: 'ion-engine', version: '1.0.0', description: '离子方程式分析', category: 'solver', enabled: true, initialized: true },
      { name: 'latex-export', version: '1.0.0', description: 'LaTeX 格式导出', category: 'export', enabled: true, initialized: true },
      { name: 'png-export', version: '1.0.0', description: 'PNG 图片导出', category: 'export', enabled: true, initialized: true },
      { name: 'local-database', version: '1.0.0', description: '本地 SQLite 化学数据库', category: 'database', enabled: true, initialized: true },
      { name: 'pubchem-provider', version: '1.0.0', description: 'PubChem API 数据源', category: 'database', enabled: true, initialized: true },
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

<style scoped>
.plugin-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 0;
  border-bottom: 1px solid var(--border);
  transition: background 0.15s;
}

.plugin-item:hover {
  background: var(--bg-hover);
  margin: 0 -8px;
  padding: 14px 8px;
  border-radius: var(--radius-sm);
}

.plugin-item:last-child {
  border-bottom: none;
}
</style>
