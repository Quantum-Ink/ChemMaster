# 🧪 ChemMaster

**AI 驱动的化学方程式编辑器** — 支持化学式解析、方程式平衡、有机物结构绘制、分子 3D 可视化、LaTeX 导出和 Microsoft Word 集成。

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ 核心功能

### 🧬 化学式解析
- 智能解析化学式（H2SO4, Ca(OH)2, NH4+）
- Unicode 下标转换（H₂SO₄）
- LaTeX 格式输出（`\ce{H2SO4}`）

### ⚖️ 方程式平衡
- 基于矩阵法的自动平衡算法
- 支持多种反应类型
- 示例：`Fe + O2 -> Fe2O3` → `4Fe + 3O2 -> 2Fe2O3`

### 📐 LaTeX 导出
- 支持 `mhchem` 包格式
- 生成完整的 LaTeX 文档
- 兼容主流 LaTeX 编辑器

### 📝 Word 集成
- Microsoft Office Add-in 支持
- Unicode 下标格式直接粘贴
- HTML/RTF 格式导出

### 🎨 有机物结构绘制
- Canvas 画布式编辑器，参考 GeoGebra 简洁模式
- 原子工具：C / N / O / S / P / F / Cl / Br / I / H
- 键型工具：单键 / 双键 / 三键
- 常用模板：苯环、环己烷、环戊烷、羟基、羧基、氨基、醛基、硝基
- 拖拽绘制：点击放置原子，拖拽创建化学键
- 自动校准键角（120° / 109.5° / 180°）
- 实时 SMILES 输出 + 分子式 / 分子量计算
- 导出 SVG / PNG 图片
- 撤销 / 重做支持（Ctrl+Z / Ctrl+Y）

### 🔬 分子 3D 可视化
- 基于 3Dmol.js 的 WebGL 3D 分子查看器，参考 Mercury 软件
- 多种显示模式：球棍模型、空间填充（CPK）、棍棒模型、线框模型
- 鼠标交互：旋转、缩放、平移
- 输入方式：SMILES 字符串 / 化合物英文名称 / SDF 文件上传
- PubChem 数据库集成：输入化合物名称自动加载 3D 结构
- 功能切换：自动旋转、氢原子显示、原子标签、分子表面
- CPK 标准元素配色方案
- PNG 截图导出

### 🔬 化学数据库查询
- PubChem API 集成
- 化合物信息检索
- 分子结构可视化

---

## 🏗️ 项目架构

```
ChemMaster/
│
├── frontend/                    # 前端界面
│   ├── index.html              # 主页面
│   ├── editor.js               # 编辑器逻辑
│   ├── canvas.js               # 画布组件
│   ├── molecule-canvas.js      # Canvas 分子结构编辑器
│   ├── molecule-viewer.js      # 3D 分子可视化器
│   ├── structure-editor.js     # SMILES 结构编辑器
│   ├── plugins.js              # 插件管理系统
│   └── style.css               # 样式文件
│
├── backend/                     # 后端服务
│   ├── app/
│   │   ├── api/                # API 端点
│   │   │   ├── export.py       # 导出接口
│   │   │   ├── reaction.py     # 反应接口
│   │   │   ├── structure.py    # 结构接口 (含 3D / PubChem)
│   │   │   └── editor.py       # 编辑器接口
│   │   ├── core/               # 核心模块
│   │   │   ├── chemistry.py    # 化学式解析
│   │   │   ├── reaction_engine.py  # 方程式平衡
│   │   │   ├── rdkit_engine.py # RDKit 集成
│   │   │   ├── molecule_renderer.py # 分子渲染器 (2D/3D)
│   │   │   ├── pubchem_api.py  # PubChem API 集成
│   │   │   ├── equation_enhancer.py # 方程式增强
│   │   │   └── smiles.py       # SMILES 支持
│   │   └── plugins/            # 插件实现
│   │       ├── word_plugin.py  # Word 导出
│   │       └── letax_plugin.py # LaTeX 导出
│   └── requirements.txt        # Python 依赖
│
├── plugins/                     # 前端插件
│   ├── word.js                 # Word 前端插件
│   ├── latex.js                # LaTeX 前端插件
│   ├── pubchem.js              # PubChem 查询插件
│   └── word-addin/             # Office Add-in
│       ├── manifest.xml        # 插件配置
│       ├── taskpane.html       # 任务面板
│       └── taskpane.js         # 面板逻辑
│
├── tests/                       # 测试文件
│   └── test_chemistry.py       # 化学模块测试
│
└── docs/                        # 文档
    └── plugin-spec.md          # 插件规范
```

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/yourname/ChemMaster.git
cd ChemMaster
```

### 2. 后端设置

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端运行在：`http://localhost:8000`

