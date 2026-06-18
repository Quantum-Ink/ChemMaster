"""
ChemMaster 后端插件管理器
负责注册和调度导出插件（Word/LaTeX）和数据库插件（PubChem 等）
"""

from typing import Dict, Callable, Any


class PluginManager:
    """插件管理中心：统一注册、查找、调用各类插件"""

    def __init__(self):
        # 导出类插件（Word / LaTeX 等格式转换）
        self.exporters: Dict[str, Callable] = {}
        # 数据库类插件（PubChem 等数据源）
        self.db_plugins: Dict[str, Callable] = {}

    # ---- 导出插件 ----

    def register_exporter(self, name: str, func: Callable):
        """注册一个导出插件"""
        self.exporters[name] = func

    def get_exporter(self, name: str):
        """按名称获取导出插件"""
        return self.exporters.get(name)

    def run_exporter(self, name: str, *args, **kwargs) -> Any:
        """运行指定的导出插件"""
        if name not in self.exporters:
            return {"error": f"exporter '{name}' not found"}
        return self.exporters[name](*args, **kwargs)

    # ---- 数据库插件 ----

    def register_db(self, name: str, func: Callable):
        """注册一个数据库插件"""
        self.db_plugins[name] = func

    def get_db(self, name: str):
        """按名称获取数据库插件"""
        return self.db_plugins.get(name)

    def run_db(self, name: str, *args, **kwargs) -> Any:
        """运行指定的数据库插件"""
        if name not in self.db_plugins:
            return {"error": f"db plugin '{name}' not found"}
        return self.db_plugins[name](*args, **kwargs)


# 全局单例：所有模块共享同一个插件管理器实例
plugin_manager = PluginManager()