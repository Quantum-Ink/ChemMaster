<template>
  <div class="fade-in">
    <div class="page-header">
      <h1 class="page-title">🧬 分子编辑器</h1>
      <p class="page-subtitle">绘制分子结构 — SVG / PNG 导出</p>
    </div>

    <div class="grid-2">
      <!-- Left: Canvas -->
      <div class="card">
        <div class="card-title">🎨 画布</div>
        <div class="toolbar">
          <div class="tab-bar" style="margin-bottom: 0;">
            <div class="tab-item" :class="{ active: tool === 'atom' }" @click="tool = 'atom'">原子</div>
            <div class="tab-item" :class="{ active: tool === 'bond' }" @click="tool = 'bond'">键</div>
            <div class="tab-item" :class="{ active: tool === 'select' }" @click="tool = 'select'">选择</div>
            <div class="tab-item" :class="{ active: tool === 'eraser' }" @click="tool = 'eraser'">橡皮擦</div>
          </div>
          <div v-if="tool === 'atom'" class="atom-select">
            <span v-for="a in commonAtoms" :key="a"
              class="atom-btn" :class="{ active: selectedAtom === a }"
              @click="selectedAtom = a">{{ a }}</span>
          </div>
          <div v-if="tool === 'bond'" class="atom-select">
            <span v-for="b in bondTypes" :key="b.value"
              class="atom-btn" :class="{ active: bondType === b.value }"
              @click="bondType = b.value">{{ b.label }}</span>
          </div>
        </div>
        <svg ref="canvas" class="mol-canvas"
          @mousedown="onMouseDown" @mousemove="onMouseMove" @mouseup="onMouseUp"
          @contextmenu.prevent>
          <g v-for="bond in bonds" :key="'b'+bond.id">
            <line v-if="bond.type === 'single'"
              :x1="getAtom(bond.from).x" :y1="getAtom(bond.from).y"
              :x2="getAtom(bond.to).x" :y2="getAtom(bond.to).y"
              stroke="var(--text-primary)" stroke-width="2" />
            <g v-else-if="bond.type === 'double'">
              <line :x1="getAtom(bond.from).x-3" :y1="getAtom(bond.from).y+3"
                :x2="getAtom(bond.to).x-3" :y2="getAtom(bond.to).y+3"
                stroke="var(--text-primary)" stroke-width="2" />
              <line :x1="getAtom(bond.from).x+3" :y1="getAtom(bond.from).y-3"
                :x2="getAtom(bond.to).x+3" :y2="getAtom(bond.to).y-3"
                stroke="var(--text-primary)" stroke-width="2" />
            </g>
            <g v-else-if="bond.type === 'triple'">
              <line :x1="getAtom(bond.from).x" :y1="getAtom(bond.from).y"
                :x2="getAtom(bond.to).x" :y2="getAtom(bond.to).y"
                stroke="var(--text-primary)" stroke-width="2" />
              <line :x1="getAtom(bond.from).x-5" :y1="getAtom(bond.from).y+5"
                :x2="getAtom(bond.to).x-5" :y2="getAtom(bond.to).y+5"
                stroke="var(--text-primary)" stroke-width="2" />
              <line :x1="getAtom(bond.from).x+5" :y1="getAtom(bond.from).y-5"
                :x2="getAtom(bond.to).x+5" :y2="getAtom(bond.to).y-5"
                stroke="var(--text-primary)" stroke-width="2" />
            </g>
          </g>
          <g v-for="atom in atoms" :key="'a'+atom.id">
            <circle :cx="atom.x" :cy="atom.y" r="18"
              :fill="selectedAtoms.has(atom.id) ? 'var(--accent-dim)' : 'var(--bg-card)'"
              :stroke="selectedAtoms.has(atom.id) ? 'var(--accent)' : 'var(--border)'"
              stroke-width="1.5" />
            <text :x="atom.x" :y="atom.y" text-anchor="middle" dominant-baseline="central"
              :fill="atomColor(atom.symbol)" font-size="14" font-weight="600">{{ atom.symbol }}</text>
          </g>
          <line v-if="drawingBond" :x1="drawingBond.x1" :y1="drawingBond.y1"
            :x2="drawingBond.x2" :y2="drawingBond.y2"
            stroke="var(--accent)" stroke-width="2" stroke-dasharray="4,4" />
        </svg>
      </div>

      <!-- Right: Info + Export -->
      <div>
        <div class="card">
          <div class="card-title">📋 分子信息</div>
          <div class="input-group">
            <label class="input-label">分子式</label>
            <div class="result-box" style="font-size: 18px;">{{ molecularFormula || '—' }}</div>
          </div>
          <div class="input-group">
            <label class="input-label">分子量</label>
            <div class="result-box" style="font-size: 18px;">{{ molecularWeight ? molecularWeight + ' g/mol' : '—' }}</div>
          </div>
          <div class="input-group">
            <label class="input-label">元素组成</label>
            <div class="chip-group">
              <span v-for="(count, elem) in composition" :key="elem" class="chip">{{ elem }}: {{ count }}</span>
              <span v-if="!Object.keys(composition).length" style="color: var(--text-muted); font-size: 13px;">在画布上绘制分子</span>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-title">📤 导出</div>
          <div class="export-row">
            <button class="btn btn-primary btn-sm" @click="exportSVG">导出 SVG</button>
            <button class="btn btn-primary btn-sm" @click="exportPNG(2)">导出 PNG 2x</button>
            <button class="btn btn-primary btn-sm" @click="exportPNG(4)">导出 PNG 4x</button>
          </div>
          <div class="input-group" style="margin-top: 12px;">
            <label class="input-label">LaTeX (mhchem)</label>
            <div class="result-box" style="font-size: 14px;">{{ latexCode || '—' }}</div>
            <button v-if="latexCode" class="btn btn-secondary btn-sm" style="margin-top: 8px;" @click="copyText(latexCode)">复制 LaTeX</button>
          </div>
          <div class="input-group">
            <label class="input-label">Word 格式 (Unicode下标)</label>
            <div class="result-box" style="font-size: 14px;">{{ unicodeFormula || '—' }}</div>
            <button v-if="unicodeFormula" class="btn btn-secondary btn-sm" style="margin-top: 8px;" @click="copyText(unicodeFormula)">复制到 Word</button>
          </div>
        </div>

        <div class="card">
          <div class="card-title">🗑️ 操作</div>
          <div style="display: flex; gap: 8px;">
            <button class="btn btn-secondary btn-sm" @click="undo">撤销</button>
            <button class="btn btn-secondary btn-sm" @click="clearAll">清空画布</button>
            <button class="btn btn-secondary btn-sm" @click="loadTemplate('water')">水</button>
            <button class="btn btn-secondary btn-sm" @click="loadTemplate('ethanol')">乙醇</button>
            <button class="btn btn-secondary btn-sm" @click="loadTemplate('benzene')">苯</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { getAllElements } from '../wails/app'

