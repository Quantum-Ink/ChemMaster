<template>
  <div class="fade-in">
    <div class="page-header">
      <h1 class="page-title">🧪 化学反应表达</h1>
      <p class="page-subtitle">Reaction AST — 支持可逆反应、条件标注、状态标记、三种方程式输出</p>
    </div>

    <div class="card">
      <div class="card-title">输入反应方程式</div>
      <div class="input-row">
        <div class="input-group">
          <input
            v-model="input"
            class="input-field"
            placeholder="AgNO3 + NaCl -> AgCl↓ + NaNO3"
            @keyup.enter="process"
            autofocus
          />
        </div>
        <button class="btn btn-primary" @click="process">分析</button>
        <button class="btn btn-ghost" @click="clear">清除</button>
      </div>
    </div>

    <div v-if="result" class="fade-in">
      <!-- Reaction AST -->
      <div class="card" v-if="result.ast">
        <div class="card-title">🌳 Reaction AST</div>
        <div class="grid-2">
          <div>
            <div class="input-label">反应物 (Reactants)</div>
            <div v-for="(r, i) in result.ast.reactants" :key="i" class="result-box" style="margin-bottom: 6px; padding: 8px 12px; font-size: 14px;">
              <span v-if="r.coefficient > 1" style="color: var(--accent);">{{ r.coefficient }}</span>
              {{ r.formula }}
              <span v-if="r.state" style="color: var(--text-muted);">({{ r.state }})</span>
              <span v-if="r.isGas" style="color: var(--warning);"> ↑</span>
              <span v-if="r.isPpt" style="color: var(--info);"> ↓</span>
            </div>
          </div>
          <div>
            <div class="input-label">生成物 (Products)</div>
            <div v-for="(p, i) in result.ast.products" :key="i" class="result-box" style="margin-bottom: 6px; padding: 8px 12px; font-size: 14px;">
              <span v-if="p.coefficient > 1" style="color: var(--accent);">{{ p.coefficient }}</span>
              {{ p.formula }}
              <span v-if="p.state" style="color: var(--text-muted);">({{ p.state }})</span>
              <span v-if="p.isGas" style="color: var(--warning);"> ↑</span>
              <span v-if="p.isPpt" style="color: var(--info);"> ↓</span>
            </div>
          </div>
        </div>
        <div style="margin-top: 12px; display: flex; gap: 16px;">
          <span class="input-label" style="margin: 0;">可逆: {{ result.ast.reversible ? '是 ⇌' : '否 →' }}</span>
          <span class="input-label" style="margin: 0;">分隔符: {{ result.ast.separator }}</span>
        </div>
      </div>

      <!-- Output Formats -->
      <div class="card">
        <div class="card-title">📤 输出格式</div>
        <div class="tab-bar">
          <div class="tab-item" :class="{ active: viewMode === 'molecular' }" @click="viewMode = 'molecular'">分子方程式</div>
          <div class="tab-item" :class="{ active: viewMode === 'fullionic' }" @click="viewMode = 'fullionic'">完整离子方程式</div>
          <div class="tab-item" :class="{ active: viewMode === 'netionic' }" @click="viewMode = 'netionic'">净离子方程式</div>
        </div>

        <div class="result-box result-formula">
          <template v-if="viewMode === 'molecular'">{{ result.subscript }}</template>
          <template v-else-if="viewMode === 'fullionic'">{{ ionicResult?.fullIonic || '请先分析方程式' }}</template>
          <template v-else>{{ ionicResult?.netIonic || '请先分析方程式' }}</template>
        </div>

        <div class="export-row">
          <button class="btn btn-secondary btn-sm" @click="copyCurrent">📋 复制当前格式</button>
          <button class="btn btn-secondary btn-sm" @click="copyText(result.latex)">📋 复制 LaTeX</button>
          <span v-if="copied" style="color: var(--success); font-size: 12px; align-self: center;">✓ 已复制</span>
        </div>
      </div>

      <!-- Balanced Info -->
      <div class="card">
        <div class="card-title">⚖️ 配平结果</div>
        <div class="result-box result-formula">{{ result.subscript }}</div>
        <div class="export-row">
          <button class="btn btn-secondary btn-sm" @click="copyText(result.subscript)">📋 复制 Unicode</button>
          <button class="btn btn-secondary btn-sm" @click="copyText(result.latex)">📋 复制 LaTeX</button>
        </div>
      </div>
    </div>

    <!-- Examples -->
    <div class="card">
      <div class="card-title">📚 示例反应</div>
      <div class="chip-group">
        <span class="chip" @click="input = 'AgNO3 + NaCl -> AgCl + NaNO3'; process()">沉淀反应 AgCl↓</span>
        <span class="chip" @click="input = 'NaOH + HCl -> NaCl + H2O'; process()">中和反应</span>
        <span class="chip" @click="input = 'Fe + CuSO4 -> FeSO4 + Cu'; process()">置换反应</span>
        <span class="chip" @click="input = 'N2 + 3H2 <=> 2NH3'; process()">可逆反应 ⇌</span>
        <span class="chip" @click="input = 'CaCO3 -> CaO + CO2'; process()">分解反应</span>
        <span class="chip" @click="input = '2Na + Cl2 -> 2NaCl'; process()">化合反应</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { processEquation, analyzeIons } from '../wails/app'

const input = ref('')
const result = ref<any>(null)
const ionicResult = ref<any>(null)
const viewMode = ref('molecular')
const copied = ref(false)

async function process() {
  if (!input.value.trim()) return
  result.value = await processEquation(input.value.trim())
  try {
    ionicResult.value = await analyzeIons(input.value.trim())
  } catch {
    ionicResult.value = null
  }
  copied.value = false
}

function clear() {
  input.value = ''
  result.value = null
  ionicResult.value = null
}

function getCurrentText(): string {
  if (viewMode.value === 'molecular') return result.value?.subscript || ''
  if (viewMode.value === 'fullionic') return ionicResult.value?.fullIonic || ''
  return ionicResult.value?.netIonic || ''
}

function copyCurrent() {
  copyText(getCurrentText())
}

function copyText(text: string) {
  navigator.clipboard.writeText(text)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}
</script>
