<template>
  <div class="fade-in">
    <div class="page-header">
      <h1 class="page-title">🔮 分子空间结构</h1>
      <p class="page-subtitle">3D 可视化 · CIF 文件解析 · SVG/PNG 导出</p>
    </div>

    <div class="grid-2" style="gap: 16px;">
      <!-- Left: 3D Canvas -->
      <div class="card" style="padding: 0; overflow: hidden;">
        <div class="canvas-toolbar">
          <div class="tool-group">
            <button class="tool-btn" :class="{ active: mode === 'rotate' }" @click="mode = 'rotate'" title="旋转">🔄</button>
            <button class="tool-btn" :class="{ active: mode === 'zoom' }" @click="mode = 'zoom'" title="缩放">🔍</button>
          </div>
          <div class="tool-divider"></div>
          <div class="tool-group">
            <button class="tool-btn" @click="resetView" title="重置视角">↺</button>
            <button class="tool-btn" @click="toggleStyle" title="切换样式">{{ styleIcon }}</button>
          </div>
          <div class="tool-divider"></div>
          <label class="tool-btn" title="导入 CIF 文件" style="cursor: pointer;">
            📂<input type="file" accept=".cif,.xyz,.mol" @change="onFileLoad" style="display:none;" />
          </label>
        </div>
        <div class="viewer-3d" ref="viewerRef"
          @mousedown="onMouseDown" @mousemove="onMouseMove" @mouseup="onMouseUp"
          @wheel.prevent="onWheel">
          <div class="scene" :style="sceneStyle">
            <div v-for="(atom, i) in atoms" :key="'a'+i"
              class="atom-3d" :style="atomStyle(atom)">
              <div class="atom-label" v-if="showLabels">{{ atom.el }}</div>
            </div>
            <div v-for="(bond, i) in bonds" :key="'b'+i"
              class="bond-3d" :style="bondStyle(bond)">
            </div>
          </div>
        </div>
        <div class="viewer-info">
          <span>{{ atoms.length }} 个原子 · {{ bonds.length }} 个键</span>
          <span v-if="cellInfo"> · {{ cellInfo }}</span>
        </div>
      </div>

      <!-- Right: Info & Export -->
      <div>
        <div class="card">
          <div class="card-title">📋 分子信息</div>
          <div v-if="moleculeName" class="input-group">
            <label class="input-label">名称</label>
            <div class="result-box">{{ moleculeName }}</div>
          </div>
          <div class="input-group">
            <label class="input-label">化学式</label>
            <div class="result-box" style="font-size: 18px;">{{ formula || '—' }}</div>
          </div>
          <div class="input-group" v-if="cellParams">
            <label class="input-label">晶胞参数</label>
            <div class="result-box" style="font-family: var(--font-mono); font-size: 13px;">
              a={{ cellParams.a }}Å b={{ cellParams.b }}Å c={{ cellParams.c }}Å
              α={{ cellParams.alpha }}° β={{ cellParams.beta }}° γ={{ cellParams.gamma }}°
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-title">📤 导出</div>
          <div style="display: flex; flex-wrap: wrap; gap: 8px;">
            <button class="btn btn-primary btn-sm" @click="exportSVG">导出 SVG</button>
            <button class="btn btn-primary btn-sm" @click="exportPNG(2)">导出 PNG @2x</button>
            <button class="btn btn-primary btn-sm" @click="exportPNG(4)">导出 PNG @4x</button>
          </div>
          <div style="margin-top: 12px;">
            <button class="btn btn-secondary btn-sm" @click="copyCIF">复制 CIF 数据</button>
            <button class="btn btn-secondary btn-sm" style="margin-left: 8px;" @click="copyXYZ">复制 XYZ 格式</button>
          </div>
        </div>

        <div class="card">
          <div class="card-title">⚙️ 显示选项</div>
          <div class="setting-row">
            <span>显示原子标签</span>
            <div class="toggle" :class="{ active: showLabels }" @click="showLabels = !showLabels"></div>
          </div>
          <div class="setting-row">
            <span>显示氢原子</span>
            <div class="toggle" :class="{ active: showHydrogens }" @click="showHydrogens = !showHydrogens; rebuildScene()"></div>
          </div>
          <div class="setting-row">
            <span>原子缩放</span>
            <input type="range" min="0.3" max="2" step="0.1" v-model.number="atomScale" style="width: 120px;" />
          </div>
        </div>

        <div class="card">
          <div class="card-title">💡 操作提示</div>
          <div style="font-size: 12px; color: var(--text-secondary); line-height: 1.8;">
            <div>🖱 拖拽 → 旋转分子</div>
            <div>🖱 滚轮 → 缩放</div>
            <div>📂 支持 .cif / .xyz / .mol 格式</div>
            <div>📁 也可直接拖放文件到画布</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'