### 3. 前端设置

```bash
cd frontend
# 使用任意 HTTP 服务器
python -m http.server 5173
# 或者使用 Node.js
npx serve -p 5173
```

前端运行在：`http://localhost:5173`

### 4. 运行测试

```bash
python tests/test_chemistry.py
```

---

## 📖 API 文档

### 基础端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `GET /` | GET | 服务状态检查 |
| `POST /api/export/formula` | POST | 导出化学式 |
| `POST /api/export/equation` | POST | 导出方程式 |
| `POST /api/export/batch` | POST | 批量导出 |
| `POST /api/export/word/formula` | POST | Word 格式化学式 |
| `POST /api/export/word/equation` | POST | Word 格式方程式 |
| `POST /api/export/latex/formula` | POST | LaTeX 格式化学式 |
| `POST /api/export/latex/equation` | POST | LaTeX 格式方程式 |
| `POST /api/export/latex/document` | POST | 生成 LaTeX 文档 |
| `POST /api/structure/validate` | POST | 验证 SMILES |
| `POST /api/structure/info` | POST | 获取分子信息 |
| `POST /api/structure/render/svg` | POST | 渲染 SVG 结构图 |
| `POST /api/structure/render/png` | POST | 渲染 PNG 结构图 |
| `POST /api/structure/3d` | POST | 生成 3D SDF 结构 |
| `POST /api/structure/pubchem/3d` | POST | PubChem 3D 结构查询 |
| `GET /api/structure/pubchem/search/{name}` | GET | PubChem 化合物搜索 |

### 请求示例

#### 化学式转换

```bash
curl -X POST "http://localhost:8000/api/export/formula" \
  -H "Content-Type: application/json" \
  -d '{"formula": "H2SO4", "format": "mhchem"}'
```

**响应：**
```json
{
  "original": "H2SO4",
  "unicode": "H₂SO₄",
  "latex": "\\ce{H2SO4}",
  "format": "mhchem"
}
```

#### 方程式平衡

```bash
curl -X POST "http://localhost:8000/api/export/equation" \
  -H "Content-Type: application/json" \
  -d '{"equation": "Fe + O2 -> Fe2O3", "format": "mhchem", "balance": true}'
```

**响应：**
```json
{
  "original": "Fe + O2 -> Fe2O3",
  "balanced": "4Fe + 3O2 -> 2Fe2O3",
  "unicode": "4Fe + 3O₂ → 2Fe₂O₃",
  "latex": "\\ce{4Fe + 3O2 -> 2Fe2O3}",
  "is_balanced": false
}
```

---

## 💻 使用示例

### Python 后端

```python
from backend.app.core.chemistry import FormulaParser
from backend.app.core.reaction_engine import EquationBalancer

# 化学式解析
parser = FormulaParser()
elements = parser.parse('H2SO4')
print(elements)  # {'H': 2, 'S': 1, 'O': 4}

subscript = parser.to_subscript('H2SO4')
print(subscript)  # H₂SO₄

latex = parser.to_latex('H2SO4', 'mhchem')
print(latex)  # \ce{H2SO4}

# 方程式平衡
balancer = EquationBalancer()
balanced = balancer.balance('Fe + O2 -> Fe2O3')
print(balanced)  # 4Fe + 3O2 -> 2Fe2O3
```

### JavaScript 前端

```javascript
// Word 插件使用
const result = await wordPlugin.convertFormula('H2SO4');
console.log(result.unicode);  // H₂SO₄

// LaTeX 插件使用
const latex = await latexPlugin.convertEquation('H2 + O2 -> H2O');
console.log(latex.latex);  // \ce{2H2 + O2 -> 2H2O}

// 批量处理
const batch = await wordPlugin.processBatch([
  'H2 + O2 -> H2O',
  'Na + H2O -> NaOH + H2'
]);

// Canvas 分子编辑器
const canvas = new MoleculeCanvas('canvas-container');
canvas.placeTemplate('benzene');  // 放置苯环模板
console.log(canvas.getSmiles());  // 输出 SMILES
console.log(canvas.getFormula()); // 输出分子式

// 3D 分子可视化
const viewer = new MoleculeViewer('viewer-container', {
    apiBaseUrl: '/api/structure'
});
await viewer.loadMolecule('CC(=O)Oc1ccccc1C(=O)O');  // 阿司匹林 SMILES
await viewer.loadMolecule('aspirin');  // 或使用英文名称
```

---

## 🔧 技术栈

