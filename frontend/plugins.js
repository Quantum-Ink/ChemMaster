/**
 * ChemMaster 插件管理系统
 * 负责注册、加载和管理所有插件
 */

class PluginManager {
    constructor() {
        this.plugins = {};
        this.loaded = false;
    }

    /**
     * 注册插件
     */
    register(plugin) {
        if (!plugin.name) {
            throw new Error('Plugin must have a name');
        }

        this.plugins[plugin.name] = plugin;
        console.log(`Plugin registered: ${plugin.name}`);

        return this;
    }

    /**
     * 获取插件
     */
    getPlugin(name) {
        return this.plugins[name];
    }

    /**
     * 获取所有插件
     */
    getAllPlugins() {
        return Object.values(this.plugins);
    }

    /**
     * 初始化所有插件
     */
    async initAll() {
        const initPromises = Object.values(this.plugins).map(async (plugin) => {
            try {
                if (typeof plugin.init === 'function') {
                    await plugin.init();
                    console.log(`Plugin initialized: ${plugin.name}`);
                }
            } catch (error) {
                console.error(`Failed to initialize plugin ${plugin.name}:`, error);
            }
        });

        await Promise.all(initPromises);
        this.loaded = true;
        console.log('All plugins initialized');
    }

    /**
     * 检查插件是否已注册
     */
    hasPlugin(name) {
        return name in this.plugins;
    }

    /**
     * 移除插件
     */
    unregister(name) {
        if (this.plugins[name]) {
            // 调用清理函数
            if (typeof this.plugins[name].destroy === 'function') {
                this.plugins[name].destroy();
            }
            delete this.plugins[name];
            console.log(`Plugin unregistered: ${name}`);
        }
    }

    /**
     * 获取插件状态
     */
    getStatus() {
        const status = {};
        Object.entries(this.plugins).forEach(([name, plugin]) => {
            status[name] = {
                name: plugin.name,
                description: plugin.description || '',
                loaded: true
            };
        });
        return status;
    }
}

// 创建全局插件管理器实例
const pluginManager = new PluginManager();

// 导出到全局
window.pluginManager = pluginManager;

// 自动注册插件（如果已加载）
document.addEventListener('DOMContentLoaded', async () => {
    // 注册 Word 插件
    if (typeof wordPlugin !== 'undefined') {
        pluginManager.register(wordPlugin);
    }

    // 注册 LaTeX 插件
    if (typeof latexPlugin !== 'undefined') {
        pluginManager.register(latexPlugin);
    }

    // 初始化所有插件
    await pluginManager.initAll();
});
