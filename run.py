"""
ChemMaster 统一启动入口

用法：
    python run.py              # 桌面模式（pywebview 窗口 + 系统托盘）
    python run.py --dev        # 开发模式（仅启动后端，浏览器访问）
    python run.py --headless   # 无头模式（仅后端服务）
"""

import sys
import argparse
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("chemmaster")


def main():
    parser = argparse.ArgumentParser(description="ChemMaster - 化学式助手")
    parser.add_argument("--dev", action="store_true", help="开发模式（仅启动后端）")
    parser.add_argument("--headless", action="store_true", help="无头模式（仅后端服务）")
    parser.add_argument("--port", type=int, default=18020, help="服务端口（默认 18020）")
    parser.add_argument("--locale", default="zh_CN", help="默认语言（zh_CN / en_US）")
    args = parser.parse_args()

    # 确保项目根目录在 Python 路径中
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    if args.dev or args.headless:
        # 开发/无头模式：仅启动 FastAPI 后端
        import uvicorn
        from backend.app.main import app

        logger.info(f"Starting in {'dev' if args.dev else 'headless'} mode...")
        logger.info(f"Backend: http://localhost:{args.port}")
        logger.info(f"Open frontend/index.html in browser for UI")

        uvicorn.run(
            "backend.app.main:app",
            host="0.0.0.0",
            port=args.port,
            reload=args.dev,
        )
    else:
        # 桌面模式：pywebview + pystray
        try:
            from desktop.app import ChemMasterDesktop
        except ImportError as e:
            logger.error(f"Desktop dependencies not installed: {e}")
            logger.info("Install with: pip install -r requirements-desktop.txt")
            logger.info("Or use --dev mode: python run.py --dev")
            sys.exit(1)

        logger.info("Starting ChemMaster Desktop...")
        app = ChemMasterDesktop(dev_mode=False)
        app.start()


if __name__ == "__main__":
    main()
