<template>
  <div class="fade-in">
    <div class="page-header">
      <h1 class="page-title">🔮 分子空间结构</h1>
      <p class="page-subtitle">3D 可视化 · CIF / XYZ 文件 · SVG / PNG 导出</p>
    </div>

    <div class="grid-2" style="gap: 16px;">
      <div class="card" style="padding: 0; overflow: hidden;">
        <div class="canvas-toolbar">
          <div class="tool-group">
            <button class="tool-btn" :class="{ active: style === 'ball-stick' }" @click="style='ball-stick'; render()" title="球棍模型">⚾</button>
            <button class="tool-btn" :class="{ active: style === 'space-fill' }" @click="style='space-fill'; render()" title="空间填充">🔵</button>
            <button class="tool-btn" :class="{ active: style === 'wireframe' }" @click="style='wireframe'; render()" title="线框">🕸</button>
          </div>
          <div class="tool-divider"></div>
          <button class="tool-btn" @click="resetView" title="重置视角">↺</button>
          <div class="tool-divider"></div>
          <label class="tool-btn" title="导入文件" style="cursor: pointer;">
            📂<input type="file" accept=".cif,.xyz,.mol" @change="onFileLoad" style="display:none;" />
          </label>
          <div class="tool-divider"></div>
          <div class="tool-group">
            <span style="font-size: 11px; color: var(--text-muted);">缩放</span>
            <input type="range" min="20" max="200" v-model.number="zoomPct" @input="render()" style="width: 80px;" />
          </div>
        </div>
        <canvas ref="canvasRef" class="viewer-canvas"
          @mousedown="onMouseDown" @mousemove="onMouseMove" @mouseup="onMouseUp" @mouseleave="onMouseUp"
          @wheel.prevent="onWheel"></canvas>
        <div class="viewer-info">
          <span>{{ atoms.length }} 原子 · {{ bonds.length }} 键</span>
          <span v-if="cellInfo"> · {{ cellInfo }}</span>
          <span v-if="moleculeName"> · {{ moleculeName }}</span>
        </div>
      </div>

      <div>
        <div class="card">
          <div class="card-title">📋 分子信息</div>
          <div class="input-group">
            <label class="input-label">化学式</label>
            <div class="result-box" style="font-size: 20px; font-family: 'Times New Roman', serif;">{{ formula || '—' }}</div>
          </div>
          <div class="input-group" v-if="cellParams">
            <label class="input-label">晶胞参数</label>
            <div class="result-box" style="font-family: var(--font-mono); font-size: 13px;">
              a={{ cellParams.a.toFixed(3) }}Å  b={{ cellParams.b.toFixed(3) }}Å  c={{ cellParams.c.toFixed(3) }}Å<br>
              α={{ cellParams.alpha.toFixed(1) }}°  β={{ cellParams.beta.toFixed(1) }}°  γ={{ cellParams.gamma.toFixed(1) }}°
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-title">📤 导出</div>
          <div style="display: flex; flex-wrap: wrap; gap: 8px;">
            <button class="btn btn-primary btn-sm" @click="exportSVG">导出 SVG</button>
            <button class="btn btn-primary btn-sm" @click="exportPNG(2)">PNG @2x</button>
            <button class="btn btn-primary btn-sm" @click="exportPNG(4)">PNG @4x</button>
          </div>
          <div style="margin-top: 12px;">
            <button class="btn btn-secondary btn-sm" @click="copyXYZ">复制 XYZ</button>
            <button class="btn btn-secondary btn-sm" style="margin-left: 8px;" @click="copyCIF">复制 CIF</button>
          </div>
        </div>

        <div class="card">
          <div class="card-title">⚙️ 显示选项</div>
          <div class="setting-row">
            <span>显示标签</span>
            <div class="toggle" :class="{ active: showLabels }" @click="showLabels = !showLabels; render()"></div>
          </div>
          <div class="setting-row">
            <span>显示氢原子</span>
            <div class="toggle" :class="{ active: showH }" @click="showH = !showH; rebuildMolecule()"></div>
          </div>
          <div class="setting-row">
            <span>原子半径缩放</span>
            <input type="range" min="30" max="200" v-model.number="radiusPct" @input="render()" style="width: 100px;" />
          </div>
        </div>

        <div class="card">
          <div class="card-title">💡 操作</div>
          <div style="font-size: 12px; color: var(--text-secondary); line-height: 2;">
            <div>🖱 左键拖拽 → 旋转</div>
            <div>🖱 滚轮 → 缩放</div>
            <div>📂 支持 .cif / .xyz 格式</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'

