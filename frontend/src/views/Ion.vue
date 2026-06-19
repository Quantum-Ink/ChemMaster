<template>
  <div class="fade-in">
    <div class="page-header">
      <h1 class="page-title">⚡ 离子方程式</h1>
      <p class="page-subtitle">分子方程式→完整离子方程式→净离子方程式，旁观离子检测</p>
    </div>

    <div class="card">
      <div class="card-title">输入方程式</div>
      <div class="input-row">
        <div class="input-group">
          <input
            v-model="input"
            class="input-field"
            placeholder="NaOH + HCl -> NaCl + H2O 或 Ag+ + Cl- -> AgCl"
            @keyup.enter="analyze"
            autofocus
          />
        </div>
        <button class="btn btn-primary" @click="analyze">分析</button>
        <button class="btn btn-secondary" @click="balanceIon">配平离子</button>
        <button class="btn btn-ghost" @click="clear">清除</button>
      </div>
    </div>

    <div v-if="result" class="fade-in">
      <!-- Three forms -->
      <div class="card">
        <div class="card-title">📝 离子方程式分析</div>

        <div style="margin-bottom: 16px;">
          <div class="input-label">分子方程式</div>
          <div class="result-box result-formula">{{ result.molecular }}</div>
        </div>

        <div style="margin-bottom: 16px;">
          <div class="input-label">🔬 完整离子方程式</div>
          <div class="result-box result-formula">{{ result.fullIonic }}</div>
        </div>

        <div style="margin-bottom: 16px;">
          <div class="input-label">⚡ 净离子方程式</div>
          <div class="result-box result-formula" style="color: var(--accent);">{{ result.netIonic }}</div>
        </div>

        <div class="export-row">
          <button class="btn btn-secondary btn-sm" @click="copy(result.fullIonic)">📋 复制完整离子</button>
          <button class="btn btn-secondary btn-sm" @click="copy(result.netIonic)">📋 复制净离子</button>
          <span v-if="copied" style="color: var(--success); font-size: 12px; align-self: center;">✓ 已复制</span>
        </div>
      </div>

      <!-- Spectator ions -->
      <div class="grid-2">
        <div class="card">
          <div class="card-title">👀 旁观离子</div>
          <div v-if="result.spectators?.length" class="chip-group">
            <span v-for="ion in result.spectators" :key="ion" class="chip" style="background: var(--accent-dim); border-color: var(--accent); color: var(--accent);">
              {{ ion }}
            </span>
          </div>
          <div v-else style="color: var(--text-muted); font-size: 13px;">无旁观离子</div>
        </div>

        <div class="card">
          <div class="card-title">🔋 电荷守恒验证</div>
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
            <span class="status-dot" :class="result.chargeBalanced ? 'online' : 'offline'"></span>
            <span :style="{ color: result.chargeBalanced ? 'var(--success)' : 'var(--error)' }">
              {{ result.chargeBalanced ? '电荷守恒' : '电荷不守恒' }}
            </span>
          </div>
          <div style="font-size: 13px; color: var(--text-secondary);">
            反应物总电荷: {{ result.reactantCharges }} | 生成物总电荷: {{ result.productCharges }}
          </div>
        </div>
      </div>
    </div>

    <!-- Balance Result -->
    <div v-if="balanceResult" class="card fade-in">
      <div class="card-title">⚖️ 离子方程式配平结果</div>
      <div class="result-box result-formula">{{ balanceResult.subscript || balanceResult.balanced }}</div>
      <div class="export-row">
        <button class="btn btn-secondary btn-sm" @click="copy(balanceResult.subscript || balanceResult.balanced)">📋 复制</button>
        <button class="btn btn-secondary btn-sm" @click="copy(balanceResult.latex)">📋 复制 LaTeX</button>
      </div>
    </div>

    <!-- Examples -->
    <div class="card">
      <div class="card-title">📚 示例</div>
      <div class="chip-group">
        <span class="chip" @click="input = 'NaOH + HCl -> NaCl + H2O'; analyze()">中和反应</span>
        <span class="chip" @click="input = 'Na2SO4 + BaCl2 -> BaSO4 + 2NaCl'; analyze()">沉淀反应</span>
        <span class="chip" @click="input = 'Na2CO3 + 2HCl -> 2NaCl + H2O + CO2'; analyze()">酸与碳酸盐</span>
        <span class="chip" @click="input = 'Fe + CuSO4 -> FeSO4 + Cu'; analyze()">置换反应</span>
        <span class="chip" @click="input = 'AgNO3 + NaCl -> AgCl + NaNO3'; analyze()">AgCl 沉淀</span>
        <span class="chip" @click="input = 'H+ + OH- -> H2O'; balanceIon()">离子中和</span>
        <span class="chip" @click="input = 'Ag+ + Cl- -> AgCl'; balanceIon()">银离子沉淀</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { analyzeIons, balanceIonEquation } from '../wails/app'

const input = ref('')
const result = ref<any>(null)
const balanceResult = ref<any>(null)
const copied = ref(false)

async function analyze() {
  if (!input.value.trim()) return
  try {
    result.value = await analyzeIons(input.value.trim())
  } catch (e: any) {
    result.value = { molecular: input.value, fullIonic: 'Error: ' + e, netIonic: '', spectators: [], chargeBalanced: false }
  }
  balanceResult.value = null
  copied.value = false
}

async function balanceIon() {
  if (!input.value.trim()) return
  balanceResult.value = await balanceIonEquation(input.value.trim())
  result.value = null
  copied.value = false
}

function clear() {
  input.value = ''
  result.value = null
  balanceResult.value = null
}

function copy(text: string) {
  navigator.clipboard.writeText(text)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}
</script>
