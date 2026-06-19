<template>
  <div class="fade-in">
    <div class="page-header">
      <h1 class="page-title">⚖️ 方程式配平</h1>
      <p class="page-subtitle">使用矩阵法（高斯消元）自动配平化学方程式</p>
    </div>

    <div class="card">
      <div class="card-title">输入方程式</div>
      <div class="input-row">
        <div class="input-group">
          <input
            v-model="input"
            class="input-field"
            placeholder="Fe + O2 -> Fe2O3"
            @keyup.enter="balance"
            autofocus
          />
        </div>
        <button class="btn btn-primary" @click="balance">配平</button>
        <button class="btn btn-ghost" @click="clear">清除</button>
      </div>
      <div style="margin-top: 8px; font-size: 12px; color: var(--text-muted);">
        支持分隔符: -> → ⟶ ⇌ <=> =
      </div>
    </div>

    <div v-if="result" class="fade-in">
      <div class="card">
        <div class="card-title">📝 配平结果</div>
        <div class="tab-bar">
          <div class="tab-item" :class="{ active: viewMode === 'subscript' }" @click="viewMode = 'subscript'">下标格式</div>
          <div class="tab-item" :class="{ active: viewMode === 'latex' }" @click="viewMode = 'latex'">LaTeX</div>
          <div class="tab-item" :class="{ active: viewMode === 'raw' }" @click="viewMode = 'raw'">原始</div>
        </div>
        <div class="result-box result-formula">
          <template v-if="viewMode === 'subscript'">{{ result.subscript }}</template>
          <template v-else-if="viewMode === 'latex'">{{ result.latex }}</template>
          <template v-else>{{ result.balanced }}</template>
        </div>
        <div class="export-row">
          <button class="btn btn-secondary btn-sm" @click="copy(result.subscript)">📋 复制 Unicode</button>
          <button class="btn btn-secondary btn-sm" @click="copy(result.latex)">📋 复制 LaTeX</button>
          <span v-if="copied" style="color: var(--success); font-size: 12px; align-self: center;">✓ 已复制</span>
        </div>
      </div>

      <div class="grid-2">
        <div class="card">
          <div class="card-title">📊 配平信息</div>
          <table class="data-table">
            <tbody>
              <tr>
                <td style="color: var(--text-secondary);">原始方程式</td>
                <td>{{ result.original }}</td>
              </tr>
              <tr>
                <td style="color: var(--text-secondary);">配平状态</td>
                <td>
                  <span :style="{ color: result.isBalanced ? 'var(--success)' : 'var(--error)' }">
                    {{ result.isBalanced ? '✓ 已配平' : '✗ 未能配平' }}
                  </span>
                </td>
              </tr>
              <tr>
                <td style="color: var(--text-secondary);">系数</td>
                <td>{{ result.coefficients?.join(', ') || 'N/A' }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="card">
          <div class="card-title">🧪 涉及元素</div>
          <div class="chip-group">
            <span v-for="elem in result.elements" :key="elem" class="chip">{{ elem }}</span>
          </div>
          <div v-if="result.error" style="margin-top: 12px; color: var(--error); font-size: 13px;">
            ⚠️ {{ result.error }}
          </div>
        </div>
      </div>
    </div>

    <!-- Examples -->
    <div class="card">
      <div class="card-title">📚 示例方程式</div>
      <div class="chip-group">
        <span class="chip" @click="input = 'Fe + O2 -> Fe2O3'; balance()">4Fe + 3O₂ → 2Fe₂O₃</span>
        <span class="chip" @click="input = 'H2 + O2 -> H2O'; balance()">2H₂ + O₂ → 2H₂O</span>
        <span class="chip" @click="input = 'Na + H2O -> NaOH + H2'; balance()">Na + H₂O</span>
        <span class="chip" @click="input = 'CH4 + O2 -> CO2 + H2O'; balance()">CH₄ + O₂</span>
        <span class="chip" @click="input = 'HCl + NaOH -> NaCl + H2O'; balance()">中和反应</span>
        <span class="chip" @click="input = 'Al + HCl -> AlCl3 + H2'; balance()">Al + HCl</span>
        <span class="chip" @click="input = 'KMnO4 + HCl -> KCl + MnCl2 + H2O + Cl2'; balance()">KMnO₄ + HCl</span>
        <span class="chip" @click="input = 'CuSO4 + NH3 -> [Cu(NH3)4]SO4'; balance()">铜氨配合物</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { balanceEquation } from '../wails/app'

const input = ref('')
const result = ref<any>(null)
const viewMode = ref('subscript')
const copied = ref(false)

async function balance() {
  if (!input.value.trim()) return
  result.value = await balanceEquation(input.value.trim())
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
