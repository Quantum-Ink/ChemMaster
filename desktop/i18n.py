"""
ChemMaster 国际化管理器
支持中/英双语切换
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger("chemmaster.i18n")

# 语言包目录
LOCALES_DIR = Path(__file__).parent / "locales"


class I18nManager:
    """
    国际化管理器
    加载 JSON 语言包，提供翻译函数
    """

    def __init__(self, default_locale: str = "zh_CN"):
        self.locale: str = default_locale
        self.translations: Dict[str, Dict[str, str]] = {}
        self._load_all()

    def _load_all(self):
        """加载所有语言包"""
        if not LOCALES_DIR.exists():
            logger.warning(f"Locales directory not found: {LOCALES_DIR}")
            return

        for json_file in LOCALES_DIR.glob("*.json"):
            locale = json_file.stem
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    self.translations[locale] = json.load(f)
                logger.info(f"Loaded locale: {locale} ({len(self.translations[locale])} keys)")
            except Exception as e:
                logger.error(f"Failed to load locale {locale}: {e}")

    def t(self, key: str, **kwargs) -> str:
        """
        翻译指定 key
        支持参数替换：t("greeting", name="World") → "Hello, World!"
        """
        text = self.translations.get(self.locale, {}).get(key)
        if text is None:
            # 回退到英文
            text = self.translations.get("en_US", {}).get(key)
        if text is None:
            # 回退到 key 本身
            return key

        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, IndexError):
                pass
        return text

    def set_locale(self, locale: str) -> bool:
        """切换语言"""
        if locale in self.translations:
            self.locale = locale
            logger.info(f"Locale changed to: {locale}")
            return True
        logger.warning(f"Locale not found: {locale}")
        return False

    def get_available_locales(self) -> list:
        """获取可用语言列表"""
        return list(self.translations.keys())

    def get_translations(self, locale: str = None) -> Dict[str, str]:
        """获取指定语言的完整翻译字典"""
        return self.translations.get(locale or self.locale, {})


# 全局实例
i18n = I18nManager()
