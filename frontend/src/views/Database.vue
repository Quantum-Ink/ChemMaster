<template>
  <div class="fade-in">
    <div class="page-header">
      <h1 class="page-title">🗄️ 化学数据库</h1>
      <p class="page-subtitle">118 元素周期表 · 化合物库 · 反应库</p>
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
          <input v-model="query" class="input-field"
            :placeholder="searchType === 'elements' ? '搜索元素: Fe, 铁, Iron, 26' : '搜索化合物: NaCl, 氯化钠'"
            @keyup.enter="search" />
        </div>
        <button class="btn btn-primary" @click="search">搜索</button>
      </div>
    </div>

    <!-- Periodic Table Grid -->
    <div v-if="searchType === 'elements'" class="card">
      <div class="card-title">🧪 元素周期表</div>
      <div class="periodic-grid">
        <div v-for="elem in periodicGrid" :key="elem?.symbol || Math.random()"
          class="pt-cell" :class="[elem?.category, { empty: !elem, selected: selectedElement?.symbol === elem?.symbol }]"
          @click="elem && selectElement(elem)">
          <template v-if="elem">
            <div class="pt-number">{{ elem.atomicNumber }}</div>
            <div class="pt-symbol">{{ elem.symbol }}</div>
            <div class="pt-name">{{ elem.nameCn }}</div>
          </template>
        </div>
      </div>
      <div class="legend">
        <span class="legend-item" v-for="c in categories" :key="c.key">
          <span class="legend-dot" :style="{ background: c.color }"></span>{{ c.label }}
        </span>
      </div>
    </div>

    <!-- Search Results -->
    <div v-if="searchResults.length" class="card fade-in">
      <div class="card-title">📊 搜索结果 ({{ searchResults.length }})</div>
      <table class="data-table">
        <thead>
          <tr v-if="searchType === 'elements'">
            <th>原子序数</th><th>符号</th><th>英文名</th><th>中文名</th><th>原子量</th><th>电子构型</th>
          </tr>
          <tr v-else>
            <th>名称</th><th>中文名</th><th>化学式</th><th>分子量</th><th>CAS号</th><th>来源</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="searchType === 'elements'" v-for="e in searchResults" :key="e.symbol" @click="selectElement(e)" style="cursor:pointer;">
            <td>{{ e.atomicNumber }}</td>
            <td style="font-weight: 600; color: var(--accent);">{{ e.symbol }}</td>
            <td>{{ e.nameEn }}</td>
            <td>{{ e.nameCn }}</td>
            <td>{{ e.atomicMass }}</td>
            <td style="font-family: var(--font-mono); font-size: 12px;">{{ e.electronConfig }}</td>
          </tr>
          <tr v-else v-for="c in searchResults" :key="c.id">
            <td>{{ c.name }}</td><td>{{ c.nameCn }}</td>
            <td style="font-weight: 600; color: var(--accent);">{{ c.formula }}</td>
            <td>{{ c.molecularWeight }}</td><td>{{ c.casNumber || '-' }}</td>
            <td><span class="chip" style="padding: 2px 8px;">{{ c.source }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Element Detail -->
    <div v-if="selectedElement" class="card fade-in">
      <div class="card-title">🔬 元素详情 — {{ selectedElement.symbol }}</div>
      <div class="grid-2">
        <div style="text-align: center; padding: 20px;">
          <div style="font-size: 12px; color: var(--text-muted);">{{ selectedElement.atomicNumber }}</div>
          <div style="font-size: 72px; font-weight: 700; color: var(--accent); line-height: 1;">{{ selectedElement.symbol }}</div>
          <div style="font-size: 18px; margin-top: 4px;">{{ selectedElement.nameCn }} ({{ selectedElement.nameEn }})</div>
          <div style="font-size: 14px; color: var(--text-secondary); margin-top: 8px;">原子量: {{ selectedElement.atomicMass }} u</div>
          <span class="chip" :style="{ background: catColor(selectedElement.category) + '22', color: catColor(selectedElement.category), borderColor: catColor(selectedElement.category) }" style="margin-top: 8px;">
            {{ catLabel(selectedElement.category) }}
          </span>
        </div>
        <table class="data-table">
          <tbody>
            <tr><td style="color: var(--text-secondary);">原子序数</td><td>{{ selectedElement.atomicNumber }}</td></tr>
            <tr><td style="color: var(--text-secondary);">元素符号</td><td>{{ selectedElement.symbol }}</td></tr>
            <tr><td style="color: var(--text-secondary);">英文名称</td><td>{{ selectedElement.nameEn }}</td></tr>
            <tr><td style="color: var(--text-secondary);">中文名称</td><td>{{ selectedElement.nameCn }}</td></tr>
            <tr><td style="color: var(--text-secondary);">相对原子质量</td><td>{{ selectedElement.atomicMass }} u</td></tr>
            <tr><td style="color: var(--text-secondary);">电子构型</td><td style="font-family: var(--font-mono);">{{ selectedElement.electronConfig }}</td></tr>
            <tr><td style="color: var(--text-secondary);">周期</td><td>{{ selectedElement.period }}</td></tr>
            <tr><td style="color: var(--text-secondary);">族</td><td>{{ selectedElement.group }}</td></tr>
            <tr><td style="color: var(--text-secondary);">电负性 (Pauling)</td><td>{{ selectedElement.electronegativity || '—' }}</td></tr>
            <tr><td style="color: var(--text-secondary);">分类</td><td>{{ catLabel(selectedElement.category) }}</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { getAllElements, searchElements, searchCompounds } from '../wails/app'

const searchType = ref<'elements' | 'compounds'>('elements')
const query = ref('')
const searchResults = ref<any[]>([])
const selectedElement = ref<any>(null)
const allElements = ref<any[]>([])

onMounted(async () => {
  const all = await getAllElements() as any[]
  if (all && all.length) allElements.value = all
})

// Build 18-col periodic table grid (7 periods + 2 lanthanide/actinide rows)
const periodicGrid = computed(() => {
  const grid: (any | null)[] = []
  const byPos: Record<string, any> = {}
  allElements.value.forEach(e => {
    byPos[`${e.period}-${e.group}`] = e
  })
  // Periods 1-7
  for (let p = 1; p <= 7; p++) {
    for (let g = 1; g <= 18; g++) {
      const key = `${p}-${g}`
      if (byPos[key]) {
        grid.push(byPos[key])
      } else if (p === 6 && g === 3) {
        grid.push({ symbol: 'La-Lu', nameCn: '镧系', atomicNumber: '57-71', category: 'lanthanide', isPlaceholder: true })
      } else if (p === 7 && g === 3) {
        grid.push({ symbol: 'Ac-Lr', nameCn: '锕系', atomicNumber: '89-103', category: 'actinide', isPlaceholder: true })
      } else {
        grid.push(null)
      }
    }
  }
  // Lanthanide row
  for (let i = 57; i <= 71; i++) {
    const e = allElements.value.find(el => el.atomicNumber === i)
    grid.push(e || null)
  }
  // Actinide row
  for (let i = 89; i <= 103; i++) {
    const e = allElements.value.find(el => el.atomicNumber === i)
    grid.push(e || null)
  }
  return grid
})

const categories = [
  { key: 'alkali', label: '碱金属', color: '#f87171' },
  { key: 'alkaline', label: '碱土金属', color: '#fb923c' },
  { key: 'transition', label: '过渡金属', color: '#fbbf24' },
  { key: 'post-transition', label: '后过渡金属', color: '#a3e635' },
  { key: 'metalloid', label: '准金属', color: '#34d399' },
  { key: 'nonmetal', label: '非金属', color: '#60a5fa' },
  { key: 'halogen', label: '卤素', color: '#c084fc' },
  { key: 'noble', label: '稀有气体', color: '#f472b6' },
  { key: 'lanthanide', label: '镧系', color: '#818cf8' },
  { key: 'actinide', label: '锕系', color: '#6ee7b7' },
]

function catColor(cat: string): string {
  return categories.find(c => c.key === cat)?.color || '#6c6cf0'
}
function catLabel(cat: string): string {
  return categories.find(c => c.key === cat)?.label || cat
}

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
  if (elem.isPlaceholder) return
  selectedElement.value = elem
}
</script>

