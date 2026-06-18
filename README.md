# ChemMaster 插件系统

## 概述

ChemMaster 插件系统提供了化学式和反应方程式的转换、导出功能，支持 Word 和 LaTeX 两种主要格式。

## 插件列表

### 1. Word 插件 (`word.js`)

**功能：**
- 将化学式转换为 Unicode 下标格式（如 H₂SO₄）
- 将反应方程式转换为 Word 可用的格式
- 支持批量处理
- 提供复制、下载功能

**使用方法：**
```javascript
// 转换化学式
const result = await wordPlugin.convertFormula('H2SO4');
console.log(result.unicode); // H₂SO₄

// 转换方程式
const result = await wordPlugin.convertEquation('Fe + O2 -> Fe2O3');
console.log(result.unicode); // 4Fe + 3O₂ → 2Fe₂O₃

// 批量处理
const result = await wordPlugin.processBatch([
    'H2 + O2 -> H2O',
    'Na + H2O -> NaOH + H2'
]);

// 复制到剪贴板
await wordPlugin.copyToClipboard(result.unicode);

// 下载为文件
wordPlugin.downloadAsText(content, 'chemistry.txt');
wordPlugin.downloadAsHTML(content, 'chemistry.html');
```

### 2. LaTeX 插件 (`latex.js`)

**功能：**
- 将化学式转换为 LaTeX 格式（支持 mhchem 包）
- 将反应方程式转换为 LaTeX 格式
- 生成完整的 LaTeX 文档
- 支持 KaTeX/MathJax 预览

**使用方法：**
```javascript
// 转换化学式
const result = await latexPlugin.convertFormula('H2SO4', 'mhchem');
console.log(result.latex); // \ce{H2SO4}

// 转换方程式
const result = await latexPlugin.convertEquation('Fe + O2 -> Fe2O3');
console.log(result.latex); // \ce{4Fe + 3O2 -> 2Fe2O3}

// 生成完整文档
const doc = await latexPlugin.generateDocument([
    'H2 + O2 -> H2O',
    'Na + H2O -> NaOH + H2'
], '化学反应方程式');

// 下载为 .tex 文件
latexPlugin.downloadAsTex(doc.document, 'chemistry.tex');

// 渲染预览
latexPlugin.renderPreview(element, '\\ce{H2SO4}');
```

### 3. 插件管理器 (`plugins.js`)

**功能：**
- 统一管理所有插件
- 自动初始化插件
- 提供插件状态查询

**使用方法：**
```javascript
// 获取插件管理器状态
const status = pluginManager.getStatus();

// 获取特定插件
const wordPlugin = pluginManager.getPlugin('word');

// 注册新插件
pluginManager.register(myPlugin);
```

## Word Add-in

### 概述

Word Add-in 是一个 Office 插件，可以在 Microsoft Word 中直接使用 ChemMaster 的功能。

### 安装方法

1. **本地开发安装（旁加载）：**

   - 打开 Word
   - 转到 "插入" > "我的加载项" > "共享文件夹"
   - 选择 `plugins/word-addin/manifest.xml`
   - 点击 "安装"

2. **生产环境安装：**

   - 将插件部署到 Web 服务器
   - 更新 `manifest.xml` 中的 URL
   - 通过 Office 365 管理中心分发

### 功能

- **任务面板：** 在 Word 侧边栏显示化学式输入界面
- **功能区按钮：** 在 "开始" 选项卡中添加 ChemMaster 按钮
- **实时预览：** 输入时实时显示转换结果
- **一键插入：** 将格式化的化学式插入到文档

### 文件结构

```
plugins/word-addin/
├── manifest.xml      # Office Add-in 配置文件
├── taskpane.html     # 任务面板界面
├── taskpane.js       # 任务面板逻辑
├── commands.js       # 命令处理文件
└── assets/           # 图标等资源
```

## 后端 API

### 端点列表

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/export/formula` | POST | 导出化学式 |
| `/api/export/equation` | POST | 导出方程式 |
| `/api/export/batch` | POST | 批量导出 |
| `/api/export/word/formula` | POST | Word 格式化学式 |
| `/api/export/word/equation` | POST | Word 格式方程式 |
| `/api/export/latex/formula` | POST | LaTeX 格式化学式 |
| `/api/export/latex/equation` | POST | LaTeX 格式方程式 |
| `/api/export/latex/document` | POST | 生成 LaTeX 文档 |

### 请求示例

**转换化学式：**
```javascript
const response = await fetch('/api/export/formula', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        formula: 'H2SO4',
        format: 'mhchem'
    })
});

