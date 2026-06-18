"""
ChemMaster 插件基类
所有插件必须继承 ChemPlugin 并实现抽象方法
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class PluginCategory(str, Enum):
    """插件分类枚举"""
    EXPORT = "export"           # 导出类（LaTeX、Word、PDF 等）
    ANALYSIS = "analysis"       # 分析类（分子性质、光谱预测等）
    PREDICTION = "prediction"   # 预测类（反应预测、产物预测等）
    DATABASE = "database"       # 数据库类（PubChem、ChEMBL 等）
    GENERATOR = "generator"     # 生成类（结构生成、命名等）
    TOOL = "tool"               # 工具类（格式转换、计算等）


@dataclass
class PluginEndpoint:
    """
    插件声明的 API 端点
    插件通过 get_endpoints() 返回端点列表，由插件管理器自动注册到 FastAPI
    """
    path: str                   # 路由路径，如 "/predict/reaction"
    method: str = "POST"        # HTTP 方法
    handler: Callable = None    # 处理函数
    summary: str = ""           # 端点描述
    tags: List[str] = field(default_factory=list)  # OpenAPI 标签


class ChemPlugin(ABC):
    """
    ChemMaster 插件基类

    所有插件必须继承此类并实现：
    - name: 插件唯一标识（小写下划线）
    - version: 语义化版本号
    - description: 一句话描述
    - category: 插件分类（PluginCategory 枚举值）
    - initialize(): 初始化逻辑
    - get_endpoints(): 声明本插件提供的 API 端点

    可选实现：
    - cleanup(): 清理资源
    - get_status(): 返回健康状态
    - get_config_schema(): 返回配置项 schema
    """

    # ---- 子类必须定义的属性 ----
    name: str = ""
    version: str = "0.1.0"
    description: str = ""
    category: str = PluginCategory.TOOL

    def __init__(self):
        self._initialized: bool = False
        self._error: Optional[str] = None

    # ---- 生命周期 ----

    @abstractmethod
    def initialize(self) -> bool:
        """
        初始化插件，在插件加载时调用。
        返回 True 表示初始化成功，False 表示失败。
        失败时插件管理器会跳过该插件。
        """
        ...

    def cleanup(self) -> None:
        """清理插件资源，在插件卸载时调用。默认无操作。"""
        pass

    # ---- 端点注册 ----

    @abstractmethod
    def get_endpoints(self) -> List[PluginEndpoint]:
        """
        返回本插件提供的 API 端点列表。
        插件管理器会自动将这些端点注册到 FastAPI 应用。
        """
        ...

    # ---- 状态与配置 ----

    def get_status(self) -> Dict[str, Any]:
        """返回插件运行状态，可用于健康检查。"""
        return {
            "name": self.name,
            "version": self.version,
            "category": self.category,
            "initialized": self._initialized,
            "error": self._error,
        }

    def get_config_schema(self) -> Optional[Dict[str, Any]]:
        """返回插件配置项的 JSON Schema（可选）。"""
        return None

    # ---- 内部方法 ----

    def _mark_initialized(self, success: bool, error: Optional[str] = None):
        """标记插件初始化状态（由插件管理器调用）"""
        self._initialized = success
        self._error = error

    def __repr__(self):
        return f"<Plugin {self.name} v{self.version} [{self.category}]>"
