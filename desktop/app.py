"""
ChemMaster 桌面应用主入口
Clash-like 体验：系统托盘常驻 + pywebview 原生窗口 + 低资源占用
"""

import logging
import threading
import time
import sys
from pathlib import Path

logger = logging.getLogger("chemmaster.desktop")


class ChemMasterDesktop:
    """
    ChemMaster 桌面应用

    架构：
    - 后台线程运行 FastAPI 服务（localhost:18020）
    - pywebview 创建原生窗口加载 Web UI
    - pystray 创建系统托盘图标
    """

    def __init__(self, dev_mode: bool = False):
        self.window = None
        self.tray = None
        self.server_thread = None
        self.dev_mode = dev_mode
        self._running = False
        self._locale_callbacks = []

    def start_server(self):
        """在后台线程启动 FastAPI 服务"""
        import uvicorn
        from app.main import app

        config = uvicorn.Config(
            app,
            host="127.0.0.1",
            port=18020,
            log_level="warning",  # 减少日志输出
            access_log=False,
        )
        server = uvicorn.Server(config)

        # 等待服务启动
        self._server_ready = False

        def run():
            self._server_ready = True
            server.run()

        self.server_thread = threading.Thread(target=run, daemon=True)
        self.server_thread.start()

        # 等待服务就绪
        for _ in range(50):  # 最多等 5 秒
            if self._server_ready:
                break
            time.sleep(0.1)

        logger.info("Backend server started at http://127.0.0.1:18020")

    def start_webview(self):
        """启动 pywebview 原生窗口"""
        try:
            import webview
        except ImportError:
            logger.error("pywebview not installed. Install with: pip install pywebview")
            sys.exit(1)

        self.window = webview.create_window(
            title="ChemMaster - 化学式助手",
            url="http://127.0.0.1:18020",
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

        # 3. 启动主窗口（阻塞直到窗口关闭）
        self.start_webview()

    def start_headless(self):
        """
        无头模式：仅启动后端服务（开发/调试用）
        """
        import uvicorn
        from app.main import app

        logger.info("Starting in headless mode...")
        uvicorn.run(app, host="0.0.0.0", port=18020, reload=self.dev_mode)

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
