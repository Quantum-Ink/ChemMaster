<template>
  <div class="fade-in">
    <div class="page-header">
      <h1 class="page-title">🌐 数据源管理</h1>
      <p class="page-subtitle">管理化学数据源 — 本地数据库、PubChem API、在线抓取（Clash风格）</p>
    </div>

    <!-- Providers List -->
    <div class="card">
      <div class="card-title">📡 数据源列表</div>
      <div v-for="(p, i) in providers" :key="i" style="display: flex; align-items: center; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid var(--border);">
        <div style="display: flex; align-items: center; gap: 12px;">
          <span style="font-size: 20px;">{{ p.type === 'local' ? '🗄️' : p.type === 'api' ? '🌐' : '🔓' }}</span>
          <div>
            <div style="font-weight: 500;">{{ p.name }}</div>
            <div style="font-size: 12px; color: var(--text-muted);">{{ p.type }} · 优先级 {{ p.priority }}</div>
          </div>
        </div>
        <div style="display: flex; align-items: center; gap: 12px;">
          <span class="chip" :style="{ background: p.enabled ? 'rgba(74,222,128,0.15)' : 'rgba(248,113,113,0.15)', color: p.enabled ? 'var(--success)' : 'var(--error)' }">
            {{ p.enabled ? '已启用' : '已禁用' }}
          </span>
          <div class="toggle" :class="{ active: p.enabled }" @click="toggleProvider(i)"></div>
          <button class="btn btn-secondary btn-sm" @click="testConnection(p)">测试连接</button>
        </div>
      </div>
    </div>

    <!-- Query -->
    <div class="card">
      <div class="card-title">🔍 跨数据源查询</div>
      <div class="input-row">
        <div class="input-group">
          <input v-model="query" class="input-field" placeholder="输入化合物名称或化学式" @keyup.enter="search" />
        </div>
        <button class="btn btn-primary" @click="search">查询</button>
      </div>
      <div style="margin-top: 8px; font-size: 12px; color: var(--text-muted);">
        查询顺序: 本地数据库 → 缓存 → API Provider → 公开网页
      </div>
    </div>

    <!-- Search Results -->
    <div v-if="searchResults.length" class="card fade-in">
      <div class="card-title">📊 查询结果 ({{ searchResults.length }})</div>
      <div v-for="(r, i) in searchResults" :key="i" class="result-box" style="margin-bottom: 8px; padding: 12px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div>
            <div style="font-weight: 600; font-size: 16px;">{{ r.name || r.formula }}</div>
            <div style="font-size: 13px; color: var(--text-secondary);">
              {{ r.formula }} · MW: {{ r.molecularWeight }}
              <span v-if="r.casNumber"> · CAS: {{ r.casNumber }}</span>
            </div>
          </div>
          <span class="chip">{{ r.source }}</span>
        </div>
      </div>
    </div>

    <!-- Connection Test Result -->
    <div v-if="testResult" class="card fade-in">
      <div class="card-title">🔗 连接测试结果</div>
      <div class="result-box">{{ testResult }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { listProviders, searchCompoundOnline, testProviderConnection } from '../wails/app'

const providers = ref<any[]>([])
const query = ref('')
const searchResults = ref<any[]>([])
const testResult = ref('')

onMounted(async () => {
  providers.value = await listProviders() as any[]
  if (!providers.value.length) {
    providers.value = [
      { name: 'Local Database', type: 'local', enabled: true, priority: 1, status: 'ready' },
      { name: 'PubChem API', type: 'api', enabled: true, priority: 2, status: 'ready' },
      { name: 'ChEBI API', type: 'api', enabled: false, priority: 3, status: 'disabled' },
    ]
  }
})

function toggleProvider(index: number) {
  providers.value[index].enabled = !providers.value[index].enabled
}

async function search() {
  if (!query.value.trim()) return
  try {
    searchResults.value = await searchCompoundOnline(query.value.trim()) as any[]
  } catch (e: any) {
    searchResults.value = [{ name: 'Error', formula: query.value, molecularWeight: 0, source: e.message }]
  }
}

async function testConnection(provider: any) {
  testResult.value = 'Testing...'
  testResult.value = await testProviderConnection(provider.name)
}
</script>