interface Atom3D { el: string; x: number; y: number; z: number }
interface Bond3D { from: number; to: number }

const viewerRef = ref<HTMLDivElement>()
const mode = ref('rotate')
const showLabels = ref(true)
const showHydrogens = ref(true)
const atomScale = ref(1)
const renderStyle = ref<'ball-stick' | 'space-fill' | 'wireframe'>('ball-stick')

const atoms = reactive<Atom3D[]>([])
const bonds = reactive<Bond3D[]>([])
const moleculeName = ref('')
const cellParams = ref<{ a: number; b: number; c: number; alpha: number; beta: number; gamma: number } | null>(null)
const rawCIF = ref('')

let rotX = ref(-20)
let rotY = ref(30)
let zoom = ref(1)
let dragging = false
let lastMouse = { x: 0, y: 0 }

const styleIcon = computed(() => {
  return renderStyle.value === 'ball-stick' ? '⚾' : renderStyle.value === 'space-fill' ? '🔵' : '🕸'
})

const cellInfo = computed(() => {
  if (!cellParams.value) return ''
  return `晶胞: ${cellParams.value.a}×${cellParams.value.b}×${cellParams.value.c} Å`
})

const formula = computed(() => {
  if (!atoms.length) return ''
  const counts: Record<string, number> = {}
  atoms.forEach(a => { counts[a.el] = (counts[a.el] || 0) + 1 })
  const keys = Object.keys(counts).sort((a, b) => {
    if (a === 'C') return -1; if (b === 'C') return 1
    if (a === 'H') return -1; if (b === 'H') return 1
    return a.localeCompare(b)
  })
  return keys.map(k => k + (counts[k] > 1 ? counts[k] : '')).join('')
})

const sceneStyle = computed(() => ({
  transform: `perspective(800px) rotateX(${rotX.value}deg) rotateY(${rotY.value}deg) scale(${zoom.value})`,
}))

const elemColors: Record<string, string> = {
  H: '#ffffff', C: '#555555', N: '#3050F8', O: '#FF0D0D', S: '#FFFF30',
  P: '#FF8000', Cl: '#1FF01F', F: '#90E050', Br: '#A62929', I: '#940094',
  Na: '#AB5CF2', K: '#8F40D4', Ca: '#3DFF00', Fe: '#E06633', Cu: '#C88033',
  Zn: '#7D80B0', Mg: '#8AFF00', Al: '#BFA6A6', Si: '#F0C8A0',
}

const elemRadii: Record<string, number> = {
  H: 0.31, C: 0.77, N: 0.71, O: 0.66, S: 1.05, P: 1.07,
  Cl: 1.02, F: 0.57, Br: 1.20, I: 1.39, Na: 1.66, K: 2.03,
  Ca: 1.76, Fe: 1.56, Cu: 1.45, Zn: 1.42, Mg: 1.41, Al: 1.21, Si: 1.11,
}

function atomColor(el: string) { return elemColors[el] || '#6c6cf0' }
function atomRadius(el: string) { return (elemRadii[el] || 1.2) * atomScale.value }

