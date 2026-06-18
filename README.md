# 🧪 ChemMaster

**AI 驱动的化学式编辑器** — 支持化学式解析、方程式平衡、有机物结构绘制、分子 3D 可视化、LaTeX 导出和 Microsoft Word 集成。

**桌面应用形态** — Clash-like 体验：系统托盘常驻、原生窗口、中英双语、极低资源占用。

**双模式数据系统** — Offline First（内置 SQLite）+ Cloud Extension（PubChem API + LRU/TTL 缓存）。

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ 核心功能

### 🖥️ 桌面应用（Clash-like）
- **系统托盘常驻** — 最小化到托盘，随时调出
- **原生窗口** — pywebview 渲染，非 Electron，极低资源占用
- **中英双语** — 一键切换中文/English，前后端同步
- **跨平台** — 支持 Windows / macOS / Linux

### 📴 离线优先（Offline First）
- **内置 SQLite 数据库** — 118 种元素 + 100+ 常见化合物 + 反应方程式
- **离线化学式解析** — 无网络完全可用
- **离线方程式配平** — 矩阵法本地计算
- **离线分子性质查询** — RDKit 本地计算分子量、原子数等

### 🌐 在线增强（Cloud Extension）
- **PubChem API 集成** — 实时查询化学物质属性
- **LRU + TTL 缓存** — 内存 512 条 + SQLite 持久化，减少网络请求
- **自动回退** — 本地未命中时自动查在线，结果自动缓存

### 🧬 化学式解析
- 智能解析化学式（H2SO4, Ca(OH)2, NH4+）
- Unicode 下标转换（H₂SO₄）
- LaTeX 格式输出（`\ce{H2SO4}`）

### ⚖️ 方程式平衡
- 基于矩阵法的自动平衡算法
- 支持多种反应类型
- 示例：`Fe + O2 -> Fe2O3` → `4Fe + 3O2 -> 2Fe2O3`

### 🎨 有机物结构绘制
- Canvas 画布式编辑器，参考 GeoGebra 简洁模式
- 原子工具：C / N / O / S / P / F / Cl / Br / I / H
- 键型工具：单键 / 双键 / 三键
- 常用模板：苯环、环己烷、环戊烷、羟基、羧基、氨基、醛基、硝基
- 拖拽绘制：点击放置原子，拖拽创建化学键
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
- PNG 截图导出

### 📐 LaTeX 导出
- 支持 `mhchem` 包格式
- 生成完整的 LaTeX 文档
- 兼容主流 LaTeX 编辑器

### 📝 Word 集成
- Microsoft Office Add-in 支持
- Unicode 下标格式直接粘贴
- HTML/RTF 格式导出

### 🔌 插件系统
- 自动发现 — 放入 `backend/app/plugins/` 即可加载
- 分类管理 — export / analysis / prediction / database / generator / tool
- 端点声明 — 插件自定义 API 路由，自动注册到 FastAPI
- 前后端同步 — 前端 PluginManager 与后端联动

---

## 🏗️ 项目架构

```
ChemMaster/
├── run.py                           # 统一启动入口
├── requirements-desktop.txt         # 桌面版额外依赖
│
├── desktop/                         # 桌面应用层
│   ├── app.py                       # pywebview 主窗口 + FastAPI 后台
│   ├── tray.py                      # pystray 系统托盘
│   ├── i18n.py                      # 国际化管理器
│   └── locales/                     # 语言包
│       ├── zh_CN.json               # 中文
│       └── en_US.json               # 英文
│
├── backend/                         # 后端服务
│   ├── app/
│   │   ├── main.py                  # FastAPI 入口（生命周期、路由注册）
│   │   ├── api/                     # API 端点
│   │   │   ├── editor.py            # 编辑器接口
│   │   │   ├── export.py            # 导出接口（LaTeX/Word）
│   │   │   ├── structure.py         # 结构接口（含 3D/PubChem）
│   │   │   └── data.py              # 数据管理接口（元素/化合物/缓存）
│   │   ├── core/                    # 核心模块
│   │   │   ├── chemistry.py         # 化学式解析器
│   │   │   ├── reaction_engine.py   # 方程式平衡器（矩阵法）
│   │   │   ├── rdkit_engine.py      # RDKit 集成（SMILES/SVG/PNG）
│   │   │   ├── molecule_renderer.py # 分子渲染器（2D/3D）
│   │   │   ├── pubchem_api.py       # PubChem API 客户端
│   │   │   └── equation_enhancer.py # 方程式增强（状态符号/条件）
│   │   ├── data/                    # 数据层
│   │   │   ├── database.py          # SQLite 管理器（aiosqlite）
│   │   │   ├── models.py            # Pydantic 数据模型
│   │   │   ├── cache.py             # LRU + TTL 混合缓存
│   │   │   ├── offline_store.py     # 离线数据查询
│   │   │   └── seed_data.py         # 种子数据（元素+化合物+反应）
│   │   ├── plugins/                 # 插件系统
│   │   │   ├── base.py              # ChemPlugin 基类
│   │   │   ├── latex_plugin.py      # LaTeX 导出插件
│   │   │   ├── word_plugin.py       # Word 导出插件
│   │   │   ├── structure_plugin.py  # 结构导出插件
│   │   │   └── reaction_predict_plugin.py  # 反应预测（示例骨架）
│   │   └── services/
│   │       └── plugin_manager.py    # 插件管理器（自动发现）
│   └── requirements.txt             # Python 依赖
│
├── frontend/                        # 前端界面
│   ├── index.html                   # 主页面（SPA）
│   ├── editor.js                    # 主编辑器逻辑
│   ├── i18n.js                      # 前端国际化
│   ├── plugins.js                   # 前端插件管理器
│   ├── molecule-canvas.js           # Canvas 分子结构编辑器
│   ├── molecule-viewer.js           # 3D 分子可视化器
│   └── structure-editor.js          # SMILES 结构编辑器
│
├── plugins/                         # 前端插件
│   ├── word.js                      # Word 前端插件
│   ├── latex.js                     # LaTeX 前端插件
│   └── word-addin/                  # Office Add-in
│       ├── manifest.xml
│       ├── taskpane.html
│       ├── taskpane.js
│       └── commands.js
│
├── scripts/                         # 构建脚本
│   └── build.py                     # PyInstaller 打包
│
├── tests/                           # 测试
│   └── test_chemistry.py
│
└── docs/                            # 文档
    └── plugin-development.md        # 插件开发指南
```

