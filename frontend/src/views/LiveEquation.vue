<template>
  <div class="fade-in">
    <div class="page-header">
      <h1 class="page-title">✏️ 实时方程式画布</h1>
      <p class="page-subtitle">输入化学式 → 实时渲染为 Unicode / LaTeX / PNG</p>
    </div>

    <div class="grid-2" style="gap: 16px;">
      <!-- Left: Input + Canvas -->
      <div>
        <div class="card">
          <div class="card-title">📝 输入</div>
          <div class="input-group">
            <label class="input-label">化学方程式</label>
            <input v-model="input" class="input-field mono-input" placeholder="例: N2 + 3H2 <=>[Fe][500K] 2NH3"
              @input="onInput" autofocus />
          </div>
          <div style="font-size: 12px; color: var(--text-muted); line-height: 1.8;">
            <div>→ <code>-></code> 或 <code>→</code> 不可逆反应</div>
            <div>⇌ <code><=></code> 或 <code><-></code> 或 <code>⇌</code> 可逆反应</div>
            <div>↑ <code>(g)</code> <code>(↑)</code> 气体 · <code>(s)</code> 固体 · <code>(l)</code> 液体 · <code>(aq)</code> 水溶液</div>
            <div>条件 <code>[催化剂][温度]</code> 例: <code>[Fe][500K]</code></div>
          </div>
        </div>

        <div class="card">
          <div class="card-title">🎨 实时渲染画布</div>
          <div class="canvas-area" ref="canvasRef">
            <div class="equation-display" v-html="renderedHTML"></div>
          </div>
          <div class="canvas-actions">
            <button class="btn btn-sm btn-secondary" @click="copyUnicode" :disabled="!parsed">复制 Unicode</button>
            <button class="btn btn-sm btn-secondary" @click="copyLatex" :disabled="!parsed">复制 LaTeX</button>
            <button class="btn btn-sm btn-secondary" @click="copyMhchem" :disabled="!parsed">复制 mhchem</button>
            <button class="btn btn-sm btn-primary" @click="exportPNG(2)" :disabled="!parsed">PNG @2x</button>
            <button class="btn btn-sm btn-primary" @click="exportPNG(4)" :disabled="!parsed">PNG @4x</button>
          </div>
        </div>
      </div>

      <!-- Right: Output panels -->
      <div>
        <div class="card">
          <div class="card-title">📋 Unicode 输出</div>
          <div class="result-box result-formula" style="min-height: 48px;">{{ unicode || '—' }}</div>
        </div>
        <div class="card">
          <div class="card-title">📄 LaTeX (mhchem) 输出</div>
          <div class="result-box mono-result" style="font-size: 16px;">{{ latex || '—' }}</div>
        </div>
        <div class="card">
          <div class="card-title">🔍 解析详情</div>
          <div v-if="parsed">
            <table class="data-table">
              <tbody>
                <tr><td style="color:var(--text-secondary)">反应物</td><td>{{ parsed.reactants.join(' + ') }}</td></tr>
                <tr><td style="color:var(--text-secondary)">产物</td><td>{{ parsed.products.join(' + ') }}</td></tr>
                <tr><td style="color:var(--text-secondary)">反应类型</td><td>{{ parsed.isReversible ? '可逆' : '不可逆' }}</td></tr>
                <tr v-if="parsed.conditions.length"><td style="color:var(--text-secondary)">条件</td><td>{{ parsed.conditions.join(', ') }}</td></tr>
              </tbody>
            </table>
          </div>
          <div v-else style="color: var(--text-muted); font-size: 13px;">输入方程式后自动解析</div>
        </div>

        <div class="card">
          <div class="card-title">📚 快速示例</div>
          <div class="chip-group">
            <span class="chip" @click="loadExample('N2 + 3H2 <=>[Fe][500K] 2NH3')">哈伯法</span>
            <span class="chip" @click="loadExample('2H2 + O2 -> 2H2O')">氢气燃烧</span>
            <span class="chip" @click="loadExample('CaCO3 ->[高温] CaO + CO2↑')">碳酸钙分解</span>
            <span class="chip" @click="loadExample('Fe2O3 + 3CO ->[高温] 2Fe + 3CO2')">炼铁</span>
            <span class="chip" @click="loadExample('NaOH + HCl -> NaCl + H2O')">中和反应</span>
            <span class="chip" @click="loadExample('CH4 + 2O2 ->[点燃] CO2 + 2H2O')">甲烷燃烧</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const input = ref('')