interface MolAtom { id: number; symbol: string; x: number; y: number }
interface MolBond { id: number; from: number; to: number; type: string }

const tool = ref('atom')
const selectedAtom = ref('C')
const bondType = ref('single')
const atoms = reactive<MolAtom[]>([])
const bonds = reactive<MolBond[]>([])
const selectedAtoms = reactive(new Set<number>())
const drawingBond = ref<{ x1: number; y1: number; x2: number; y2: number } | null>(null)

let nextId = 1
let dragFrom: MolAtom | null = null
let dragOffset = { x: 0, y: 0 }

const commonAtoms = ['C', 'H', 'O', 'N', 'S', 'P', 'F', 'Cl', 'Br', 'I', 'Na', 'K', 'Ca', 'Fe', 'Cu', 'Zn']
const bondTypes = [
  { label: '—', value: 'single' },
  { label: '=', value: 'double' },
  { label: '≡', value: 'triple' },
]

const elementMasses: Record<string, number> = {}

onMounted(async () => {
  const all = await getAllElements() as any[]
  if (all) {
    for (const e of all) {
      elementMasses[e.symbol] = e.atomicMass
    }
  }
})

function getAtom(id: number): MolAtom {
  return atoms.find(a => a.id === id) || { id: 0, symbol: '?', x: 0, y: 0 }
}

function atomColor(symbol: string): string {
  const colors: Record<string, string> = {
    O: '#f87171', N: '#60a5fa', S: '#fbbf24', P: '#f59e0b',
    Cl: '#4ade80', Br: '#a855f7', I: '#8b5cf6', F: '#34d399',
    H: '#e0e0e6', Na: '#f472b6', K: '#c084fc', Ca: '#818cf8',
    Fe: '#fb923c', Cu: '#f97316',
  }
  return colors[symbol] || 'var(--text-primary)'
}

const composition = computed(() => {
  const map: Record<string, number> = {}
  atoms.forEach(a => { map[a.symbol] = (map[a.symbol] || 0) + 1 })
  return map
})

const molecularFormula = computed(() => {
  // Hill system: C first, H second, then alphabetical
  const c = composition.value
  const keys = Object.keys(c).sort((a, b) => {
    if (a === 'C') return -1; if (b === 'C') return 1
    if (a === 'H') return -1; if (b === 'H') return 1
    return a.localeCompare(b)
  })
  return keys.map(k => k + (c[k] > 1 ? c[k] : '')).join('')
})

