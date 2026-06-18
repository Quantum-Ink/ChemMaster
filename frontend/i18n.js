/**
 * ChemMaster 前端国际化模块
 * 通过 data-i18n 属性自动翻译 DOM 元素
 * 支持中/英双语实时切换
 */

class I18n {
    constructor() {
        /** @type {string} 当前语言 */
        this.locale = localStorage.getItem('chemmaster_locale') || 'zh_CN';
        /** @type {Object<string, string>} 翻译字典 */
        this.translations = {};
        /** @type {Function[]} 语言切换回调 */
        this._callbacks = [];
    }

    /**
     * 加载语言包
     * @param {string} locale - 语言代码，如 'zh_CN', 'en_US'
     */
    async load(locale) {
        try {
            const response = await fetch(`/locales/${locale}.json`);
            if (!response.ok) {
                // 回退：尝试从静态文件加载
                const fallback = await fetch(`/static/../desktop/locales/${locale}.json`);
                if (fallback.ok) {
                    this.translations = await fallback.json();
                } else {
                    console.warn(`[i18n] Locale ${locale} not found`);
                    return;
                }
            } else {
                this.translations = await response.json();
            }

            this.locale = locale;
            localStorage.setItem('chemmaster_locale', locale);
            this.apply();

            // 触发回调
            this._callbacks.forEach(cb => cb(locale));

            console.log(`[i18n] Loaded locale: ${locale}`);
        } catch (error) {
            console.error(`[i18n] Failed to load locale ${locale}:`, error);
        }
    }

    /**
     * 翻译指定 key
     * @param {string} key - 翻译键
     * @param {Object} [params] - 替换参数
     * @returns {string}
     */
    t(key, params = {}) {
        let text = this.translations[key];
        if (text === undefined) {
            return key; // 回退到 key 本身
        }

        // 参数替换 {name} → value
        Object.entries(params).forEach(([k, v]) => {
            text = text.replace(`{${k}}`, v);
        });

        return text;
    }

    /**
     * 将翻译应用到 DOM
     * 扫描所有带 data-i18n 属性的元素并更新文本
     */
    apply() {
        // 翻译文本内容
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            el.textContent = this.t(key);
        });

        // 翻译 placeholder
        document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
            const key = el.getAttribute('data-i18n-placeholder');
            el.placeholder = this.t(key);
        });

        // 翻译 title 属性
        document.querySelectorAll('[data-i18n-title]').forEach(el => {
            const key = el.getAttribute('data-i18n-title');
            el.title = this.t(key);
        });
    }

    /**
     * 注册语言切换回调
     * @param {Function} callback
     */
    onChange(callback) {
        this._callbacks.push(callback);
    }

    /**
     * 切换语言
     * @param {string} locale
     */
    async switchTo(locale) {
        if (locale !== this.locale) {
            await this.load(locale);
        }
    }

    /**
     * 获取当前语言
     * @returns {string}
     */
    getLocale() {
        return this.locale;
    }
}

// 创建全局实例
window.i18n = new I18n();

// DOM 加载完成后自动应用翻译
document.addEventListener('DOMContentLoaded', async () => {
    await window.i18n.load(window.i18n.locale);
});