function atomStyle(atom: Atom3D) {
  const r = atomRadius(atom.el) * 18
  const color = atomColor(atom.el)
  const x = atom.x * 40
  const y = atom.y * 40
  const z = atom.z * 40
  return {
    transform: `translate3d(${x}px, ${y}px, ${z}px)`,
    width: `${r}px`, height: `${r}px`,
    marginLeft: `${-r/2}px`, marginTop: `${-r/2}px`,
    background: renderStyle.value === 'wireframe' ? 'transparent' : `radial-gradient(circle at 30% 30%, ${color}cc, ${color})`,
    border: renderStyle.value === 'wireframe' ? `1px solid ${color}` : 'none',
    borderRadius: '50%',
  }
}

function bondStyle(bond: Bond3D) {
  const a = atoms[bond.from], b = atoms[bond.to]
  if (!a || !b) return { display: 'none' }
  const dx = (b.x - a.x) * 40, dy = (b.y - a.y) * 40, dz = (b.z - a.z) * 40
  const len = Math.sqrt(dx*dx + dy*dy + dz*dz)
  const mx = (a.x + b.x) / 2 * 40, my = (a.y + b.y) / 2 * 40, mz = (a.z + b.z) / 2 * 40
  const rx = Math.atan2(dz, Math.sqrt(dx*dx + dy*dy)) * 180 / Math.PI
  const ry = -Math.atan2(dx, dy) * 180 / Math.PI
  return {
    transform: `translate3d(${mx}px, ${my}px, ${mz}px) rotateX(${rx}deg) rotateZ(${ry}deg)`,
    width: '3px', height: `${len}px`, marginLeft: '-1.5px', marginTop: `${-len/2}px`,
  }
}

// Mouse interaction
function onMouseDown(e: MouseEvent) { dragging = true; lastMouse = { x: e.clientX, y: e.clientY } }
function onMouseMove(e: MouseEvent) {
  if (!dragging) return
  const dx = e.clientX - lastMouse.x, dy = e.clientY - lastMouse.y
  rotY.value += dx * 0.5; rotX.value -= dy * 0.5
  lastMouse = { x: e.clientX, y: e.clientY }
}
function onMouseUp() { dragging = false }
function onWheel(e: WheelEvent) { zoom.value = Math.max(0.3, Math.min(3, zoom.value - e.deltaY * 0.001)) }
function resetView() { rotX.value = -20; rotY.value = 30; zoom.value = 1 }
function toggleStyle() {
  const styles: typeof renderStyle.value[] = ['ball-stick', 'space-fill', 'wireframe']
  renderStyle.value = styles[(styles.indexOf(renderStyle.value) + 1) % styles.length]
}
function rebuildScene() { /* triggers reactivity */ }

// CIF Parser
function parseCIF(text: string) {
  rawCIF.value = text
  atoms.splice(0); bonds.splice(0)
  cellParams.value = null

  const lines = text.split('\n')

  // Parse cell parameters
  for (const line of lines) {
    const m = line.match(/_cell_length_a\s+([\d.]+)/)
    if (m) { cellParams.value = cellParams.value || { a:0,b:0,c:0,alpha:0,beta:0,gamma:0 }; cellParams.value.a = parseFloat(m[1]) }
    const m2 = line.match(/_cell_length_b\s+([\d.]+)/)
    if (m2 && cellParams.value) cellParams.value.b = parseFloat(m2[1])
    const m3 = line.match(/_cell_length_c\s+([\d.]+)/)
    if (m3 && cellParams.value) cellParams.value.c = parseFloat(m3[1])
    const m4 = line.match(/_cell_angle_alpha\s+([\d.]+)/)
    if (m4 && cellParams.value) cellParams.value.alpha = parseFloat(m4[1])
    const m5 = line.match(/_cell_angle_beta\s+([\d.]+)/)
    if (m5 && cellParams.value) cellParams.value.beta = parseFloat(m5[1])
    const m6 = line.match(/_cell_angle_gamma\s+([\d.]+)/)
    if (m6 && cellParams.value) cellParams.value.gamma = parseFloat(m6[1])
  }

  // Parse atom_site loop
  let inAtomLoop = false
  let colMap: Record<string, number> = {}
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim()
    if (line === 'loop_' || line.startsWith('loop_')) { inAtomLoop = false; colMap = {}; continue }
    if (line.startsWith('_atom_site_')) {
      const col = line.replace('_atom_site_', '')
      colMap[col] = Object.keys(colMap).length
      inAtomLoop = true
      continue
    }
    if (inAtomLoop && line && !line.startsWith('_') && !line.startsWith('#') && !line.startsWith('loop_')) {
      const parts = line.split(/\s+/)
      if (parts.length < 3) continue
      const elIdx = colMap['type_symbol'] ?? colMap['label'] ?? 0
      const xIdx = colMap['fract_x'] ?? colMap['Cartn_x'] ?? 1
      const yIdx = colMap['fract_y'] ?? colMap['Cartn_y'] ?? 2
      const zIdx = colMap['fract_z'] ?? colMap['Cartn_z'] ?? 3
      const el = (parts[elIdx] || 'C').replace(/\d+/g, '')
      const x = parseFloat(parts[xIdx]) || 0
      const y = parseFloat(parts[yIdx]) || 0
      const z = parseFloat(parts[zIdx]) || 0
      if (!showHydrogens.value && el === 'H') continue
      atoms.push({ el, x: x * 5 - 2.5, y: y * 5 - 2.5, z: z * 5 - 2.5 })
    }
  }

  // Auto-generate bonds based on distance
  autoBond()
  moleculeName.value = extractCIFName(text)
}