interface Atom { el: string; x: number; y: number; z: number }
interface Bond { a: number; b: number }

const canvasRef = ref<HTMLCanvasElement>()
const style = ref<'ball-stick' | 'space-fill' | 'wireframe'>('ball-stick')
const showLabels = ref(true)
const showH = ref(true)
const zoomPct = ref(80)
const radiusPct = ref(100)

const atoms = ref<Atom[]>([])
const bonds = ref<Bond[]>([])
const moleculeName = ref('')
const cellParams = ref<{a:number;b:number;c:number;alpha:number;beta:number;gamma:number} | null>(null)
const rawCIF = ref('')

let rotX = -0.4, rotY = 0.5
let dragging = false, lastX = 0, lastY = 0
let ctx: CanvasRenderingContext2D | null = null

const cellInfo = computed(() => cellParams.value ? `${cellParams.value.a.toFixed(1)}×${cellParams.value.b.toFixed(1)}×${cellParams.value.c.toFixed(1)} Å` : '')

const formula = computed(() => {
  if (!atoms.value.length) return ''
  const c: Record<string, number> = {}
  atoms.value.forEach(a => c[a.el] = (c[a.el] || 0) + 1)
  const order = ['C','H'].filter(k => c[k])
  Object.keys(c).sort().forEach(k => { if (!order.includes(k)) order.push(k) })
  return order.map(k => k + ((c[k] || 0) > 1 ? c[k] : '')).join('')
})

// ===== Element data =====
const COLORS: Record<string, string> = {
  H:'#FFFFFF', C:'#404040', N:'#3050F8', O:'#FF2020', S:'#FFFF30',
  P:'#FF8000', Cl:'#1FF01F', F:'#90E050', Br:'#A62929', I:'#940094',
  Na:'#AB5CF2', K:'#8F40D4', Ca:'#3DFF00', Fe:'#E06633', Cu:'#C88033',
  Zn:'#7D80B0', Mg:'#8AFF00', Al:'#BFA6A6', Si:'#F0C8A0', Ti:'#BFC2C7',
  Mn:'#9C7AC7', Cr:'#8A99C7', Ni:'#50D050', Ba:'#00C900', Ag:'#C0C0C0',
  Au:'#FFD123', Pb:'#575961', Sn:'#668080', Bi:'#9E4FB5',
}
const RADII: Record<string, number> = {
  H:0.31, C:0.77, N:0.71, O:0.66, S:1.05, P:1.07, Cl:1.02, F:0.57,
  Br:1.20, I:1.39, Na:1.66, K:2.03, Ca:1.76, Fe:1.56, Cu:1.45,
  Zn:1.42, Mg:1.41, Al:1.21, Si:1.11, Ti:1.76, Mn:1.61, Cr:1.66,
  Ni:1.49, Ba:2.15, Ag:1.65, Au:1.44, Pb:1.80, Sn:1.45, Bi:1.60,
}
function getColor(el: string) { return COLORS[el] || '#6c6cf0' }
function getRadius(el: string) { return (RADII[el] || 1.2) * (radiusPct.value / 100) }

// ===== 3D math =====
function rotate(p: [number,number,number], ax: number, ay: number): [number,number,number] {
  let [x,y,z] = p
  const cy=Math.cos(ay), sy=Math.sin(ay), cx=Math.cos(ax), sx=Math.sin(ax)
  const x1=x*cy+z*sy, z1=-x*sy+z*cy, y1=y*cx-z1*sx, z2=y*sx+z1*cx
  return [x1,y1,z2]
}

function project(p: [number,number,number], w: number, h: number): {px:number;py:number;depth:number} {
  const zoom = zoomPct.value / 50
  const fov = 6
  const z = p[2] + fov
  const scale = fov / z * Math.min(w, h) * zoom * 0.5
  return { px: w/2 + p[0]*scale, py: h/2 - p[1]*scale, depth: z }
}

