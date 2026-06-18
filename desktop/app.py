"""
ChemMaster 桌面应用主入口
Clash-like 体验：系统托盘常驻 + pywebview 原生窗口 + 低资源占用
"""

import logging
import socket
import threading
import time
import sys
import urllib.request
from pathlib import Path

logger = logging.getLogger("chemmaster.desktop")


class ChemMasterDesktop:
    """
    ChemMaster 桌面应用

    架构：
    - 后台线程运行 FastAPI 服务（localhost:port）
    - pywebview 创建原生窗口加载 Web UI
    - pystray 创建系统托盘图标
    """

    def __init__(self, dev_mode: bool = False, port: int = 18020):
        self.window = None
        self.tray = None
        self.server_thread = None
        self.dev_mode = dev_mode
        self.port = port
        self._running = False
        self._locale_callbacks = []

    def _wait_for_server(self, timeout: float = 15.0) -> bool:
        """
        等待 HTTP 服务真正就绪
        不仅检查端口可连接，还验证 /health 端点返回 200
        """
        deadline = time.monotonic() + timeout
        url = f"http://127.0.0.1:{self.port}/health"
        while time.monotonic() < deadline:
            try:
                req = urllib.request.urlopen(url, timeout=1)
                if req.status == 200:
                    return True
            except Exception:
                pass
            time.sleep(0.3)
        return False

    def start_server(self):
        """在后台线程启动 FastAPI 服务"""
        import uvicorn
        from backend.app.main import app

        config = uvicorn.Config(
            app,
            host="127.0.0.1",
            port=self.port,
            log_level="warning",  # 减少日志输出
            access_log=False,
        )
        server = uvicorn.Server(config)

        self.server_thread = threading.Thread(target=server.run, daemon=True)
        self.server_thread.start()

        # 通过 HTTP 请求等待服务真正就绪
        if self._wait_for_server():
            logger.info(f"Backend server started at http://127.0.0.1:{self.port}")
        else:
            logger.error(f"Backend server failed to start on port {self.port}")
            sys.exit(1)

    def start_webview(self):
        """启动 pywebview 原生窗口"""
        try:
            import webview
        except ImportError:
            logger.error("pywebview not installed. Install with: pip install pywebview")
            sys.exit(1)

        self.window = webview.create_window(
            title="ChemMaster - 化学式助手",
            url=f"http://127.0.0.1:{self.port}/static/index.html",
            width=1280,
            height=860,
            min_size=(900, 600),
            background_color="#667eea",
            text_select=True,
        )

        # 窗口关闭回调
        self.window.events.closed += self._on_window_closed

        logger.info("Starting pywebview GUI...")
        webview.start(debug=self.dev_mode)

    def start_tray(self):
        """启动系统托盘（后台线程）"""
        try:
            from .tray import create_tray
            self.tray = create_tray(self)
            if self.tray:
                threading.Thread(target=self.tray.run, daemon=True).start()
                logger.info("System tray started")
        except Exception as e:
            logger.warning(f"Failed to start system tray: {e}")

    def start(self):
        """
        启动完整桌面应用
        1. 启动 FastAPI 后台服务
        2. 启动系统托盘
        3. 启动 pywebview 主窗口（阻塞）
        """
        self._running = True
        logger.info("Starting ChemMaster Desktop...")

        # 1. 启动后端服务
        self.start_server()

        # 2. 启动系统托盘
        self.start_tray()

        # 3. 等待一下确保页面可加载
        time.sleep(0.5)

        # 4. 启动主窗口（阻塞直到窗口关闭）
        self.start_webview()

    def start_headless(self):
        """
        无头模式：仅启动后端服务（开发/调试用）
        """
        import uvicorn
        from backend.app.main import app

        logger.info("Starting in headless mode...")
        uvicorn.run(app, host="0.0.0.0", port=self.port, reload=self.dev_mode)

    def quit(self):
        """退出应用"""
        self._running = False
        logger.info("Application quitting...")
        if self.window:
            try:
                self.window.destroy()
            except Exception:
                pass
        sys.exit(0)

    def notify_locale_change(self, locale: str):
        """通知语言切换"""
        for callback in self._locale_callbacks:
            try:
                callback(locale)
            except Exception as e:
                logger.error(f"Locale callback error: {e}")

    def _on_window_closed(self):
        """窗口关闭时的处理"""
        logger.info("Window closed")
        self._running = False
