# ChemMaster 插件开发指南

## 概述

ChemMaster 采用模块化插件架构，支持动态扩展功能。插件可以：
- 提供新的 API 端点
- 集成外部数据库或 AI 模型
- 添加新的导出格式
- 实现化学分析或预测功能

## 插件分类

| 分类 | 说明 | 示例 |
|------|------|------|
| `export` | 导出类 | LaTeX、Word、PDF 导出 |
| `analysis` | 分析类 | 分子性质计算、光谱预测 |
| `prediction` | 预测类 | 反应预测、产物预测 |
| `database` | 数据库类 | PubChem、ChEMBL 集成 |
| `generator` | 生成类 | 结构自动生成、命名 |
| `tool` | 工具类 | 格式转换、单位换算 |

## 快速开始

### 1. 创建插件文件

在 `backend/app/plugins/` 目录下创建新文件，例如 `my_plugin.py`：

```python
"""
我的自定义插件
"""

from typing import List
from .base import ChemPlugin, PluginCategory, PluginEndpoint


class MyPlugin(ChemPlugin):
    """示例插件"""

    # ---- 必填属性 ----
    name = "my_plugin"              # 唯一标识（小写下划线）
    version = "1.0.0"               # 语义化版本
    description = "我的自定义插件"    # 一句话描述
    category = PluginCategory.TOOL  # 插件分类

    # ---- 生命周期 ----

    def initialize(self) -> bool:
        """初始化插件，返回 True 表示成功"""
        # 加载模型、建立连接等
        return True

    def cleanup(self) -> None:
        """清理资源（可选）"""
        pass

    # ---- API 端点 ----

    def get_endpoints(self) -> List[PluginEndpoint]:
        """声明本插件提供的 API 端点"""
        return [
            PluginEndpoint(
                path="/plugins/my-plugin/hello",
                method="GET",
                handler=self._handle_hello,
                summary="示例端点",
                tags=["my-plugin"],
            ),
        ]

    async def _handle_hello(self):
        """端点处理函数"""
        return {"message": "Hello from MyPlugin!"}
```

### 2. 自动加载

插件管理器会自动扫描 `backend/app/plugins/` 目录，发现所有继承 `ChemPlugin` 的类并加载。**无需手动注册**。

### 3. 验证

启动后端后访问 `/plugins` 端点，确认插件出现在列表中：

```bash
curl http://localhost:8000/plugins
```

## 插件基类 API

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `name` | `str` | 插件唯一标识 |
| `version` | `str` | 版本号 |
| `description` | `str` | 描述 |
| `category` | `str` | 分类（PluginCategory 枚举值） |

### 方法

| 方法 | 说明 |
|------|------|
| `initialize() -> bool` | 初始化插件（必须实现） |
| `get_endpoints() -> List[PluginEndpoint]` | 声明 API 端点（必须实现） |
| `cleanup() -> None` | 清理资源（可选） |
| `get_status() -> dict` | 返回运行状态（可选覆盖） |
| `get_config_schema() -> dict` | 返回配置项 schema（可选） |

### PluginEndpoint 数据结构

```python
PluginEndpoint(
    path="/plugins/my-endpoint",   # 路由路径
    method="POST",                 # HTTP 方法
    handler=my_handler,            # 处理函数
    summary="端点描述",             # OpenAPI 文档描述
    tags=["my-plugin"],            # OpenAPI 标签
)
```

## 前端插件开发

### 注册前端插件

```javascript
const myPlugin = {
    name: 'my-plugin',
    description: '我的前端插件',
    category: 'tool',
    version: '1.0.0',

    async init() {
        console.log('My plugin initialized');
    },

    destroy() {
        console.log('My plugin destroyed');
    }
};

// 注册到全局插件管理器
pluginManager.register(myPlugin);
```

### 查询插件

```javascript
// 获取指定插件
const plugin = pluginManager.getPlugin('my-plugin');

// 按分类获取
const exportPlugins = pluginManager.getPluginsByCategory('export');

// 获取所有分类
const categories = pluginManager.getCategories();
```

## 已有插件

| 插件 | 分类 | 说明 |
|------|------|------|
| `latex_export` | export | LaTeX 格式导出 |
| `word_export` | export | Word 格式导出 |
| `structure_export` | export | 化学结构多格式导出 |
| `reaction_predict` | prediction | 反应预测（示例骨架） |

## 最佳实践

1. **命名规范**：插件 `name` 使用小写下划线，文件名与插件名一致
2. **错误处理**：`initialize()` 失败时返回 `False`，不要抛异常
3. **资源清理**：在 `cleanup()` 中释放模型、关闭连接
4. **端点路径**：以 `/plugins/插件名/` 为前缀，避免与核心路由冲突
5. **向后兼容**：保留原有类和函数，新增 ChemPlugin 子类包装