const unicode = ref('')
const latex = ref('')
const renderedHTML = ref('')
const parsed = ref<ReturnType<typeof parseEquation> | null>(null)
const canvasRef = ref<HTMLDivElement>()

let debounceTimer: ReturnType<typeof setTimeout>

function onInput() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => update(), 80)
}

function loadExample(eq: string) {
  input.value = eq
  update()
}

function update() {
  const raw = input.value.trim()
  if (!raw) {
    unicode.value = ''; latex.value = ''; renderedHTML.value = ''; parsed.value = null
    return
  }
  parsed.value = parseEquation(raw)
  unicode.value = toUnicode(parsed.value)
  latex.value = toLatex(parsed.value)
  renderedHTML.value = toHTML(parsed.value)
}

// ===== Parser =====
interface ParsedEq {
  raw: string
  reactants: string[]
  products: string[]
  conditions: string[]
  isReversible: boolean
  arrow: string
}

function parseEquation(raw: string): ParsedEq {
  // Normalize arrows
  let s = raw
    .replace(/<=>|⇌|⇄/g, '<EQ_REV>')
    .replace(/->|→|⟶/g, '<EQ_IRR>')

  const isReversible = s.includes('<EQ_REV>')
  const arrow = isReversible ? '<EQ_REV>' : '<EQ_IRR>'
  const sides = s.split(arrow)

  const conditions: string[] = []
  const condRegex = /\[([^\]]+)\]/g
  let m
  while ((m = condRegex.exec(sides[0] || '')) !== null) conditions.push(m[1])
  while ((m = condRegex.exec(sides[1] || '')) !== null) conditions.push(m[1])

  const parseSide = (side: string) =>
    side.replace(/\[[^\]]+\]/g, '').split('+').map(t => t.trim()).filter(Boolean)

  return {
    raw,
    reactants: parseSide(sides[0] || ''),
    products: parseSide(sides[1] || ''),
    conditions,
    isReversible,
    arrow,
  }
}

// ===== Unicode rendering =====
const subMap: Record<string, string> = { '0':'₀','1':'₁','2':'₂','3':'₃','4':'₄','5':'₅','6':'₆','7':'₇','8':'₈','9':'₉' }
const supMap: Record<string, string> = { '0':'⁰','1':'¹','2':'²','3':'³','4':'⁴','5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹','+':'⁺','-':'⁻' }

function toSub(s: string) { return s.replace(/[0-9]/g, c => subMap[c] || c) }
function toSup(s: string) { return s.replace(/[0-9+\-]/g, c => supMap[c] || c) }

function formulaToUnicode(f: string): string {
  // Strip state markers
  f = f.replace(/\((?:g|s|l|aq|↑|↓)\)/g, '')
  // coefficient
  let coeff = ''
  const cm = f.match(/^(\d+)(.*)/)
  if (cm) { coeff = cm[1]; f = cm[2] }
  // subscript numbers, superscript charges
  let out = f
    .replace(/([A-Z][a-z]?)(\d+)/g, (_, el, n) => el + toSub(n))
    .replace(/\^([0-9+\-]+)/g, (_, c) => toSup(c))
  // state markers as unicode
  out = input.value.match(/\((?:g)\)/) ? out : out
  return coeff + out
}

function toUnicode(eq: ParsedEq): string {
  const r = eq.reactants.map(formulaToUnicode)
  const p = eq.products.map(formulaToUnicode)
  const arrow = eq.isReversible ? ' ⇌ ' : ' → '
  const cond = eq.conditions.length ? ' ' + eq.conditions.map(c => toSub(c)).join(' ') : ''
  return r.join(' + ') + (cond ? arrow.trim() + cond : arrow) + p.join(' + ')
}

// ===== LaTeX (mhchem) rendering =====
function formulaToLatex(f: string): string {
  // Keep state markers as mhchem supports them
  let s = f.replace(/->/g, '\\to').replace(/<=>/g, '\\rightleftharpoons')
  // Convert coefficient + formula
  s = s.replace(/^(\d+)/, '$1')
  return s
}

