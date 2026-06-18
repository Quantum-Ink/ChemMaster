"""
ChemMaster 系统托盘
Clash-like 体验：显示/隐藏窗口、语言切换、状态查看、退出
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .app import ChemMasterDesktop

logger = logging.getLogger("chemmaster.tray")


def create_tray_icon_image():
    """创建托盘图标（简单的化学烧杯图案）"""
    try:
        from PIL import Image, ImageDraw
        # 创建 64x64 图标
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 绘制烧杯轮廓（简化）
        draw.rectangle([20, 10, 44, 15], fill=(102, 126, 234))  # 烧杯口
        draw.rectangle([18, 15, 46, 50], outline=(102, 126, 234), width=2)  # 烧杯体
        draw.rectangle([22, 30, 42, 48], fill=(118, 75, 162))  # 液体
        draw.polygon([(18, 50), (46, 50), (42, 58), (22, 58)], fill=(102, 126, 234))  # 烧杯底

        return img
    except ImportError:
        # 如果没有 PIL，返回 None（pystray 会使用默认图标）
        return None


def create_tray(app: "ChemMasterDesktop"):
    """
    创建系统托盘

    Args:
        app: 桌面应用实例
    """
    try:
        import pystray
        from pystray import MenuItem as Item
    except ImportError:
        logger.warning("pystray not installed, system tray disabled")
        return None

    from .i18n import i18n

    def _build_menu():
        """根据当前语言构建菜单"""
        def on_show_window(icon, item):
            if app.window:
                app.window.show()
                app.window.restore()

        def on_set_locale_zh(icon, item):
            i18n.set_locale("zh_CN")
            app.notify_locale_change("zh_CN")
            icon.menu = _build_menu()

        def on_set_locale_en(icon, item):
            i18n.set_locale("en_US")
            app.notify_locale_change("en_US")
            icon.menu = _build_menu()

        def on_status(icon, item):
            try:
                import requests
                resp = requests.get(f"http://127.0.0.1:{app.port}/api/data/status", timeout=2)
                data = resp.json()
                db_stats = data.get("database", {})
                msg = i18n.t("tray.status_msg",
                             compounds=db_stats.get('compounds', 0),
                             cache=db_stats.get('cache_entries', 0))
                icon.notify(msg, i18n.t("app.title"))
            except Exception:
                icon.notify(i18n.t("tray.status_running"), i18n.t("app.title"))

        def on_quit(icon, item):
            logger.info("Quitting application...")
            icon.stop()
            app.quit()

        return pystray.Menu(
            Item(i18n.t("tray.show_window"), on_show_window, default=True),
            pystray.Menu.SEPARATOR,
            Item(i18n.t("tray.language"), pystray.Menu(
                Item("中文", on_set_locale_zh),
                Item("English", on_set_locale_en),
            )),
            Item(i18n.t("tray.status"), on_status),
            pystray.Menu.SEPARATOR,
            Item(i18n.t("tray.quit"), on_quit),
        )

    icon_image = create_tray_icon_image()
    icon = pystray.Icon(
        "ChemMaster",
        icon_image,
        i18n.t("app.title"),
        _build_menu(),
    )

    return icon
