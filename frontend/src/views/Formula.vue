<template>
  <div class="fade-in">
    <div class="page-header">
      <h1 class="page-title">🔬 化学式解析</h1>
      <p class="page-subtitle">解析化学式，获取元素组成、分子量、Unicode下标、LaTeX格式</p>
    </div>

    <div class="card">
      <div class="card-title">输入化学式</div>
      <div class="input-row">
        <div class="input-group">
          <input
            v-model="input"
            class="input-field"
            placeholder="H2SO4, Ca(OH)2, [Cu(NH3)4]SO4, Fe2(SO4)3"
            @keyup.enter="parse"
            autofocus
          />
        </div>
        <button class="btn btn-primary" @click="parse">解析</button>
        <button class="btn btn-ghost" @click="clear">清除</button>
      </div>
    </div>

    <div v-if="result" class="fade-in">
      <!-- Preview -->
      <div class="card">
        <div class="card-title">📝 解析结果</div>
        <div class="tab-bar">
          <div class="tab-item" :class="{ active: viewMode === 'subscript' }" @click="viewMode = 'subscript'">下标格式</div>
          <div class="tab-item" :class="{ active: viewMode === 'latex' }" @click="viewMode = 'latex'">LaTeX</div>
          <div class="tab-item" :class="{ active: viewMode === 'html' }" @click="viewMode = 'html'">HTML</div>
        </div>
        <div class="result-box result-formula">
          <template v-if="viewMode === 'subscript'">{{ result.subscript }}</template>
          <template v-else-if="viewMode === 'latex'">{{ result.latex }}</template>
          <template v-else><span v-html="htmlFormula"></span></template>
        </div>
        <div class="export-row">
          <button class="btn btn-secondary btn-sm" @click="copy(result.subscript)">📋 复制 Unicode</button>
          <button class="btn btn-secondary btn-sm" @click="copy(result.latex)">📋 复制 LaTeX</button>
          <span v-if="copied" style="color: var(--success); font-size: 12px; align-self: center;">✓ 已复制</span>
        </div>
      </div>

      <!-- Details -->
      <div class="grid-2">
        <div class="card">
          <div class="card-title">📊 元素组成</div>
          <table class="data-table">
            <thead>
              <tr>
                <th>元素</th>
                <th>符号</th>
                <th>原子数</th>
                <th>原子量</th>
                <th>质量贡献</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(count, elem) in result.elements" :key="elem">
                <td>{{ getElementName(elem) }}</td>
                <td style="font-weight: 600; color: var(--accent);">{{ elem }}</td>
                <td>{{ count }}</td>
                <td>{{ getElementMass(elem) }}</td>
                <td>{{ (getElementMass(elem) * count).toFixed(3) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="card">
          <div class="card-title">⚖️ 分子量信息</div>
          <div style="text-align: center; padding: 20px 0;">
            <div style="font-size: 48px; font-weight: 700; color: var(--accent);">
              {{ result.molecularWeight }}
            </div>
            <div style="font-size: 14px; color: var(--text-secondary); margin-top: 8px;">g/mol</div>
          </div>
          <div style="margin-top: 16px;">
            <div class="input-label">验证状态</div>
            <div style="display: flex; align-items: center; gap: 8px;">
              <span class="status-dot" :class="result.isValid ? 'online' : 'offline'"></span>
              <span>{{ result.isValid ? '有效化学式' : '无效化学式: ' + result.error }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Examples -->
    <div class="card">
      <div class="card-title">📚 示例化学式</div>
      <div class="chip-group">
        <span class="chip" @click="input = 'H2SO4'; parse()">H₂SO₄ 硫酸</span>
        <span class="chip" @click="input = 'Ca(OH)2'; parse()">Ca(OH)₂ 氢氧化钙</span>
        <span class="chip" @click="input = 'NH4+'; parse()">NH₄⁺ 铵根</span>
        <span class="chip" @click="input = 'CO2'; parse()">CO₂ 二氧化碳</span>
        <span class="chip" @click="input = 'NaCl'; parse()">NaCl 氯化钠</span>
        <span class="chip" @click="input = 'C6H12O6'; parse()">C₆H₁₂O₆ 葡萄糖</span>
        <span class="chip" @click="input = 'K3[Fe(CN)6]'; parse()">K₃[Fe(CN)₆] 赤血盐</span>
        <span class="chip" @click="input = '[Cu(NH3)4]SO4'; parse()">[Cu(NH₃)₄]SO₄</span>
        <span class="chip" @click="input = 'Al2(SO4)3'; parse()">Al₂(SO₄)₃ 硫酸铝</span>
        <span class="chip" @click="input = 'Fe2(SO4)3'; parse()">Fe₂(SO₄)₃ 硫酸铁</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { parseFormula, getAllElements } from '../wails/app'

const input = ref('')
const result = ref<any>(null)
const viewMode = ref('subscript')
const copied = ref(false)

const htmlFormula = computed(() => {
  if (!result.value) return ''
  const formula = result.value.original
  // Convert formula to HTML with subscripts/superscripts
  return formula
    .replace(/([A-Z][a-z]?)(\d+)/g, '$1<sub>$2</sub>')
    .replace(/\^([0-9+\-]+)/g, '<sup>$1</sup>')
    .replace(/\(/g, '(')
    .replace(/\)/g, ')')
})

const elementMasses: Record<string, number> = {}
const elementNames: Record<string, string> = {}

onMounted(async () => {
  const all = await getAllElements() as any[]
  if (all) {
    for (const e of all) {
      elementMasses[e.symbol] = e.atomicMass
      elementNames[e.symbol] = e.nameCn
    }
  }
})

function getElementMass(symbol: any): number {
  return elementMasses[String(symbol)] || 0
}

function getElementName(symbol: any): string {
  return elementNames[String(symbol)] || String(symbol)
}

async function parse() {
  if (!input.value.trim()) return
  result.value = await parseFormula(input.value.trim())
  copied.value = false
}

function clear() {
  input.value = ''
  result.value = null
}

function copy(text: string) {
  navigator.clipboard.writeText(text)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}
</script>
