<template>
  <div class="fade-in">
    <div class="page-header">
      <h1 class="page-title">⚗️ ChemMaster</h1>
      <p class="page-subtitle">离线优先化学计算与数据库系统 · v1.0.8</p>
    </div>

    <div class="grid-2" style="gap: 16px;">
      <div>
        <div class="card">
          <div class="card-title">📋 简介</div>
          <div style="line-height: 1.8; color: var(--text-secondary); font-size: 14px;">
            <p>ChemMaster 是一款面向化学工作者的离线桌面应用，核心目标是将化学式、方程式快速转换为标准格式，可直接插入 LaTeX 论文或 Word 文档。</p>
            <p style="margin-top: 12px;"><strong style="color: var(--text-primary);">主要能力：</strong></p>
            <ul style="padding-left: 20px; margin-top: 8px;">
              <li>化学式解析 → Unicode 下标 / LaTeX / HTML</li>
              <li>方程式配平 → 自动系数求解</li>
              <li>实时方程式画布 → 输入即渲染，支持 mhchem 格式</li>
              <li>118 种元素完整周期表 → 电子构型、电负性、分类</li>
              <li>3D 分子结构查看器 → CIF/XYZ 文件导入，SVG/PNG 导出</li>
              <li>离子方程式 → 分子/离子/净离子方程式自动转换</li>
            </ul>
          </div>
        </div>

        <div class="card">
          <div class="card-title">🚀 快速上手</div>
          <div style="line-height: 2; font-size: 13px; color: var(--text-secondary);">
            <div><strong style="color: var(--accent);">1.</strong> 在左侧导航选择功能模块</div>
            <div><strong style="color: var(--accent);">2.</strong> 输入化学式或方程式，结果实时显示</div>
            <div><strong style="color: var(--accent);">3.</strong> 点击「复制」按钮获取 Unicode / LaTeX 文本</div>
            <div><strong style="color: var(--accent);">4.</strong> 直接粘贴到 LaTeX (需 \usepackage{mhchem}) 或 Word</div>
          </div>
        </div>
      </div>

      <div>
        <div class="card">
          <div class="card-title">📝 LaTeX 使用方法</div>
          <div class="result-box" style="font-family: var(--font-mono); font-size: 13px; line-height: 1.8;">
            <div style="color: var(--text-muted);">% 导言区添加</div>
            <div>\usepackage[version=4]{mhchem}</div>
            <div style="margin-top: 12px; color: var(--text-muted);">% 正文中使用</div>
            <div>\ce{H2SO4}</div>
            <div>\ce{2H2 + O2 ->[\text{点燃}] 2H2O}</div>
            <div>\ce{N2 + 3H2 &lt;=>[Fe][500K] 2NH3}</div>
            <div>\ce{SO4^2- + Ba^2+ -> BaSO4 v}</div>
          </div>
        </div>

        <div class="card">
          <div class="card-title">⚡ 快速入口</div>
          <div class="chip-group" style="flex-direction: column; gap: 10px;">
            <router-link to="/formula" class="quick-link">
              <span>🔬</span> 化学式解析 — 输入 H₂SO₄，获取标准格式
            </router-link>
            <router-link to="/live-equation" class="quick-link">
              <span>✏️</span> 实时方程式画布 — 输入即渲染，直接导出
            </router-link>
            <router-link to="/equation" class="quick-link">
              <span>⚖️</span> 方程式配平 — 自动求解系数
            </router-link>
            <router-link to="/database" class="quick-link">
              <span>🗄️</span> 元素周期表 — 118 种元素完整数据
            </router-link>
            <router-link to="/structure" class="quick-link">
              <span>🔮</span> 3D 分子结构 — CIF 文件可视化
            </router-link>
          </div>
        </div>

        <div class="card">
          <div class="card-title">💡 示例</div>
          <div class="grid-2" style="gap: 8px;">
            <div v-for="ex in examples" :key="ex.display" class="example-card" @click="$router.push('/formula')">
              <div style="font-size: 16px; font-weight: 600; color: var(--accent); font-family: 'Times New Roman', serif;">{{ ex.display }}</div>
              <div style="font-size: 11px; color: var(--text-muted);">{{ ex.name }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const examples = [
  { display: 'H₂SO₄', name: '硫酸' },
  { display: 'Ca(OH)₂', name: '氢氧化钙' },
  { display: 'Al₂(SO₄)₃', name: '硫酸铝' },
  { display: 'C₆H₁₂O₆', name: '葡萄糖' },
  { display: 'KMnO₄', name: '高锰酸钾' },
  { display: 'Fe₂O₃', name: '氧化铁' },
]
</script>

<style scoped>
.quick-link {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 14px; background: var(--bg-tertiary);
  border: 1px solid var(--border); border-radius: var(--radius-md);
  color: var(--text-primary); text-decoration: none;
  font-size: 13px; transition: all 0.15s;
}
.quick-link:hover {
  border-color: var(--accent); background: var(--accent-dim);
}
.quick-link span { font-size: 18px; }
.example-card {
  padding: 12px; background: var(--bg-tertiary);
  border: 1px solid var(--border); border-radius: var(--radius-md);
  cursor: pointer; transition: all 0.15s; text-align: center;
}
.example-card:hover { border-color: var(--accent); transform: translateY(-2px); }
</style>
