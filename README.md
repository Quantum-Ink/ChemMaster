🧪 核心功能
1. 化学式解析器 (chemistry.py)

解析化学式（如 H2SO4, Ca(OH)2）

转换为 Unicode 下标格式（H₂SO₄）

转换为 LaTeX 格式（\ce{H2SO4}）

2. 方程式平衡器 (reaction_engine.py)

使用矩阵法自动平衡化学方程式

示例：Fe + O2 -> Fe2O3 → 4Fe + 3O2 -> 2Fe2O3

3. LaTeX 导出插件 (letax_plugin.py)

支持 mhchem 包格式
生成完整 LaTeX 文档
4. Word 导出插件 (word_plugin.py)
生成 Unicode 下标格式
生成 HTML 和 RTF 格式
提供 Office.js 集成代码
📝 Word Add-in
完整的 Office 插件实现：


plugins/word-addin/
├── manifest.xml      # Office Add-in 配置
├── taskpane.html     # 任务面板界面
├── taskpane.js       # 任务面板逻辑
└── commands.js       # 命令处理
功能特点：

🎨 现代化 UI 设计
📊 实时预览转换结果
📋 支持批量处理
📜 历史记录功能
🔄 一键插入到 Word 文档
🔌 前端插件
word.js - Word 前端插件
latex.js - LaTeX 前端插件
plugins.js - 插件管理系统
🚀 API 端点
端点	方法	描述
/api/export/formula	POST	导出化学式
/api/export/equation	POST	导出方程式
/api/export/batch	POST	批量导出
/api/export/word/*	POST	Word 格式
/api/export/latex/*	POST	LaTeX 格式
📊 测试结果

[PASS] Formula parser tests passed
[PASS] Reaction parser tests passed
[PASS] Equation balancer tests passed
[PASS] Format conversion tests passed

[PASS] All tests passed!
📖 使用示例
化学式转换：


// Word 格式
wordPlugin.convertFormula('H2SO4')
// 输出: H₂SO₄

// LaTeX 格式
latexPlugin.convertFormula('H2SO4', 'mhchem')
// 输出: \ce{H2SO4}
方程式平衡：


wordPlugin.convertEquation('Fe + O2 -> Fe2O3')
// 输出: 4Fe + 3O₂ → 2Fe₂O₃
📚 文档
详细使用说明请查看 plugins/README.md