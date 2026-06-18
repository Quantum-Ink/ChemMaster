/**
 * ChemMaster 前端插件管理系统
 * 支持插件注册、分类查询、动态加载
 */

class PluginManager {
    constructor() {
        /** @type {Object<string, object>} 已注册插件 */
        this.plugins = {};
        /** @type {Object<string, string[]>} 按分类索引 */
        this.categories = {};
        this.loaded = false;
        this.apiBaseUrl = '/plugins';
    }

    // ====== 插件注册 ======

    /**
     * 注册一个前端插件
     * @param {object} plugin - 插件对象，必须包含 name 属性
     * @returns {PluginManager}
     */
    register(plugin) {
        if (!plugin.name) {
            throw new Error('Plugin must have a name');
        }

        this.plugins[plugin.name] = plugin;
        console.log(`[PluginManager] Registered: ${plugin.name}`);

        // 按分类索引
        const cat = plugin.category || 'other';
        if (!this.categories[cat]) {
            this.categories[cat] = [];
        }
        if (!this.categories[cat].includes(plugin.name)) {
            this.categories[cat].push(plugin.name);
        }

        return this;
    }

    /**
     * 注销一个插件
     * @param {string} name - 插件名称
     */
    unregister(name) {
        const plugin = this.plugins[name];
        if (!plugin) return;

        // 调用清理函数
        if (typeof plugin.destroy === 'function') {
            plugin.destroy();
        }

        // 从分类中移除
        const cat = plugin.category || 'other';
        if (this.categories[cat]) {
            this.categories[cat] = this.categories[cat].filter(n => n !== name);
        }

        delete this.plugins[name];
        console.log(`[PluginManager] Unregistered: ${name}`);
    }

    // ====== 插件查询 ======

    /**
     * 获取指定插件
     * @param {string} name
     * @returns {object|undefined}
     */
    getPlugin(name) {
        return this.plugins[name];
    }

    /**
     * 获取所有插件
     * @returns {object[]}
     */
    getAllPlugins() {
        return Object.values(this.plugins);
    }

    /**
     * 按分类获取插件列表
     * @param {string} category
     * @returns {object[]}
     */
    getPluginsByCategory(category) {
        const names = this.categories[category] || [];
        return names.map(n => this.plugins[n]).filter(Boolean);
    }

    /**
     * 获取所有分类
     * @returns {string[]}
     */
    getCategories() {
        return Object.keys(this.categories);
    }

    /**
     * 检查插件是否已注册
     * @param {string} name
     * @returns {boolean}
     */
    hasPlugin(name) {
        return name in this.plugins;
    }

    // ====== 生命周期 ======

    /**
     * 初始化所有已注册的插件
     */
    async initAll() {
        const initPromises = Object.values(this.plugins).map(async (plugin) => {
            try {
                if (typeof plugin.init === 'function') {
                    await plugin.init();
                    console.log(`[PluginManager] Initialized: ${plugin.name}`);
                }
            } catch (error) {
                console.error(`[PluginManager] Failed to init ${plugin.name}:`, error);
            }
        });

        await Promise.all(initPromises);
        this.loaded = true;
        console.log('[PluginManager] All plugins initialized');
    }

    /**
     * 获取所有插件状态
     * @returns {object}
     */
    getStatus() {
        const status = {};
        Object.entries(this.plugins).forEach(([name, plugin]) => {
            status[name] = {
                name: plugin.name,
                description: plugin.description || '',
                category: plugin.category || 'other',
                version: plugin.version || '0.0.0',
                loaded: true,
            };
        });
        return status;
    }

    // ====== 后端插件同步 ======

    /**
     * 从后端 /plugins 端点获取已加载的插件信息
     * @returns {object|null}
     */
    async fetchBackendPlugins() {
        try {
            const response = await fetch(this.apiBaseUrl);
            if (!response.ok) return null;
            return await response.json();
        } catch (error) {
            console.error('[PluginManager] Failed to fetch backend plugins:', error);
            return null;
        }
    }

    /**
     * 从后端动态加载插件的前端脚本
     * @param {string} name - 插件名称
     * @param {string} url - 脚本 URL
     * @returns {boolean}
     */
    async loadPluginScript(name, url) {
        if (this.hasPlugin(name)) {
            console.warn(`[PluginManager] Plugin '${name}' already loaded`);
            return true;
        }

        return new Promise((resolve) => {
            const script = document.createElement('script');
            script.src = url;
            script.onload = () => {
                console.log(`[PluginManager] Script loaded: ${name}`);
                resolve(true);
            };
            script.onerror = () => {
                console.error(`[PluginManager] Failed to load script: ${name}`);
                resolve(false);
            };
            document.head.appendChild(script);
        });
    }
}

// 创建全局插件管理器实例
const pluginManager = new PluginManager();

// 导出到全局
window.pluginManager = pluginManager;
window.PluginManager = PluginManager;

// DOM 加载完成后自动注册已加载的插件
document.addEventListener('DOMContentLoaded', async () => {
    // 注册 Word 插件（如果已通过 script 标签加载）
    if (typeof wordPlugin !== 'undefined') {
        pluginManager.register(wordPlugin);
    }

    // 注册 LaTeX 插件
    if (typeof latexPlugin !== 'undefined') {
        pluginManager.register(latexPlugin);
    }

    // 初始化所有插件
    await pluginManager.initAll();

    // 尝试从后端同步插件信息
    const backendInfo = await pluginManager.fetchBackendPlugins();
    if (backendInfo) {
        console.log(`[PluginManager] Backend has ${backendInfo.total} plugins`);
    }
});
