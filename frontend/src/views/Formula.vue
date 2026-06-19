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
          <template v-else>{{ result.original }}</template>
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
                <td>{{ getElementName(elem as string) }}</td>
                <td style="font-weight: 600; color: var(--accent);">{{ elem }}</td>
                <td>{{ count }}</td>
                <td>{{ getElementMass(elem as string) }}</td>
                <td>{{ (getElementMass(elem as string) * count).toFixed(3) }}</td>
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
import { ref } from 'vue'
import { parseFormula } from '../wails/app'

const input = ref('')
const result = ref<any>(null)
const viewMode = ref('subscript')
const copied = ref(false)

const elementMasses: Record<string, number> = {
  H: 1.008, He: 4.003, Li: 6.941, Be: 9.012, B: 10.81, C: 12.011,
  N: 14.007, O: 15.999, F: 18.998, Ne: 20.18, Na: 22.99, Mg: 24.305,
  Al: 26.982, Si: 28.086, P: 30.974, S: 32.065, Cl: 35.453, Ar: 39.948,
  K: 39.098, Ca: 40.078, Fe: 55.845, Cu: 63.546, Zn: 65.38, Ag: 107.87,
  Au: 196.97, Hg: 200.59, Pb: 207.2, Mn: 55.938, Cr: 51.996, Ni: 58.693,
  Ba: 137.33, Sr: 87.62, Br: 79.904, I: 126.9, Ti: 47.867, V: 50.942,
}

const elementNames: Record<string, string> = {
  H: '氢', He: '氦', Li: '锂', Be: '铍', B: '硼', C: '碳',
  N: '氮', O: '氧', F: '氟', Ne: '氖', Na: '钠', Mg: '镁',
  Al: '铝', Si: '硅', P: '磷', S: '硫', Cl: '氯', Ar: '氩',
  K: '钾', Ca: '钙', Fe: '铁', Cu: '铜', Zn: '锌', Ag: '银',
  Au: '金', Hg: '汞', Pb: '铅', Mn: '锰', Cr: '铬', Ni: '镍',
  Ba: '钡', Sr: '锶', Br: '溴', I: '碘', Ti: '钛', V: '钒',
}

function getElementMass(symbol: string): number {
  return elementMasses[symbol] || 0
}

function getElementName(symbol: string): string {
  return elementNames[symbol] || symbol
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