---

## 🚀 快速开始

### 方式一：桌面应用（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/yourname/ChemMaster.git
cd ChemMaster

# 2. 安装依赖
pip install -r backend/requirements.txt
pip install -r requirements-desktop.txt

# 3. 启动桌面应用
python run.py
```

启动后将看到：
- 🖥️ 原生窗口（pywebview）
- 🔻 系统托盘图标（右键菜单：显示/隐藏、语言切换、退出）
- 🗄️ SQLite 数据库自动初始化（含 118 种元素 + 100+ 化合物）

### 方式二：开发模式

```bash
# 仅启动后端服务，浏览器访问
python run.py --dev

# 后端：http://localhost:18020
# 前端：用浏览器打开 frontend/index.html
```

### 方式三：无头模式

```bash
# 仅后端服务（无 GUI）
python run.py --headless
```

### 运行测试

```bash
python tests/test_chemistry.py
```

---

## 📦 打包分发

```bash
# 安装打包工具
pip install pyinstaller

# 执行打包
python scripts/build.py

# 输出：
# Windows: dist/ChemMaster.exe
# macOS:   dist/ChemMaster.app
# Linux:   dist/ChemMaster
```

---

## 📖 API 文档

### 核心端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `GET /` | GET | 服务状态检查 |
| `GET /plugins` | GET | 已加载插件列表 |
| `POST /api/export/formula` | POST | 导出化学式 |
| `POST /api/export/equation` | POST | 导出方程式 |
| `POST /api/export/batch` | POST | 批量导出 |
| `POST /api/export/word/formula` | POST | Word 格式化学式 |
| `POST /api/export/latex/formula` | POST | LaTeX 格式化学式 |
| `POST /api/export/latex/document` | POST | 生成 LaTeX 文档 |
| `POST /api/structure/validate` | POST | 验证 SMILES |
| `POST /api/structure/info` | POST | 获取分子信息 |
| `POST /api/structure/render/svg` | POST | 渲染 SVG 结构图 |
| `POST /api/structure/render/png` | POST | 渲染 PNG 结构图 |
| `POST /api/structure/3d` | POST | 生成 3D SDF 结构 |
| `POST /api/structure/pubchem/3d` | POST | PubChem 3D 结构查询 |
| `GET /api/structure/pubchem/search/{name}` | GET | PubChem 化合物搜索 |

### 数据管理端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `GET /api/data/status` | GET | 数据层状态（离线/在线/缓存统计） |
| `GET /api/data/elements` | GET | 获取所有元素（离线） |
| `GET /api/data/elements/{symbol}` | GET | 按符号查元素 |
| `GET /api/data/compounds/search?q=` | GET | 搜索化合物（离线优先） |
| `GET /api/data/reactions/search?q=` | GET | 搜索反应方程式 |
| `POST /api/data/cache/clear` | POST | 清理过期缓存 |
| `GET /api/data/cache/stats` | GET | 缓存统计 |

### 请求示例

```bash
# 化学式转换
curl -X POST "http://localhost:18020/api/export/formula" \
  -H "Content-Type: application/json" \
  -d '{"formula": "H2SO4", "format": "mhchem"}'

