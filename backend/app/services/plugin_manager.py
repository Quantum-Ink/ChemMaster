from typing import Dict, Callable, Any

class PluginManager:
    """
    V13 插件管理中心（轻量版）
    - 注册插件
    - 调用插件
    """

    def __init__(self):
        self.exporters: Dict[str, Callable] = {}
        self.db_plugins: Dict[str, Callable] = {}

    # =========================
    # 注册导出插件（Word / LaTeX）
    # =========================
    def register_exporter(self, name: str, func: Callable):
        self.exporters[name] = func

    def get_exporter(self, name: str):
        return self.exporters.get(name)

    def run_exporter(self, name: str, *args, **kwargs) -> Any:
        if name not in self.exporters:
            return {"error": f"exporter '{name}' not found"}
        return self.exporters[name](*args, **kwargs)

    # =========================
    # 数据库插件（PubChem等）
    # =========================
    def register_db(self, name: str, func: Callable):
        self.db_plugins[name] = func

    def get_db(self, name: str):
        return self.db_plugins.get(name)

    def run_db(self, name: str, *args, **kwargs) -> Any:
        if name not in self.db_plugins:
            return {"error": f"db plugin '{name}' not found"}
        return self.db_plugins[name](*args, **kwargs)


# =========================
# 全局单例（非常重要）
# =========================
plugin_manager = PluginManager()