function parseXYZ(text: string) {
  rawCIF.value = text
  atoms.splice(0); bonds.splice(0); cellParams.value = null
  const lines = text.trim().split('\n')
  const count = parseInt(lines[0]) || 0
  moleculeName.value = lines[1]?.trim() || 'Molecule'
  for (let i = 2; i < Math.min(lines.length, count + 2); i++) {
    const parts = lines[i].trim().split(/\s+/)
    if (parts.length < 4) continue
    const el = parts[0].replace(/\d+/g, '')
    const x = parseFloat(parts[1]), y = parseFloat(parts[2]), z = parseFloat(parts[3])
    if (!showHydrogens.value && el === 'H') continue
    atoms.push({ el, x: x / 2, y: y / 2, z: z / 2 })
  }
  autoBond()
}

function extractCIFName(text: string): string {
  const m = text.match(/_chemical_name_common\s+'?([^'\n]+)/)
  if (m) return m[1]
  const m2 = text.match(/_chemical_formula_sum\s+'?([^'\n]+)/)
  if (m2) return m2[1]
  return 'Molecule'
}

function autoBond() {
  const maxDist = 2.0
  for (let i = 0; i < atoms.length; i++) {
    for (let j = i + 1; j < atoms.length; j++) {
      const dx = atoms[i].x - atoms[j].x, dy = atoms[i].y - atoms[j].y, dz = atoms[i].z - atoms[j].z
      const dist = Math.sqrt(dx*dx + dy*dy + dz*dz) * 2
      const r1 = elemRadii[atoms[i].el] || 1.2, r2 = elemRadii[atoms[j].el] || 1.2
      if (dist < (r1 + r2) * 1.3 && dist < maxDist) {
        bonds.push({ from: i, to: j })
      }
    }
  }
}

function onFileLoad(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    const text = reader.result as string
    if (file.name.endsWith('.cif')) parseCIF(text)
    else parseXYZ(text)
  }
  reader.readAsText(file)
}

// Export
function exportSVG() {
  const svg = generateSVG()
  const blob = new Blob([svg], { type: 'image/svg+xml' })
  download(blob, `${moleculeName.value || 'structure'}.svg`)
}

