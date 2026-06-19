<template>
  <div class="fade-in">
    <div class="page-header">
      <h1 class="page-title">🗄️ 化学数据库</h1>
      <p class="page-subtitle">本地 SQLite 数据库 — 元素周期表、化合物库、反应库</p>
    </div>

    <!-- Search -->
    <div class="card">
      <div class="card-title">🔍 搜索</div>
      <div class="tab-bar">
        <div class="tab-item" :class="{ active: searchType === 'elements' }" @click="searchType = 'elements'">元素</div>
        <div class="tab-item" :class="{ active: searchType === 'compounds' }" @click="searchType = 'compounds'">化合物</div>
      </div>
      <div class="input-row">
        <div class="input-group">
          <input
            v-model="query"
            class="input-field"
            :placeholder="searchType === 'elements' ? '搜索元素: Fe, 铁, Iron' : '搜索化合物: NaCl, 氯化钠'"
            @keyup.enter="search"
          />
        </div>
        <button class="btn btn-primary" @click="search">搜索</button>
      </div>
    </div>

    <!-- Elements Grid -->
    <div v-if="searchType === 'elements'" class="card">
      <div class="card-title">🧪 元素周期表（部分）</div>
      <div class="grid-4">
        <div
          v-for="elem in elements"
          :key="elem.symbol"
          class="element-card"
          @click="selectElement(elem)"
        >
          <div class="element-number">{{ elem.atomicNumber }}</div>
          <div class="element-symbol">{{ elem.symbol }}</div>
          <div class="element-name">{{ elem.nameCn }}</div>
        </div>
      </div>
    </div>

    <!-- Search Results -->
    <div v-if="searchResults.length" class="card fade-in">
      <div class="card-title">📊 搜索结果 ({{ searchResults.length }})</div>
      <table class="data-table">
        <thead>
          <tr v-if="searchType === 'elements'">
            <th>原子序数</th>
            <th>符号</th>
            <th>英文名</th>
            <th>中文名</th>
            <th>原子量</th>
          </tr>
          <tr v-else>
            <th>名称</th>
            <th>中文名</th>
            <th>化学式</th>
            <th>分子量</th>
            <th>CAS号</th>
            <th>来源</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="searchType === 'elements'" v-for="e in searchResults" :key="e.symbol">
            <td>{{ e.atomicNumber }}</td>
            <td style="font-weight: 600; color: var(--accent);">{{ e.symbol }}</td>
            <td>{{ e.nameEn }}</td>
            <td>{{ e.nameCn }}</td>
            <td>{{ e.atomicMass }}</td>
          </tr>
          <tr v-else v-for="c in searchResults" :key="c.id">
            <td>{{ c.name }}</td>
            <td>{{ c.nameCn }}</td>
            <td style="font-weight: 600; color: var(--accent);">{{ c.formula }}</td>
            <td>{{ c.molecularWeight }}</td>
            <td>{{ c.casNumber || '-' }}</td>
            <td><span class="chip" style="padding: 2px 8px;">{{ c.source }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Element Detail -->
    <div v-if="selectedElement" class="card fade-in">
      <div class="card-title">🔬 元素详情</div>
      <div class="grid-2">
        <div style="text-align: center; padding: 20px;">
          <div style="font-size: 12px; color: var(--text-muted);">{{ selectedElement.atomicNumber }}</div>
          <div style="font-size: 64px; font-weight: 700; color: var(--accent);">{{ selectedElement.symbol }}</div>
          <div style="font-size: 18px;">{{ selectedElement.nameCn }} ({{ selectedElement.nameEn }})</div>
          <div style="font-size: 14px; color: var(--text-secondary); margin-top: 8px;">原子量: {{ selectedElement.atomicMass }}</div>
        </div>
        <div>
          <table class="data-table">
            <tbody>
              <tr><td style="color: var(--text-secondary);">原子序数</td><td>{{ selectedElement.atomicNumber }}</td></tr>
              <tr><td style="color: var(--text-secondary);">元素符号</td><td>{{ selectedElement.symbol }}</td></tr>
              <tr><td style="color: var(--text-secondary);">英文名称</td><td>{{ selectedElement.nameEn }}</td></tr>
              <tr><td style="color: var(--text-secondary);">中文名称</td><td>{{ selectedElement.nameCn }}</td></tr>
              <tr><td style="color: var(--text-secondary);">相对原子质量</td><td>{{ selectedElement.atomicMass }} u</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getAllElements, searchElements, searchCompounds } from '../wails/app'

const searchType = ref<'elements' | 'compounds'>('elements')
const query = ref('')
const searchResults = ref<any[]>([])
const selectedElement = ref<any>(null)
const elements = ref<any[]>([])

onMounted(async () => {
  const all = await getAllElements() as any[]
  if (all && all.length) {
    elements.value = all
  }
})

async function search() {
  if (!query.value.trim()) return
  if (searchType.value === 'elements') {
    searchResults.value = await searchElements(query.value.trim()) as any[]
  } else {
    searchResults.value = await searchCompounds(query.value.trim()) as any[]
  }
  selectedElement.value = null
}

function selectElement(elem: any) {
  selectedElement.value = elem
}
</script>
