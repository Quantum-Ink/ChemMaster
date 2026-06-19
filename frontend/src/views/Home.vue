<template>
  <div class="fade-in">
    <div class="page-header">
      <h1 class="page-title">⚗️ ChemMaster</h1>
      <p class="page-subtitle">离线优先化学计算与数据库系统</p>
    </div>

    <!-- Quick Stats -->
    <div class="grid-4" style="margin-bottom: 24px;">
      <div class="card" style="text-align: center;">
        <div style="font-size: 28px; font-weight: 700; color: var(--accent);">118</div>
        <div style="font-size: 12px; color: var(--text-secondary);">元素数据</div>
      </div>
      <div class="card" style="text-align: center;">
        <div style="font-size: 28px; font-weight: 700; color: var(--success);">✓</div>
        <div style="font-size: 12px; color: var(--text-secondary);">化学式解析</div>
      </div>
      <div class="card" style="text-align: center;">
        <div style="font-size: 28px; font-weight: 700; color: var(--warning);">⚖️</div>
        <div style="font-size: 12px; color: var(--text-secondary);">方程式配平</div>
      </div>
      <div class="card" style="text-align: center;">
        <div style="font-size: 28px; font-weight: 700; color: var(--info);">🔌</div>
        <div style="font-size: 12px; color: var(--text-secondary);">插件系统</div>
      </div>
    </div>

    <!-- Quick Input -->
    <div class="card">
      <div class="card-title">🔬 快速化学式解析</div>
      <div class="input-row">
        <div class="input-group">
          <label class="input-label">输入化学式</label>
          <input
            v-model="formulaInput"
            class="input-field"
            placeholder="例如: H2SO4, Ca(OH)2, Al2(SO4)3"
            @keyup.enter="parseFormula"
          />
        </div>
        <button class="btn btn-primary" @click="parseFormula">解析</button>
      </div>

      <div v-if="formulaResult" style="margin-top: 16px;">
        <div class="grid-2">
          <div>
            <div class="input-label">Unicode 下标</div>
            <div class="result-box result-formula">{{ formulaResult.subscript }}</div>
          </div>
          <div>
            <div class="input-label">分子量</div>
            <div class="result-box" style="text-align: center; font-size: 24px;">
              {{ formulaResult.molecularWeight }} g/mol
            </div>
          </div>
        </div>
        <div style="margin-top: 12px;">
          <div class="input-label">元素组成</div>
          <div class="chip-group">
            <span v-for="(count, elem) in formulaResult.elements" :key="elem" class="chip">
              {{ elem }}: {{ count }}
            </span>
          </div>
        </div>
        <div class="export-row">
          <button class="btn btn-secondary btn-sm" @click="copyText(formulaResult.subscript)">复制 Unicode</button>
          <button class="btn btn-secondary btn-sm" @click="copyText(formulaResult.latex)">复制 LaTeX</button>
        </div>
      </div>
    </div>

    <!-- Quick Equation -->
    <div class="card">
      <div class="card-title">⚖️ 快速方程式配平</div>
      <div class="input-row">
        <div class="input-group">
          <label class="input-label">输入方程式</label>
          <input
            v-model="equationInput"
            class="input-field"
            placeholder="例如: Fe + O2 -> Fe2O3"
            @keyup.enter="balanceEquation"
          />
        </div>
        <button class="btn btn-primary" @click="balanceEquation">配平</button>
      </div>

      <div v-if="equationResult" style="margin-top: 16px;">
        <div class="result-box result-formula">{{ equationResult.subscript || equationResult.balanced }}</div>
        <div class="export-row">
          <button class="btn btn-secondary btn-sm" @click="copyText(equationResult.subscript || equationResult.balanced)">复制结果</button>
          <button class="btn btn-secondary btn-sm" @click="copyText(equationResult.latex)">复制 LaTeX</button>
        </div>
      </div>
    </div>

    <!-- Examples -->
    <div class="card">
      <div class="card-title">📚 常用示例</div>
      <div class="grid-2">
        <div>
          <div class="input-label" style="margin-bottom: 8px;">化学式</div>
          <div class="chip-group">
            <span class="chip" @click="formulaInput = 'H2SO4'; parseFormula()">H₂SO₄ 硫酸</span>
            <span class="chip" @click="formulaInput = 'Ca(OH)2'; parseFormula()">Ca(OH)₂ 氢氧化钙</span>
            <span class="chip" @click="formulaInput = 'Al2(SO4)3'; parseFormula()">Al₂(SO₄)₃ 硫酸铝</span>
            <span class="chip" @click="formulaInput = 'C6H12O6'; parseFormula()">C₆H₁₂O₆ 葡萄糖</span>
          </div>
        </div>
        <div>
          <div class="input-label" style="margin-bottom: 8px;">方程式</div>
          <div class="chip-group">
            <span class="chip" @click="equationInput = 'Fe + O2 -> Fe2O3'; balanceEquation()">铁的氧化</span>
            <span class="chip" @click="equationInput = 'H2 + O2 -> H2O'; balanceEquation()">氢气燃烧</span>
            <span class="chip" @click="equationInput = 'CH4 + O2 -> CO2 + H2O'; balanceEquation()">甲烷燃烧</span>
            <span class="chip" @click="equationInput = 'Na + H2O -> NaOH + H2'; balanceEquation()">钠与水</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { parseFormula as apiParse, balanceEquation as apiBalance } from '../wails/app'

const formulaInput = ref('')
const formulaResult = ref<any>(null)
const equationInput = ref('')
const equationResult = ref<any>(null)

async function parseFormula() {
  if (!formulaInput.value.trim()) return
  formulaResult.value = await apiParse(formulaInput.value.trim())
}

async function balanceEquation() {
  if (!equationInput.value.trim()) return
  equationResult.value = await apiBalance(equationInput.value.trim())
}

function copyText(text: string) {
  navigator.clipboard.writeText(text)
}
</script>