// ===== Canvas rendering =====
function render() {
  const canvas = canvasRef.value
  if (!canvas) return
  const w = canvas.width, h = canvas.height
  if (!ctx) ctx = canvas.getContext('2d')!
  ctx.clearRect(0, 0, w, h)
  ctx.fillStyle = '#121218'
  ctx.fillRect(0, 0, w, h)

  if (!atoms.value.length) {
    ctx.fillStyle = '#606070'
    ctx.font = '14px sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText('导入 CIF 或 XYZ 文件查看 3D 结构', w/2, h/2)
    return
  }

  // Transform atoms
  const transformed = atoms.value.map(a => {
    const p = rotate([a.x, a.y, a.z], rotX, rotY)
    const proj = project(p, w, h)
    return { ...a, ...proj, p3: p }
  })

  // Draw bonds (back to front)
  for (const bond of bonds.value) {
    const a = transformed[bond.a], b = transformed[bond.b]
    if (!a || !b) continue
    const avgZ = (a.depth + b.depth) / 2
    const alpha = Math.max(0.3, Math.min(1, 1 / (avgZ * 0.3)))
    ctx.beginPath()
    ctx.moveTo(a.px, a.py)
    ctx.lineTo(b.px, b.py)
    ctx.strokeStyle = style.value === 'wireframe'
      ? `rgba(150,150,180,${alpha})`
      : `rgba(100,100,120,${alpha})`
    ctx.lineWidth = style.value === 'wireframe' ? 1 : 3
    ctx.stroke()
  }

  // Sort atoms by depth (back to front)
  const sorted = transformed.map((a, i) => ({ ...a, idx: i }))
    .sort((a, b) => b.depth - a.depth)

  // Draw atoms
  for (const atom of sorted) {
    const r = getRadius(atom.el)
    const scale = zoomPct.value / 50 * 6 / atom.depth * Math.min(w, h) * 0.02
    let drawR: number
    if (style.value === 'space-fill') drawR = r * 1.8 * scale
    else if (style.value === 'wireframe') drawR = r * 0.3 * scale
    else drawR = r * 0.8 * scale

    const color = getColor(atom.el)
    const alpha = Math.max(0.4, Math.min(1, 1.5 / atom.depth))

    // Sphere shading (Mercury-style)
    if (style.value !== 'wireframe') {
      const grad = ctx.createRadialGradient(
        atom.px - drawR * 0.3, atom.py - drawR * 0.3, drawR * 0.1,
        atom.px, atom.py, drawR
      )
      const rgb = hexToRgb(color)
      grad.addColorStop(0, `rgba(${Math.min(255,rgb.r+80)},${Math.min(255,rgb.g+80)},${Math.min(255,rgb.b+80)},${alpha})`)
      grad.addColorStop(0.6, `rgba(${rgb.r},${rgb.g},${rgb.b},${alpha})`)
      grad.addColorStop(1, `rgba(${Math.max(0,rgb.r-40)},${Math.max(0,rgb.g-40)},${Math.max(0,rgb.b-40)},${alpha})`)
      ctx.beginPath()
      ctx.arc(atom.px, atom.py, drawR, 0, Math.PI * 2)
      ctx.fillStyle = grad
      ctx.fill()
      // Edge highlight
      ctx.strokeStyle = `rgba(255,255,255,${alpha * 0.15})`
      ctx.lineWidth = 1
      ctx.stroke()
    } else {
      ctx.beginPath()
      ctx.arc(atom.px, atom.py, drawR, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(${hexToRgb(color).r},${hexToRgb(color).g},${hexToRgb(color).b},${alpha})`
      ctx.fill()
    }

    // Label
    if (showLabels.value && drawR > 6) {
      ctx.fillStyle = `rgba(255,255,255,${Math.max(0.5, alpha)})`
      ctx.font = `${Math.max(9, Math.min(14, drawR))}px sans-serif`
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText(atom.el, atom.px, atom.py)
    }
  }
}

function hexToRgb(hex: string): {r:number;g:number;b:number} {
  const m = hex.match(/^#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i)
  if (!m) return {r:108,g:108,b:240}
  return { r: parseInt(m[1],16), g: parseInt(m[2],16), b: parseInt(m[3],16) }
}

// ===== Mouse interaction =====
function onMouseDown(e: MouseEvent) {
  dragging = true; lastX = e.clientX; lastY = e.clientY
}
function onMouseMove(e: MouseEvent) {
  if (!dragging) return
  rotY += (e.clientX - lastX) * 0.01
  rotX += (e.clientY - lastY) * 0.01
  lastX = e.clientX; lastY = e.clientY
  render()
}
function onMouseUp() { dragging = false }
function onWheel(e: WheelEvent) {
  zoomPct.value = Math.max(20, Math.min(200, zoomPct.value - e.deltaY * 0.05))
  render()
}
function resetView() { rotX = -0.4; rotY = 0.5; zoomPct.value = 80; render() }

// ===== File parsing =====
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

function parseCIF(text: string) {
  rawCIF.value = text
  const newAtoms: Atom[] = []
  const lines = text.split('\n')

  // Cell parameters
  let cp = {a:1,b:1,c:1,alpha:90,beta:90,gamma:90}
  for (const line of lines) {
    const ma = line.match(/_cell_length_a\s+([\d.]+)/)
    if (ma) cp.a = parseFloat(ma[1])
    const mb = line.match(/_cell_length_b\s+([\d.]+)/)
    if (mb) cp.b = parseFloat(mb[1])
    const mc = line.match(/_cell_length_c\s+([\d.]+)/)
    if (mc) cp.c = parseFloat(mc[1])
    const mα = line.match(/_cell_angle_alpha\s+([\d.]+)/)
    if (mα) cp.alpha = parseFloat(mα[1])
    const mβ = line.match(/_cell_angle_beta\s+([\d.]+)/)
    if (mβ) cp.beta = parseFloat(mβ[1])
    const mγ = line.match(/_cell_angle_gamma\s+([\d.]+)/)
    if (mγ) cp.gamma = parseFloat(mγ[1])
  }
  cellParams.value = cp

  // Parse atom_site loop
  let inLoop = false, cols: Record<string, number> = {}
  for (const line of lines) {
    const t = line.trim()
    if (t.startsWith('loop_')) { inLoop = false; cols = {}; continue }
    if (t.startsWith('_atom_site_')) {
      cols[t.replace('_atom_site_', '')] = Object.keys(cols).length
      inLoop = true; continue
    }
    if (inLoop && t && !t.startsWith('_') && !t.startsWith('#')) {
      const p = t.split(/\s+/)
      if (p.length < 4) continue
      const el = (p[cols['type_symbol'] ?? cols['label'] ?? 0] || 'C').replace(/\d+/g,'')
      if (!showH.value && el === 'H') continue
      const fx = parseFloat(p[cols['fract_x'] ?? cols['Cartn_x'] ?? 1]) || 0
      const fy = parseFloat(p[cols['fract_y'] ?? cols['Cartn_y'] ?? 2]) || 0
      const fz = parseFloat(p[cols['fract_z'] ?? cols['Cartn_z'] ?? 3]) || 0
      // Convert fractional to Cartesian using full cell parameters
      const alphaRad = cp.alpha * Math.PI / 180
      const betaRad = cp.beta * Math.PI / 180
      const gammaRad = cp.gamma * Math.PI / 180
      const cosAlpha = Math.cos(alphaRad), cosBeta = Math.cos(betaRad), cosGamma = Math.cos(gammaRad)
      const sinGamma = Math.sin(gammaRad)
      // Volume factor
      const v = Math.sqrt(1 - cosAlpha*cosAlpha - cosBeta*cosBeta - cosGamma*cosGamma + 2*cosAlpha*cosBeta*cosGamma)
      const x = cp.a * fx + cp.b * cosGamma * fy + cp.c * cosBeta * fz
      const y = cp.b * sinGamma * fy + cp.c * (cosAlpha - cosBeta*cosGamma)/sinGamma * fz
      const z = cp.c * v/sinGamma * fz
      newAtoms.push({ el, x: x/2 - cp.a/4, y: y/2 - cp.b/4, z: z/2 - cp.c/4 })
    }
  }

  atoms.value = newAtoms
  moleculeName.value = extractName(text)
  autoBond()
  render()
}

function parseXYZ(text: string) {
  rawCIF.value = text; cellParams.value = null
  const lines = text.trim().split('\n')
  const count = parseInt(lines[0]) || 0
  moleculeName.value = lines[1]?.trim() || 'Molecule'
  const newAtoms: Atom[] = []
  for (let i = 2; i < Math.min(lines.length, count + 2); i++) {
    const p = lines[i].trim().split(/\s+/)
    if (p.length < 4) continue
    const el = p[0].replace(/\d+/g, '')
    if (!showH.value && el === 'H') continue
    newAtoms.push({ el, x: parseFloat(p[1])/1, y: parseFloat(p[2])/1, z: parseFloat(p[3])/1 })
  }
  // Center
  if (newAtoms.length) {
    let cx=0,cy=0,cz=0
    newAtoms.forEach(a => { cx+=a.x; cy+=a.y; cz+=a.z })
    cx/=newAtoms.length; cy/=newAtoms.length; cz/=newAtoms.length
    newAtoms.forEach(a => { a.x-=cx; a.y-=cy; a.z-=cz })
  }
  atoms.value = newAtoms
  autoBond()
  render()
}

function extractName(text: string): string {
  const m = text.match(/_chemical_name_common\s+'?([^'\n]+)/)
  if (m) return m[1].trim()
  const m2 = text.match(/_chemical_formula_sum\s+'?([^'\n]+)/)
  if (m2) return m2[1].trim()
  return ''
}

function autoBond() {
  const newBonds: Bond[] = []
  const aa = atoms.value
  for (let i = 0; i < aa.length; i++) {
    for (let j = i+1; j < aa.length; j++) {
      const dx=aa[i].x-aa[j].x, dy=aa[i].y-aa[j].y, dz=aa[i].z-aa[j].z
      const dist = Math.sqrt(dx*dx+dy*dy+dz*dz)
      const r1 = RADII[aa[i].el]||1.2, r2 = RADII[aa[j].el]||1.2
      if (dist < (r1+r2)*1.4 && dist < 3.0) {
        newBonds.push({a:i, b:j})
      }
    }
  }
  bonds.value = newBonds
}

function rebuildMolecule() {
  if (rawCIF.value) {
    if (cellParams.value) parseCIF(rawCIF.value)
    else parseXYZ(rawCIF.value)
  }
}

// ===== Export =====
function exportSVG() {
  const canvas = canvasRef.value
  if (!canvas) return
  const svg = canvasToSVG(canvas)
  download(new Blob([svg], {type:'image/svg+xml'}), `${moleculeName.value||'structure'}.svg`)
}

function exportPNG(scale: number) {
  const canvas = canvasRef.value
  if (!canvas) return
  const c = document.createElement('canvas')
  c.width = canvas.width * scale; c.height = canvas.height * scale
  const cx = c.getContext('2d')!
  cx.scale(scale, scale)
  cx.drawImage(canvas, 0, 0)
  c.toBlob(b => { if(b) download(b, `${moleculeName.value||'structure'}@${scale}x.png`) }, 'image/png')
}

function canvasToSVG(canvas: HTMLCanvasElement): string {
  const w = canvas.width, h = canvas.height
  let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}">`
  svg += `<rect width="${w}" height="${h}" fill="#121218"/>`
  // Re-render as SVG using same projection
  const transformed = atoms.value.map(a => {
    const p = rotate([a.x,a.y,a.z], rotX, rotY)
    const proj = project(p, w, h)
    return { ...a, ...proj }
  })
  for (const bond of bonds.value) {
    const a = transformed[bond.a], b = transformed[bond.b]
    if (a&&b) svg += `<line x1="${a.px}" y1="${a.py}" x2="${b.px}" y2="${b.py}" stroke="#666" stroke-width="2"/>`
  }
  for (const a of transformed) {
    const r = getRadius(a.el) * 8 * zoomPct.value / 100
    svg += `<circle cx="${a.px}" cy="${a.py}" r="${r}" fill="${getColor(a.el)}"/>`
    if (showLabels.value) svg += `<text x="${a.px}" y="${a.py-r-2}" text-anchor="middle" fill="#ccc" font-size="10">${a.el}</text>`
  }
  svg += '</svg>'
  return svg
}

function copyXYZ() {
  let xyz = `${atoms.value.length}\n${moleculeName.value}\n`
  atoms.value.forEach(a => { xyz += `${a.el}  ${a.x.toFixed(4)}  ${a.y.toFixed(4)}  ${a.z.toFixed(4)}\n` })
  navigator.clipboard.writeText(xyz)
}
function copyCIF() { if (rawCIF.value) navigator.clipboard.writeText(rawCIF.value) }
function download(blob: Blob, name: string) {
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = name; a.click(); URL.revokeObjectURL(a.href)
}

// ===== Init =====
onMounted(async () => {
  await nextTick()
  const canvas = canvasRef.value
  if (!canvas) return
  const parent = canvas.parentElement!
  canvas.width = parent.clientWidth
  canvas.height = 440
  ctx = canvas.getContext('2d')
  // Load demo: ethanol (C2H5OH)
  parseXYZ(`9
Ethanol
C  -0.756  -0.015   0.024
C   0.756   0.015  -0.024
O   1.168   1.410  -0.149
H  -1.163  -0.541   0.891
H  -1.121  -0.499  -0.877
H  -1.082   1.020   0.073
H   1.163   0.541  -0.891
H   1.121   0.499   0.877
H   2.128   1.440  -0.166`)
})
</script>

<style scoped>
.viewer-canvas {
  width: 100%; height: 440px; display: block; cursor: grab;
  background: var(--bg-primary);
}
.viewer-canvas:active { cursor: grabbing; }
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
