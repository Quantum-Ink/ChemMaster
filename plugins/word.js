/**
 * ChemMaster Word 前端插件
 * 提供 Word 相关的前端功能
 */

class WordPlugin {
    constructor() {
        this.name = 'word';
        this.description = 'Word 文档导出插件';
        this.apiBaseUrl = '/api/export';
        this.history = [];
    }

    /**
     * 初始化插件
     */
    async init() {
        console.log('Word Plugin initialized');
        this.loadHistory();
    }

    /**
     * 转换化学式为 Word 格式
     */
    async convertFormula(formula) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/formula`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    formula: formula,
                    format: 'standard'
                })
            });

            if (!response.ok) {
                throw new Error('转换失败');
            }

            const result = await response.json();
            this.addToHistory(formula, result.unicode);

            return result;
        } catch (error) {
            console.error('Convert formula error:', error);
            throw error;
        }
    }

    /**
     * 转换方程式为 Word 格式
     */
    async convertEquation(equation, balance = true) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/equation`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    equation: equation,
                    format: 'standard',
                    balance: balance
                })
            });

            if (!response.ok) {
                throw new Error('转换失败');
            }

            const result = await response.json();
            this.addToHistory(equation, result.unicode);

            return result;
        } catch (error) {
            console.error('Convert equation error:', error);
            throw error;
        }
    }

    /**
     * 批量处理方程式
     */
    async processBatch(equations, balance = true) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/batch`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    equations: equations,
                    format: 'standard',
                    balance: balance
                })
            });

            if (!response.ok) {
                throw new Error('批量处理失败');
            }

            const result = await response.json();

            // 添加到历史
            result.results.forEach(r => {
                this.addToHistory(r.original, r.unicode);
            });

            return result;
        } catch (error) {
            console.error('Batch process error:', error);
            throw error;
        }
    }

    /**
     * 生成可复制的文本
     */
    generateCopyText(content) {
        return content;
    }

    /**
     * 生成 HTML 格式
     */
    generateHTML(content) {
        return `<span style="font-family: 'Times New Roman', serif;">${content}</span>`;
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
     * 下载为文本文件
     */
    downloadAsText(content, filename = 'chemistry.txt') {
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
     * 下载为 HTML 文件
     */
    downloadAsHTML(content, filename = 'chemistry.html') {
        const html = `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>化学式</title>
    <style>
        body { font-family: 'Times New Roman', serif; padding: 20px; }
        .formula { font-size: 18px; margin: 10px 0; }
    </style>
</head>
<body>
    ${content}
</body>
</html>`;

        const blob = new Blob([html], { type: 'text/html;charset=utf-8' });
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
            localStorage.setItem('chemmaster_word_history', JSON.stringify(this.history));
        } catch (error) {
            console.error('Save history failed:', error);
        }
    }

    /**
     * 从本地存储加载历史记录
     */
    loadHistory() {
        try {
            const saved = localStorage.getItem('chemmaster_word_history');
            if (saved) {
                this.history = JSON.parse(saved);
            }
        } catch (error) {
            console.error('Load history failed:', error);
        }
    }
}

// 导出插件实例
const wordPlugin = new WordPlugin();

// 自动初始化
document.addEventListener('DOMContentLoaded', () => {
    wordPlugin.init();
});

// 导出到全局
window.wordPlugin = wordPlugin;