### 后端
- **Python 3.8+** — 主要编程语言
- **FastAPI** — Web 框架
- **NumPy** — 矩阵运算（方程式平衡）
- **RDKit** — 化学信息学（分子处理、2D/3D 渲染）
- **Pillow** — 图像处理

### 前端
- **HTML/CSS/JavaScript** — 基础技术
- **Canvas API** — 分子结构画布编辑器
- **3Dmol.js** — WebGL 3D 分子可视化
- **Office.js** — Microsoft Office 集成
- **KaTeX/MathJax** — LaTeX 预览（可选）

### 化学数据库
- **PubChem API** — 化合物信息查询、3D 结构获取
- **SMILES** — 分子结构表示

---

## 📊 支持的化学式格式

| 输入 | Unicode 输出 | LaTeX 输出 |
|------|-------------|------------|
| H2O | H₂O | \ce{H2O} |
| H2SO4 | H₂SO₄ | \ce{H2SO4} |
| Ca(OH)2 | Ca(OH)₂ | \ce{Ca(OH)2} |
| NH4+ | NH₄⁺ | \ce{NH4+} |
| CO2 | CO₂ | \ce{CO2} |
| C6H12O6 | C₆H₁₂O₆ | \ce{C6H12O6} |

---

## ⚖️ 方程式平衡示例

| 输入 | 平衡后 |
|------|--------|
| Fe + O2 -> Fe2O3 | 4Fe + 3O2 -> 2Fe2O3 |
| H2 + O2 -> H2O | 2H2 + O2 -> 2H2O |
| Na + H2O -> NaOH + H2 | 2Na + 2H2O -> 2NaOH + H2 |
| CH4 + O2 -> CO2 + H2O | CH4 + 2O2 -> CO2 + 2H2O |
| Al + HCl -> AlCl3 + H2 | 2Al + 6HCl -> 2AlCl3 + 3H2 |

---

## 📝 Word Add-in 安装

### 本地开发（旁加载）

1. 打开 Microsoft Word
2. 转到 **插入** > **我的加载项** > **共享文件夹**
3. 选择 `plugins/word-addin/manifest.xml`
4. 点击 **安装**

### 功能

- 📊 任务面板：侧边栏化学式输入界面
- 🔄 实时预览：输入时即时显示转换结果
- 📋 一键插入：将格式化内容直接插入文档
- 📜 历史记录：保存最近使用的化学式

---

## 🧪 运行测试

```bash
# 运行所有测试
python tests/test_chemistry.py

# 预期输出
[PASS] Formula parser tests passed
[PASS] Reaction parser tests passed
[PASS] Equation balancer tests passed
[PASS] Format conversion tests passed

[PASS] All tests passed!
```

---

## 📚 文档

- [插件开发指南](plugins/README.md)
- [API 详细文档](docs/api.md)（规划中）
- [化学式规范](docs/chemistry-spec.md)（规划中）

---

## 🛣️ 发展路线

### 已完成 ✅
- [x] 化学式解析器
- [x] 方程式平衡器
- [x] LaTeX 导出插件
- [x] Word 导出插件
- [x] Office Add-in 基础框架
- [x] REST API 端点
- [x] 有机物结构绘制（Canvas 画布编辑器）
- [x] 分子 3D 可视化（3Dmol.js）
- [x] PubChem API 集成（化合物查询 + 3D 结构）
- [x] 矢量图输出（SVG / PNG）

### 规划中 📋
- [ ] AI 自然语言转方程式
- [ ] 离子方程式支持
- [ ] 反应类型分类
- [ ] 3D 分子结构展示
- [ ] PDF 导出
- [ ] 协作编辑

---

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m 'Add your feature'`
4. 推送分支：`git push origin feature/your-feature`
5. 创建 Pull Request

### 开发规范

- 遵循 PEP 8（Python）和 ESLint（JavaScript）规范
- 添加适当的注释和文档
- 编写测试用例
- 更新 README（如需要）

---

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。

---

## 👥 团队

- **开发者** — [Your Name](https://github.com/yourname)

---

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) — 高性能 Web 框架
- [NumPy](https://numpy.org/) — 科学计算库
- [RDKit](https://www.rdkit.org/) — 化学信息学工具包
- [3Dmol.js](https://3dmol.org/) — WebGL 3D 分子可视化
- [PubChem](https://pubchem.ncbi.nlm.nih.gov/) — 化学数据库
- [mhchem](https://ctan.org/pkg/mhchem) — LaTeX 化学式包

---

## 📞 联系方式

- 📧 Email: your.email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourname/ChemMaster/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourname/ChemMaster/discussions)

---

<p align="center">Made with ❤️ for Chemistry</p>
