/**
 * ChemMaster LaTeX 前端插件
 * 提供 LaTeX 相关的前端功能
 */

class LatexPlugin {
    constructor() {
        this.name = 'latex';
        this.description = 'LaTeX 导出插件';
        this.apiBaseUrl = '/api/export';
        this.history = [];
    }

    /**
     * 初始化插件
     */
    async init() {
        console.log('LaTeX Plugin initialized');
        this.loadHistory();
    }

    /**
     * 转换化学式为 LaTeX 格式
     */
    async convertFormula(formula, packageType = 'mhchem') {
        try {
            const response = await fetch(`${this.apiBaseUrl}/formula`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    formula: formula,
                    format: packageType
                })
            });

            if (!response.ok) {
                throw new Error('转换失败');
            }

            const result = await response.json();
            this.addToHistory(formula, result.latex);

            return result;
        } catch (error) {
            console.error('Convert formula error:', error);
            throw error;
        }
    }

    /**
     * 转换方程式为 LaTeX 格式
     */
    async convertEquation(equation, packageType = 'mhchem', balance = true) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/equation`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    equation: equation,
                    format: packageType,
                    balance: balance
                })
            });

            if (!response.ok) {
                throw new Error('转换失败');
            }

            const result = await response.json();
            this.addToHistory(equation, result.latex);

            return result;
        } catch (error) {
            console.error('Convert equation error:', error);
            throw error;
        }
    }

    /**
     * 批量处理方程式
     */
    async processBatch(equations, packageType = 'mhchem', balance = true) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/batch`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    equations: equations,
                    format: packageType,
                    balance: balance
                })
            });

            if (!response.ok) {
                throw new Error('批量处理失败');
            }

            const result = await response.json();

            // 添加到历史
            result.results.forEach(r => {
                this.addToHistory(r.original, r.latex);
            });

            return result;
        } catch (error) {
            console.error('Batch process error:', error);
            throw error;
        }
    }

    /**
     * 生成完整的 LaTeX 文档
     */
    async generateDocument(equations, title = '化学反应方程式') {
        try {
            const response = await fetch(`${this.apiBaseUrl}/latex/document`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    equations: equations,
                    format: 'mhchem',
                    balance: true
                })
            });

            if (!response.ok) {
                throw new Error('生成文档失败');
            }

            return await response.json();
        } catch (error) {
            console.error('Generate document error:', error);
            throw error;
        }
    }

    /**
     * 生成 LaTeX 片段
     */
    generateFragment(content, displayMode = true) {
        if (displayMode) {
            return `\\[${content}\\]`;
        } else {
            return `\\(${content}\\)`;
        }
    }

    /**
     * 生成 mhchem 命令
     */
    generateMhchemCommand(formula) {
        return `\\ce{${formula}}`;
    }

    /**
     * 生成数学模式
     */
    generateMathMode(content, displayMode = true) {
        if (displayMode) {
            return `\\[${content}\\]`;
        } else {
            return `$${content}$`;
        }
    }

    /**
     * 复制到剪贴板
     */
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (error) {
            console.error('Copy to clipboard failed:', error);
            // 降级方案
            const textarea = document.createElement('textarea');
            textarea.value = text;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            return true;
        }
    }

    /**
     * 下载为 .tex 文件
     */
    downloadAsTex(content, filename = 'chemistry.tex') {
        const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    /**
     * 渲染 LaTeX 预览（使用 KaTeX 或 MathJax）
     */
    renderPreview(element, latex) {
        // 检查是否使用 KaTeX
        if (typeof katex !== 'undefined') {
            try {
                katex.render(latex, element, {
                    throwOnError: false,
                    displayMode: true
                });
                return;
            } catch (e) {
                console.warn('KaTeX render failed:', e);
            }
        }

        // 检查是否使用 MathJax
        if (typeof MathJax !== 'undefined') {
            try {
                element.innerHTML = `\\[${latex}\\]`;
                MathJax.typesetPromise([element]).catch(err => {
                    console.warn('MathJax render failed:', err);
                });
                return;
            } catch (e) {
                console.warn('MathJax render failed:', e);
            }
        }

        // 降级：显示原始文本
        element.textContent = latex;
    }

    /**
     * 添加到历史记录
     */
    addToHistory(input, output) {
        const item = {
            input: input,
            output: output,
            time: new Date().toISOString()
        };

        this.history.unshift(item);

        // 只保留最近 50 条
        if (this.history.length > 50) {
            this.history = this.history.slice(0, 50);
        }

        this.saveHistory();
    }

    /**
     * 获取历史记录
     */
    getHistory() {
        return this.history;
    }

    /**
     * 清空历史记录
     */
    clearHistory() {
        this.history = [];
        this.saveHistory();
    }

    /**
     * 保存历史记录到本地存储
     */
    saveHistory() {
        try {
            localStorage.setItem('chemmaster_latex_history', JSON.stringify(this.history));
        } catch (error) {
            console.error('Save history failed:', error);
        }
    }

    /**
     * 从本地存储加载历史记录
     */
    loadHistory() {
        try {
            const saved = localStorage.getItem('chemmaster_latex_history');
            if (saved) {
                this.history = JSON.parse(saved);
            }
        } catch (error) {
            console.error('Load history failed:', error);
        }
    }
}

// 导出插件实例
const latexPlugin = new LatexPlugin();

// 自动初始化
document.addEventListener('DOMContentLoaded', () => {
    latexPlugin.init();
});

// 导出到全局
window.latexPlugin = latexPlugin;