const molecularWeight = computed(() => {
  let mw = 0
  for (const [elem, count] of Object.entries(composition.value)) {
    mw += (elementMasses[elem] || 0) * count
  }
  return mw ? Math.round(mw * 1000) / 1000 : 0
})

const unicodeFormula = computed(() => {
  if (!molecularFormula.value) return ''
  return molecularFormula.value.replace(/(\d+)/g, (_, d) => {
    const subs = '₀₁₂₃₄₅₆₇₈₉'
    return d.split('').map((c: string) => subs[parseInt(c)]).join('')
  })
})

const latexCode = computed(() => {
  if (!molecularFormula.value) return ''
  return `\\ce{${molecularFormula.value}}`
})

function getSVGPos(e: MouseEvent): { x: number; y: number } {
  const svg = document.querySelector('.mol-canvas') as SVGSVGElement
  const rect = svg.getBoundingClientRect()
  return { x: e.clientX - rect.left, y: e.clientY - rect.top }
}

function findAtomAt(x: number, y: number, exclude?: number): MolAtom | null {
  return atoms.find(a => a.id !== exclude && Math.hypot(a.x - x, a.y - y) < 24) || null
}

function onMouseDown(e: MouseEvent) {
  const pos = getSVGPos(e)
  const hit = findAtomAt(pos.x, pos.y)

  if (tool.value === 'atom') {
    if (!hit) {
      atoms.push({ id: nextId++, symbol: selectedAtom.value, x: pos.x, y: pos.y })
    } else {
      hit.symbol = selectedAtom.value
    }
  } else if (tool.value === 'bond') {
    if (hit) {
      dragFrom = hit
      drawingBond.value = { x1: hit.x, y1: hit.y, x2: hit.x, y2: hit.y }
    }
  } else if (tool.value === 'select') {
    if (hit) {
      if (selectedAtoms.has(hit.id)) {
        selectedAtoms.delete(hit.id)
      } else {
        selectedAtoms.add(hit.id)
      }
    }
  } else if (tool.value === 'eraser') {
    if (hit) {
      removeAtom(hit.id)
    }
  }
}

function onMouseMove(e: MouseEvent) {
  if (dragFrom && drawingBond.value) {
    const pos = getSVGPos(e)
    drawingBond.value.x2 = pos.x
    drawingBond.value.y2 = pos.y
  }
}

function onMouseUp(e: MouseEvent) {
  if (dragFrom) {
    const pos = getSVGPos(e)
    const target = findAtomAt(pos.x, pos.y, dragFrom.id)
    if (target) {
      const exists = bonds.find(b =>
        (b.from === dragFrom!.id && b.to === target.id) ||
        (b.from === target.id && b.to === dragFrom!.id)
      )
      if (!exists) {
        bonds.push({ id: nextId++, from: dragFrom.id, to: target.id, type: bondType.value })
      } else {
        exists.type = bondType.value
      }
    }
    dragFrom = null
    drawingBond.value = null
  }
}

function removeAtom(id: number) {
  const idx = atoms.findIndex(a => a.id === id)
  if (idx >= 0) atoms.splice(idx, 1)
  for (let i = bonds.length - 1; i >= 0; i--) {
    if (bonds[i].from === id || bonds[i].to === id) bonds.splice(i, 1)
  }
  selectedAtoms.delete(id)
}

function undo() {
  if (bonds.length > 0) {
    bonds.pop()
  } else if (atoms.length > 0) {
    const last = atoms.pop()!
    selectedAtoms.delete(last.id)
  }
}

function clearAll() {
  atoms.length = 0
  bonds.length = 0
  selectedAtoms.clear()
  nextId = 1
}

