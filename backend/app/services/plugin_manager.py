"""
ChemMaster 插件管理器
负责自动发现、加载、注册和调度所有插件
"""

import importlib
import inspect
import logging
import pkgutil
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from ..plugins.base import ChemPlugin, PluginCategory, PluginEndpoint

logger = logging.getLogger("chemmaster.plugins")


class PluginManager:
    """
    插件管理中心

    职责：
    1. 自动扫描 backend/app/plugins/ 目录，发现所有 ChemPlugin 子类
    2. 实例化并初始化插件
    3. 将插件声明的 API 端点注册到 FastAPI 应用
    4. 按分类管理插件，提供查询接口
    """

    def __init__(self):
        # 已注册的插件实例 {name: plugin_instance}
        self._plugins: Dict[str, ChemPlugin] = {}
        # 按分类索引 {category: [plugin_name, ...]}
        self._categories: Dict[str, List[str]] = {}
        # FastAPI 应用引用（在 discover_and_load 时设置）
        self._app = None

    # ====== 插件发现与加载 ======

    def discover_and_load(self, app=None) -> Dict[str, bool]:
        """
        自动发现并加载所有插件。

        扫描 backend/app/plugins/ 目录下所有 .py 文件，
        找到 ChemPlugin 的子类并实例化。

        Args:
            app: FastAPI 应用实例，用于注册插件端点

        Returns:
            {plugin_name: success_bool} 加载结果
        """
        self._app = app
        results = {}

        # 插件目录路径
        plugins_dir = Path(__file__).parent.parent / "plugins"

        if not plugins_dir.exists():
            logger.warning(f"Plugins directory not found: {plugins_dir}")
            return results

        # 遍历 plugins 目录下所有模块
        for finder, module_name, is_pkg in pkgutil.iter_modules([str(plugins_dir)]):
            if module_name.startswith("_") or module_name == "base":
                continue

            try:
                # 动态导入模块
                module = importlib.import_module(
                    f"..plugins.{module_name}", package="app.services"
                )

                # 查找模块中所有 ChemPlugin 子类
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        inspect.isclass(attr)
                        and issubclass(attr, ChemPlugin)
                        and attr is not ChemPlugin
                    ):
                        plugin = attr()
                        success = self.register(plugin)
                        results[plugin.name] = success

            except Exception as e:
                logger.error(f"Failed to load plugin module '{module_name}': {e}")
                results[module_name] = False

        return results

    # ====== 插件注册与管理 ======

    def register(self, plugin: ChemPlugin) -> bool:
        """
        注册并初始化一个插件。

        Args:
            plugin: ChemPlugin 子类实例

        Returns:
            True 表示注册成功
        """
        if not plugin.name:
            logger.error(f"Plugin {type(plugin).__name__} has no name")
            return False

        if plugin.name in self._plugins:
            logger.warning(f"Plugin '{plugin.name}' already registered, skipping")
            return False

        # 初始化插件
        try:
            success = plugin.initialize()
            plugin._mark_initialized(success)
        except Exception as e:
            plugin._mark_initialized(False, str(e))
            logger.error(f"Plugin '{plugin.name}' init failed: {e}")
            return False

        if not success:
            logger.warning(f"Plugin '{plugin.name}' initialize() returned False")
            return False

        # 注册到字典
        self._plugins[plugin.name] = plugin

        # 按分类索引
        cat = plugin.category
        if cat not in self._categories:
            self._categories[cat] = []
        self._categories[cat].append(plugin.name)

        # 注册插件端点到 FastAPI
        if self._app:
            self._register_endpoints(plugin)

        logger.info(f"Plugin registered: {plugin}")
        return True

    def unregister(self, name: str) -> bool:
        """卸载指定插件"""
        plugin = self._plugins.pop(name, None)
        if not plugin:
            return False

        plugin.cleanup()

        # 从分类索引中移除
        cat = plugin.category
        if cat in self._categories and name in self._categories[cat]:
            self._categories[cat].remove(name)

        logger.info(f"Plugin unregistered: {name}")
        return True

    # ====== 查询接口 ======

    def get_plugin(self, name: str) -> Optional[ChemPlugin]:
        """按名称获取插件实例"""
        return self._plugins.get(name)

    def get_plugins_by_category(self, category: str) -> List[ChemPlugin]:
        """按分类获取插件列表"""
        names = self._categories.get(category, [])
        return [self._plugins[n] for n in names if n in self._plugins]

    def list_plugins(self) -> List[Dict[str, Any]]:
        """返回所有已注册插件的摘要信息"""
        return [p.get_status() for p in self._plugins.values()]

    def get_all_status(self) -> Dict[str, Any]:
        """返回插件管理器全局状态"""
        return {
            "total": len(self._plugins),
            "categories": {
                cat: len(names) for cat, names in self._categories.items()
            },
            "plugins": self.list_plugins(),
        }

    # ====== 兼容旧接口 ======

    def register_exporter(self, name: str, func: Callable):
        """兼容旧接口：注册一个导出函数"""
        if not hasattr(self, "_legacy_exporters"):
            self._legacy_exporters: Dict[str, Callable] = {}
        self._legacy_exporters[name] = func

    def get_exporter(self, name: str):
        """兼容旧接口：获取导出函数"""
        if hasattr(self, "_legacy_exporters"):
            return self._legacy_exporters.get(name)
        return None

    def run_exporter(self, name: str, *args, **kwargs) -> Any:
        """兼容旧接口：运行导出函数"""
        func = self.get_exporter(name)
        if func is None:
            return {"error": f"exporter '{name}' not found"}
        return func(*args, **kwargs)

    def register_db(self, name: str, func: Callable):
        """兼容旧接口：注册数据库插件"""
        if not hasattr(self, "_legacy_db"):
            self._legacy_db: Dict[str, Callable] = {}
        self._legacy_db[name] = func

    def get_db(self, name: str):
        """兼容旧接口：获取数据库插件"""
        if hasattr(self, "_legacy_db"):
            return self._legacy_db.get(name)
        return None

    def run_db(self, name: str, *args, **kwargs) -> Any:
        """兼容旧接口：运行数据库插件"""
        func = self.get_db(name)
        if func is None:
            return {"error": f"db plugin '{name}' not found"}
        return func(*args, **kwargs)

    # ====== 内部方法 ======

    def _register_endpoints(self, plugin: ChemPlugin):
        """将插件声明的端点注册到 FastAPI 应用"""
        endpoints = plugin.get_endpoints()
        if not endpoints:
            return

        for ep in endpoints:
            if not ep.handler:
                logger.warning(f"Plugin '{plugin.name}' endpoint {ep.path} has no handler")
                continue

            tags = ep.tags or [plugin.name]
            route_kwargs = {
                "path": ep.path,
                "endpoint": ep.handler,
                "tags": tags,
                "summary": ep.summary or f"{plugin.name} - {ep.path}",
            }

            # 根据 HTTP 方法注册路由
            method = ep.method.upper()
            if method == "GET":
                self._app.get(**route_kwargs)
            elif method == "POST":
                self._app.post(**route_kwargs)
            elif method == "PUT":
                self._app.put(**route_kwargs)
            elif method == "DELETE":
                self._app.delete(**route_kwargs)
            else:
                logger.warning(f"Unsupported HTTP method '{method}' for {ep.path}")

            logger.debug(f"  Endpoint registered: {method} {ep.path}")


# 全局单例：所有模块共享同一个插件管理器实例
plugin_manager = PluginManager()