<style scoped>
.periodic-grid {
  display: grid;
  grid-template-columns: repeat(18, 1fr);
  gap: 2px;
  margin-bottom: 12px;
}
.pt-cell {
  aspect-ratio: 1;
  padding: 3px;
  border-radius: 4px;
  text-align: center;
  cursor: pointer;
  transition: all 0.15s;
  border: 1px solid transparent;
  position: relative;
  min-width: 0;
}
.pt-cell:not(.empty):hover {
  border-color: var(--accent);
  transform: scale(1.15);
  z-index: 2;
}
.pt-cell.selected {
  border-color: var(--accent);
  box-shadow: 0 0 0 2px var(--accent-dim);
}
.pt-cell.empty { cursor: default; }
.pt-number { font-size: 8px; color: var(--text-muted); line-height: 1; }
.pt-symbol { font-size: 13px; font-weight: 700; line-height: 1.2; color: var(--text-primary); }
.pt-name { font-size: 7px; color: var(--text-secondary); line-height: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.pt-cell.alkali { background: rgba(248,113,113,0.12); }
.pt-cell.alkaline { background: rgba(251,146,60,0.12); }
.pt-cell.transition { background: rgba(251,191,36,0.12); }
.pt-cell.post-transition { background: rgba(163,230,53,0.12); }
.pt-cell.metalloid { background: rgba(52,211,153,0.12); }
.pt-cell.nonmetal { background: rgba(96,165,250,0.12); }
.pt-cell.halogen { background: rgba(192,132,252,0.12); }
.pt-cell.noble { background: rgba(244,114,182,0.12); }
.pt-cell.lanthanide { background: rgba(129,140,248,0.12); }
.pt-cell.actinide { background: rgba(110,231,183,0.12); }

.legend {
  display: flex; flex-wrap: wrap; gap: 12px; font-size: 11px; color: var(--text-secondary);
}
.legend-item { display: flex; align-items: center; gap: 4px; }
.legend-dot { width: 8px; height: 8px; border-radius: 50%; }
</style>