function loadTemplate(name: string) {
  clearAll()
  const cx = 250, cy = 150, r = 60
  if (name === 'water') {
    const o = nextId++
    const h1 = nextId++
    const h2 = nextId++
    atoms.push(
      { id: o, symbol: 'O', x: cx, y: cy },
      { id: h1, symbol: 'H', x: cx - 40, y: cy + 35 },
      { id: h2, symbol: 'H', x: cx + 40, y: cy + 35 },
    )
    bonds.push(
      { id: nextId++, from: o, to: h1, type: 'single' },
      { id: nextId++, from: o, to: h2, type: 'single' },
    )
  } else if (name === 'ethanol') {
    const c1 = nextId++, c2 = nextId++, o = nextId++, h = nextId++
    atoms.push(
      { id: c1, symbol: 'C', x: cx - 40, y: cy },
      { id: c2, symbol: 'C', x: cx + 40, y: cy },
      { id: o, symbol: 'O', x: cx + 100, y: cy },
      { id: h, symbol: 'H', x: cx + 140, y: cy + 30 },
    )
    for (let i = 0; i < 3; i++) {
      const hid = nextId++
      atoms.push({ id: hid, symbol: 'H', x: cx - 80 + i * 15, y: cy - 30 - i * 10 })
      bonds.push({ id: nextId++, from: c1, to: hid, type: 'single' })
    }
    for (let i = 0; i < 2; i++) {
      const hid = nextId++
      atoms.push({ id: hid, symbol: 'H', x: cx + 40 + i * 15, y: cy - 30 - i * 10 })
      bonds.push({ id: nextId++, from: c2, to: hid, type: 'single' })
    }
    bonds.push(
      { id: nextId++, from: c1, to: c2, type: 'single' },
      { id: nextId++, from: c2, to: o, type: 'single' },
      { id: nextId++, from: o, to: h, type: 'single' },
    )
  } else if (name === 'benzene') {
    const ids: number[] = []
    for (let i = 0; i < 6; i++) {
      const angle = (Math.PI / 3) * i - Math.PI / 2
      const id = nextId++
      ids.push(id)
      atoms.push({ id, symbol: 'C', x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) })
    }
    for (let i = 0; i < 6; i++) {
      bonds.push({ id: nextId++, from: ids[i], to: ids[(i + 1) % 6], type: i % 2 === 0 ? 'double' : 'single' })
      const hId = nextId++
      const angle = (Math.PI / 3) * i - Math.PI / 2
      atoms.push({ id: hId, symbol: 'H', x: cx + (r + 30) * Math.cos(angle), y: cy + (r + 30) * Math.sin(angle) })
      bonds.push({ id: nextId++, from: ids[i], to: hId, type: 'single' })
    }
  }
}

function getSVGString(): string {
  const svg = document.querySelector('.mol-canvas') as SVGSVGElement
  const clone = svg.cloneNode(true) as SVGSVGElement
  // Replace CSS vars with actual colors for export
  const html = clone.outerHTML
    .replace(/var\(--text-primary\)/g, '#e0e0e6')
    .replace(/var\(--accent\)/g, '#6c6cf0')
    .replace(/var\(--accent-dim\)/g, 'rgba(108,108,240,0.15)')
    .replace(/var\(--bg-card\)/g, '#1e1e2a')
    .replace(/var\(--border\)/g, '#2a2a3a')
  return `<?xml version="1.0" encoding="UTF-8"?>\n${html}`
}

function exportSVG() {
  const svg = getSVGString()
  const blob = new Blob([svg], { type: 'image/svg+xml' })
  downloadBlob(blob, `molecule_${Date.now()}.svg`)
}

function exportPNG(scale: number) {
  const svg = getSVGString()
  const canvas = document.createElement('canvas')
  const svgEl = document.querySelector('.mol-canvas') as SVGSVGElement
  canvas.width = svgEl.clientWidth * scale
  canvas.height = svgEl.clientHeight * scale
  const ctx = canvas.getContext('2d')!
  const img = new Image()
  const blob = new Blob([svg], { type: 'image/svg+xml;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  img.onload = () => {
    ctx.fillStyle = '#121218'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
    canvas.toBlob(b => {
      if (b) downloadBlob(b, `molecule_${scale}x_${Date.now()}.png`)
      URL.revokeObjectURL(url)
    }, 'image/png')
  }
  img.src = url
}

function downloadBlob(blob: Blob, filename: string) {
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = filename
  a.click()
  URL.revokeObjectURL(a.href)
}

function copyText(text: string) {
  navigator.clipboard.writeText(text)
}
</script>

<style scoped>
.toolbar {
  display: flex; flex-direction: column; gap: 8px; margin-bottom: 12px;
}
.atom-select {
  display: flex; flex-wrap: wrap; gap: 6px;
}
.atom-btn {
  padding: 4px 10px; border-radius: 6px; font-size: 13px; font-weight: 500;
  background: var(--bg-tertiary); color: var(--text-secondary);
  cursor: pointer; transition: all 0.15s; border: 1px solid var(--border);
}
.atom-btn:hover { background: var(--bg-hover); color: var(--text-primary); }
.atom-btn.active {
  background: var(--accent-dim); border-color: var(--accent); color: var(--accent);
}
.mol-canvas {
  width: 100%; height: 400px; background: var(--bg-primary);
  border: 1px solid var(--border); border-radius: var(--radius-md);
  cursor: crosshair;
}
</style>