function toLatex(eq: ParsedEq): string {
  const r = eq.reactants.join(' + ')
  const p = eq.products.join(' + ')
  const arrow = eq.isReversible ? '\\rightleftharpoons' : '\\to'
  const cond = eq.conditions.length
    ? `[${eq.conditions[0]}]` + (eq.conditions[1] ? `[${eq.conditions[1]}]` : '')
    : ''
  return `\\ce{${r} ${arrow}${cond} ${p}}`
}

// ===== HTML rendering =====
function formulaToHTML(f: string): string {
  let s = f.replace(/\((?:g|s|l|aq|↑|↓)\)/g, (m) => {
    const state = m[1] === '↑' ? '↑' : m[1] === '↓' ? '↓' : `(${m[1]})`
    return `<sub class="state">${state}</sub>`
  })
  const cm = s.match(/^(\d+)(.*)/)
  let coeff = '', rest = s
  if (cm) { coeff = `<span class="coeff">${cm[1]}</span>`; rest = cm[2] }
  rest = rest.replace(/([A-Z][a-z]?)(\d+)/g, (_, el, n) => `${el}<sub>${n}</sub>`)
  rest = rest.replace(/\^([0-9+\-]+)/g, (_, c) => `<sup>${c}</sup>`)
  return coeff + rest
}

function toHTML(eq: ParsedEq): string {
  const r = eq.reactants.map(formulaToHTML)
  const p = eq.products.map(formulaToHTML)
  const arrow = eq.isReversible
    ? '<span class="arrow reversible">⇌</span>'
    : '<span class="arrow">→</span>'
  const condStr = eq.conditions.length
    ? `<span class="conditions">${eq.conditions.join(' · ')}</span>`
    : ''
  return `<span class="reactants">${r.join(' + ')}</span> ${condStr} ${arrow} <span class="products">${p.join(' + ')}</span>`
}

// ===== Copy =====
function copyUnicode() { navigator.clipboard.writeText(unicode.value) }
function copyLatex() { navigator.clipboard.writeText(latex.value) }
function copyMhchem() { navigator.clipboard.writeText(latex.value) }

// ===== PNG Export =====
function exportPNG(scale: number) {
  const el = canvasRef.value
  if (!el) return
  const rect = el.getBoundingClientRect()
  const canvas = document.createElement('canvas')
  canvas.width = rect.width * scale
  canvas.height = rect.height * scale
  const ctx = canvas.getContext('2d')!
  ctx.scale(scale, scale)
  ctx.fillStyle = '#121218'
  ctx.fillRect(0, 0, rect.width, rect.height)
  // Render text
  ctx.font = '28px "Times New Roman", serif'
  ctx.fillStyle = '#e0e0e6'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(unicode.value, rect.width / 2, rect.height / 2)
  canvas.toBlob(b => {
    if (!b) return
    const a = document.createElement('a')
    a.href = URL.createObjectURL(b)
    a.download = `equation@${scale}x.png`
    a.click()
    URL.revokeObjectURL(a.href)
  }, 'image/png')
}
</script>

<style scoped>
.canvas-area {
  background: var(--bg-primary); border: 1px solid var(--border);
  border-radius: var(--radius-md); padding: 32px 24px;
  min-height: 80px; display: flex; align-items: center; justify-content: center;
}
.equation-display {
  font-family: 'Times New Roman', 'Cambria Math', serif;
  font-size: 28px; color: var(--text-primary); text-align: center;
}
.equation-display :deep(.coeff) { font-weight: 600; color: var(--accent); }
.equation-display :deep(.arrow) { margin: 0 12px; color: var(--text-secondary); }
.equation-display :deep(.arrow.reversible) { color: var(--warning); }
.equation-display :deep(.conditions) {
  font-size: 14px; color: var(--text-muted);
  display: block; margin: -4px 0 4px;
}
.equation-display :deep(.state) { font-size: 16px; color: var(--text-muted); }
.canvas-actions {
  display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap;
}
.mono-input { font-family: var(--font-mono); font-size: 16px; letter-spacing: 0.5px; }
.mono-result { font-family: var(--font-mono); word-break: break-all; }
code {
  background: var(--bg-tertiary); padding: 1px 5px; border-radius: 3px;
  font-family: var(--font-mono); font-size: 12px; color: var(--accent);
}
</style>