const result = await response.json();
// {
//   original: 'H2SO4',
//   unicode: 'H₂SO₄',
//   latex: '\\ce{H2SO4}',
//   format: 'mhchem'
// }
```

**转换方程式：**
```javascript
const response = await fetch('/api/export/equation', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        equation: 'Fe + O2 -> Fe2O3',
        format: 'mhchem',
        balance: true
    })
});

const result = await response.json();
// {
//   original: 'Fe + O2 -> Fe2O3',
//   balanced: '4Fe + 3O2 -> 2Fe2O3',
//   unicode: '4Fe + 3O₂ → 2Fe₂O₃',
//   latex: '\\ce{4Fe + 3O2 -> 2Fe2O3}',
//   is_balanced: false
// }
```

## 核心模块

### 1. 化学式解析器 (`chemistry.py`)

**功能：**
- 解析化学式（如 H2SO4, Ca(OH)2）
- 转换为 Unicode 下标格式
- 转换为 LaTeX 格式

**使用方法：**
```python
from app.core.chemistry import FormulaParser

parser = FormulaParser()

# 解析化学式
elements = parser.parse('H2SO4')
# {'H': 2, 'S': 1, 'O': 4}

# 转换为下标格式
subscript = parser.to_subscript('H2SO4')
# 'H₂SO₄'

# 转换为 LaTeX 格式
latex = parser.to_latex('H2SO4', 'mhchem')
# '\\ce{H2SO4}'
```

### 2. 方程式平衡器 (`reaction_engine.py`)

**功能：**
- 使用矩阵法平衡化学方程式
- 支持多种反应类型
- 提供格式化输出

**使用方法：**
```python
from app.core.reaction_engine import EquationBalancer

balancer = EquationBalancer()

# 平衡方程式
balanced = balancer.balance('Fe + O2 -> Fe2O3')
# '4Fe + 3O2 -> 2Fe2O3'

# 检查是否已平衡
is_balanced = balancer.is_balanced('2H2 + O2 -> 2H2O')
# True
```

### 3. LaTeX 导出插件 (`letax_plugin.py`)

**功能：**
- 生成 LaTeX 格式的化学式
- 生成完整的 LaTeX 文档
- 支持 mhchem 包

### 4. Word 导出插件 (`word_plugin.py`)

**功能：**
- 生成 Unicode 下标格式
- 生成 HTML 和 RTF 格式
- 提供 Office.js 集成代码

## 示例

### 化学式转换

| 输入 | Unicode 输出 | LaTeX 输出 |
|------|-------------|------------|
| H2SO4 | H₂SO₄ | \ce{H2SO4} |
| Ca(OH)2 | Ca(OH)₂ | \ce{Ca(OH)2} |
| NH4+ | NH₄⁺ | \ce{NH4+} |
| CO2 | CO₂ | \ce{CO2} |

### 反应方程式平衡

| 输入 | 平衡后 |
|------|--------|
| Fe + O2 -> Fe2O3 | 4Fe + 3O2 -> 2Fe2O3 |
| H2 + O2 -> H2O | 2H2 + O2 -> 2H2O |
| Na + H2O -> NaOH + H2 | 2Na + 2H2O -> 2NaOH + H2 |
| CH4 + O2 -> CO2 + H2O | CH4 + 2O2 -> CO2 + 2H2O |

## 依赖

### 后端依赖

```
fastapi>=0.68.0
uvicorn>=0.15.0
numpy>=1.21.0
pydantic>=1.8.0
```

### 前端依赖

- Office.js（Word Add-in）
- KaTeX 或 MathJax（LaTeX 预览，可选）

## 开发

### 添加新插件

1. 在 `plugins/` 目录创建新的 JS 文件
2. 实现插件类
3. 在 `plugins.js` 中注册插件

### 扩展 API

1. 在 `backend/app/api/` 创建新的路由文件
2. 在 `main.py` 中注册路由
3. 更新前端调用代码

## 注意事项

1. **化学式格式：** 使用标准化学式格式（如 H2SO4, Ca(OH)2）
2. **方程式格式：** 使用 `->` 或 `→` 作为反应箭头
3. **离子电荷：** 使用 `+` 和 `-` 表示电荷（如 NH4+, SO4^2-）
4. **括号：** 支持嵌套括号（如 Ca(OH)2）
5. **系数：** 平衡后的系数会自动添加到化学式前面

## 常见问题

**Q: 为什么有些方程式无法平衡？**
A: 请确保输入的方程式是有效的化学反应，且包含所有必要的反应物和生成物。

**Q: 如何在 Word 中使用插件？**
A: 安装 Word Add-in 后，在 "开始" 选项卡中会显示 ChemMaster 按钮，点击即可打开任务面板。

**Q: LaTeX 预览不显示怎么办？**
A: 请确保页面中引入了 KaTeX 或 MathJax 库，或者直接复制 LaTeX 代码到专业的 LaTeX 编辑器中使用。