# 方程式平衡
curl -X POST "http://localhost:18020/api/export/equation" \
  -H "Content-Type: application/json" \
  -d '{"equation": "Fe + O2 -> Fe2O3", "balance": true}'

# 查询元素（离线）
curl "http://localhost:18020/api/data/elements/Fe"

# 搜索化合物（离线优先）
curl "http://localhost:18020/api/data/compounds/search?q=乙醇"

# 数据层状态
curl "http://localhost:18020/api/data/status"
```

---

## 🔧 技术栈

### 后端
- **Python 3.8+** — 主要编程语言
- **FastAPI** — Web 框架
- **SQLite + aiosqlite** — 离线数据存储
- **NumPy** — 矩阵运算（方程式平衡）
- **RDKit** — 化学信息学（分子处理、2D/3D 渲染）
- **Pillow** — 图像处理
- **requests** — HTTP 客户端（PubChem API）

### 桌面
- **pywebview** — 原生窗口渲染（非 Electron）
- **pystray** — 系统托盘
- **PyInstaller** — 打包分发

### 前端
- **HTML/CSS/JavaScript** — 基础技术
- **Canvas API** — 分子结构画布编辑器
- **3Dmol.js** — WebGL 3D 分子可视化
- **Office.js** — Microsoft Office 集成

### 数据
- **SQLite** — 本地化学数据库
- **PubChem API** — 在线化合物查询
- **LRU + TTL 缓存** — 内存 512 条 + SQLite 持久化

---

## 🌍 国际化

ChemMaster 支持中/英双语，可通过以下方式切换：

- **桌面托盘** — 右键托盘图标 → 语言 / Language
- **前端代码** — `i18n.switchTo('en_US')` 或 `i18n.switchTo('zh_CN')`

语言包文件位于 `desktop/locales/`，格式为 JSON。

---

## 🔌 插件开发

### 快速创建插件

1. 在 `backend/app/plugins/` 创建 `.py` 文件
2. 继承 `ChemPlugin` 基类
3. 实现 `initialize()` 和 `get_endpoints()`
4. 重启后端，插件自动加载

```python
from backend.app.plugins.base import ChemPlugin, PluginCategory, PluginEndpoint

class MyPlugin(ChemPlugin):
    name = "my_plugin"
    version = "1.0.0"
    description = "我的自定义插件"
    category = PluginCategory.TOOL

    def initialize(self) -> bool:
        return True

    def get_endpoints(self):
        return [
            PluginEndpoint(
                path="/plugins/my-plugin/hello",
                method="GET",
                handler=self._handle_hello,
            ),
        ]

    async def _handle_hello(self):
        return {"message": "Hello!"}
```

详细文档：[插件开发指南](docs/plugin-development.md)

---

## 📊 支持的化学式格式

| 输入 | Unicode 输出 | LaTeX 输出 |
|------|-------------|------------|
| H2O | H₂O | `\ce{H2O}` |
| H2SO4 | H₂SO₄ | `\ce{H2SO4}` |
| Ca(OH)2 | Ca(OH)₂ | `\ce{Ca(OH)2}` |
| NH4+ | NH₄⁺ | `\ce{NH4+}` |
| CO2 | CO₂ | `\ce{CO2}` |
| C6H12O6 | C₆H₁₂O₆ | `\ce{C6H12O6}` |

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

## 🛣️ 发展路线

### 已完成 ✅
- [x] 化学式解析器
- [x] 方程式平衡器
- [x] LaTeX / Word 导出
- [x] REST API 端点
- [x] 有机物结构绘制（Canvas）
- [x] 分子 3D 可视化（3Dmol.js）
- [x] PubChem API 集成
- [x] 矢量图输出（SVG / PNG）
- [x] 插件系统（自动发现 + 分类管理）
- [x] 桌面应用（pywebview + pystray）
- [x] 双模式数据系统（SQLite + PubChem）
- [x] 中英双语支持

### 规划中 📋
- [ ] AI 自然语言转方程式
- [ ] 离子方程式支持
- [ ] 反应类型分类
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

- 遵循 PEP 8（Python）规范
- 添加适当的注释和文档
- 编写测试用例
- 更新 README（如需要）

---

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。

---

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) — 高性能 Web 框架
- [NumPy](https://numpy.org/) — 科学计算库
- [RDKit](https://www.rdkit.org/) — 化学信息学工具包
- [3Dmol.js](https://3dmol.org/) — WebGL 3D 分子可视化
- [PubChem](https://pubchem.ncbi.nlm.nih.gov/) — 化学数据库
- [pywebview](https://pywebview.flowrl.com/) — 轻量级桌面窗口
- [pystray](https://github.com/moses-palmer/pystray) — 系统托盘
- [mhchem](https://ctan.org/pkg/mhchem) — LaTeX 化学式包

---

<p align="center">Made with ❤️ for Chemistry</p>
