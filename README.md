# ⚗️ ChemMaster

**离线优先化学计算桌面应用** — Go + Wails v2 + Vue3 + TypeScript

## 定位

ChemMaster 是一个：
- 离线优先 (Offline First)
- 插件化 (Plugin-Based)
- Clash 风格轻量级桌面应用
- 化学计算 + 化学数据库 + 化学表达渲染系统

目标：本地化 PubChem + ChemDraw Lite + 化学计算引擎 + 数据源聚合器

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Go 1.21+ |
| 桌面框架 | Wails v2 |
| 前端 | Vue3 + TypeScript |
| 数据库 | SQLite (modernc.org/sqlite) |
| 加密 | AES-256-GCM |
| UI 风格 | Clash for Windows 深色主题 |

## 核心功能

### 🔬 化学式解析
- 支持 H2SO4 / Ca(OH)2 / Al2(SO4)3 / [Cu(NH3)4]SO4
- 元素拆解、原子计数、分子量计算
- Unicode 下标转换、LaTeX 输出
- 性能: <10ms

### ⚖️ 方程式配平
- 矩阵法 + 高斯消元
- 配平结果、系数矩阵、守恒验证
- 性能: <100ms

### 🧪 化学反应表达 (Reaction AST)
- 支持 → ⇌ ⟶ = 等分隔符
- 条件标注 (Δ/hν/catalyst/温度/压力)
- 状态标记 (↑气体/↓沉淀/(aq)(s)(l)(g))
- 三种输出: 分子方程式、完整离子方程式、净离子方程式

### ⚡ 离子方程式引擎
- 分子方程式→完整离子方程式→净离子方程式
- 旁观离子检测
- 电荷守恒验证

### 📤 导出系统
- LaTeX (mhchem 格式)
- Unicode 下标
- HTML
- PNG (2x/4x 高清)

### 🗄️ 化学数据库
- 本地 SQLite: 元素周期表、化合物库、反应库
- 在线扩展: PubChem API、ChEBI API
- LRU/TTL 缓存

### 🔌 插件系统
- parser / solver / database / export / ai 分类
- 启用/禁用/版本控制

### 🔒 安全
- AES-256-GCM 加密所有敏感数据
- API Key / Cookie 加密存储
- 凭证加密存储

## 项目结构

```
ChemMaster/
├── main.go                          # Wails 入口
├── wails.json                       # Wails 配置
├── go.mod                           # Go 模块
├── Makefile                         # 构建脚本
├── internal/
│   ├── app/
│   │   ├── app.go                   # 应用主结构
│   │   └── bindings.go              # Wails 绑定 (前端可调用的 API)
│   ├── chemistry/
│   │   ├── formula.go               # 化学式解析引擎
│   │   ├── balancer.go              # 方程式配平引擎 (矩阵法)
│   │   ├── reaction.go              # Reaction AST
│   │   ├── ion.go                   # 离子方程式引擎
│   │   └── renderer.go             # LaTeX/HTML/Unicode 渲染
│   ├── database/
│   │   └── database.go              # SQLite 数据库
│   ├── encryption/
│   │   └── encryption.go            # AES-256 加密
│   ├── plugin/
│   │   └── plugin.go                # 插件管理器
│   └── provider/
│       └── provider.go              # 数据源管理 (PubChem 等)
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── index.html
│   └── src/
│       ├── main.ts                  # Vue 入口
│       ├── App.vue                  # 主布局 (侧边栏 + 内容区)
│       ├── assets/styles.css        # Clash 风格深色主题
│       ├── router/index.ts          # 路由
│       ├── wails/app.ts             # Wails 绑定包装 (含 mock)
│       └── views/
│           ├── Home.vue             # 首页
│           ├── Formula.vue          # 化学式解析
│           ├── Equation.vue         # 方程式配平
│           ├── Reaction.vue         # 化学反应表达
│           ├── Ion.vue              # 离子方程式
│           ├── Database.vue         # 化学数据库
│           ├── Providers.vue        # 数据源管理
│           ├── Plugins.vue          # 插件管理
│           └── Settings.vue         # 设置
└── build/
    └── README.md                    # 构建说明
```

## 快速开始

### 前置条件

1. Go 1.21+ — https://go.dev/dl/
2. Node.js 18+ — https://nodejs.org/
3. Wails CLI: `go install github.com/wailsapp/wails/v2/cmd/wails@latest`

### 开发模式

```bash
# 安装前端依赖
cd frontend && npm install && cd ..

# 启动开发服务器 (热重载)
wails dev
```

### 生产构建

```bash
# Windows 构建 (隐藏控制台窗口)
wails build -platform windows/amd64 -ldflags "-H windowsgui"

# 输出: build/bin/ChemMaster.exe
```

### 调试构建

```bash
wails build -platform windows/amd64
```

## 性能要求

| 操作 | 目标 |
|---|---|
| 启动 | < 2s |
| 本地查询 | < 50ms |
| 配平 | < 100ms |
| 化学解析 | < 10ms |

## License

MIT License - Quantum-Ink