function exportPNG(scale: number) {
  const svg = generateSVG()
  const img = new Image()
  const blob = new Blob([svg], { type: 'image/svg+xml;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  img.onload = () => {
    const canvas = document.createElement('canvas')
    canvas.width = 600 * scale; canvas.height = 440 * scale
    const ctx = canvas.getContext('2d')!
    ctx.fillStyle = '#121218'; ctx.fillRect(0, 0, canvas.width, canvas.height)
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
    canvas.toBlob(b => { if (b) download(b, `${moleculeName.value || 'structure'}@${scale}x.png`); URL.revokeObjectURL(url) }, 'image/png')
  }
  img.src = url
}

function generateSVG(): string {
  const w = 600, h = 440, cx = w/2, cy = h/2
  let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">`
  svg += `<rect width="${w}" height="${h}" fill="#121218"/>`
  const cosX = Math.cos(rotX.value * Math.PI/180), sinX = Math.sin(rotX.value * Math.PI/180)
  const cosY = Math.cos(rotY.value * Math.PI/180), sinY = Math.sin(rotY.value * Math.PI/180)
  const projected = atoms.map(a => {
    const x = a.x * 40, y = a.y * 40, z = a.z * 40
    const y2 = y * cosX - z * sinX, z2 = y * sinX + z * cosX
    const x2 = x * cosY + z2 * sinY
    return { x: cx + x2 * zoom.value, y: cy + y2 * zoom.value, z: z2, el: a.el }
  })
  for (const b of bonds) {
    const a = projected[b.from], bt = projected[b.to]
    if (a && bt) svg += `<line x1="${a.x}" y1="${a.y}" x2="${bt.x}" y2="${bt.y}" stroke="#666" stroke-width="2"/>`
  }
  for (const a of projected) {
    const r = atomRadius(a.el) * 10 * zoom.value
    svg += `<circle cx="${a.x}" cy="${a.y}" r="${r}" fill="${atomColor(a.el)}"/>`
    if (showLabels.value) svg += `<text x="${a.x}" y="${a.y-r-3}" text-anchor="middle" fill="#ccc" font-size="10">${a.el}</text>`
  }
  svg += '</svg>'
  return svg
}

function copyCIF() { if (rawCIF.value) navigator.clipboard.writeText(rawCIF.value) }
function copyXYZ() {
  let xyz = `${atoms.length}\n${moleculeName.value}\n`
  atoms.forEach(a => { xyz += `${a.el}  ${a.x*2}  ${a.y*2}  ${a.z*2}\n` })
  navigator.clipboard.writeText(xyz)
}

function download(blob: Blob, name: string) {
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = name; a.click(); URL.revokeObjectURL(a.href)
}

// Load demo molecule on mount
;(function initDemo() {
  const water = `2
Water molecule
O   0.000   0.000   0.117
H   0.000   0.757  -0.469
H   0.000  -0.757  -0.469`
  parseXYZ(water)
})()
</script>

<style scoped>
.viewer-3d {
  width: 100%; height: 440px; background: var(--bg-primary);
  border: none; overflow: hidden; cursor: grab; position: relative;
}
.viewer-3d:active { cursor: grabbing; }
.scene {
  position: absolute; top: 50%; left: 50%;
  transform-style: preserve-3d;
  transition: transform 0.05s linear;
}
.atom-3d {
  position: absolute; border-radius: 50%;
  transition: width 0.2s, height 0.2s;
}
.atom-label {
  position: absolute; top: -16px; left: 50%; transform: translateX(-50%);
  font-size: 10px; color: var(--text-secondary); white-space: nowrap;
  pointer-events: none;
}
.bond-3d {
  position: absolute; background: #666;
  transform-origin: center center;
}
.canvas-toolbar {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 12px; background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border);
}
.tool-group { display: flex; align-items: center; gap: 4px; }
.tool-divider { width: 1px; height: 20px; background: var(--border); margin: 0 4px; }
.tool-btn {
  width: 32px; height: 32px; border: none; border-radius: var(--radius-sm);
  background: transparent; color: var(--text-secondary); cursor: pointer;
  font-size: 14px; display: flex; align-items: center; justify-content: center;
  transition: all 0.15s;
}
.tool-btn:hover { background: var(--bg-hover); color: var(--text-primary); }
.tool-btn.active { background: var(--accent); color: white; }
.viewer-info {
  padding: 6px 12px; font-size: 11px; color: var(--text-muted);
  background: var(--bg-tertiary); border-top: 1px solid var(--border);
}
.setting-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 0; border-bottom: 1px solid var(--border); font-size: 13px;
}
.setting-row:last-child { border-bottom: none; }
</style>
