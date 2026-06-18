/**
 * ChemMaster Word Add-in 主逻辑
 * 处理化学式转换和插入
 */

// 全局状态
const state = {
    currentFormat: 'subscript',
    history: [],
    apiBaseUrl: 'http://localhost:8000/api/export'
};

// Office 初始化
Office.onReady((info) => {
    console.log('Office.js initialized');

    // 初始化 UI
    initTabs();
    initFormatOptions();
    loadHistory();

    // 绑定输入事件
    document.getElementById('formula-input').addEventListener('input', debounce(previewFormula, 300));
    document.getElementById('equation-input').addEventListener('input', debounce(previewEquation, 300));
});

/**
 * 初始化标签页切换
 */
function initTabs() {
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // 移除所有 active
            tabs.forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            // 添加 active
            tab.classList.add('active');
            const tabId = tab.getAttribute('data-tab');
            document.getElementById(`${tabId}-tab`).classList.add('active');
        });
    });
}

/**
 * 初始化格式选项
 */
function initFormatOptions() {
    document.querySelectorAll('.format-option').forEach(option => {
        option.addEventListener('click', () => {
            const parent = option.closest('.format-options');
            parent.querySelectorAll('.format-option').forEach(o => o.classList.remove('selected'));
            option.classList.add('selected');
            state.currentFormat = option.getAttribute('data-format');
        });
    });
}

/**
 * 防抖函数
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * 显示状态消息
 */
function showStatus(elementId, message, type = 'success') {
    const status = document.getElementById(elementId);
    status.textContent = message;
    status.className = `status ${type}`;
    status.style.display = 'block';

    // 3秒后自动隐藏
    setTimeout(() => {
        status.style.display = 'none';
    }, 3000);
}

/**
 * 显示/隐藏加载状态
 */
function setLoading(elementId, loading) {
    const element = document.getElementById(elementId);
    if (loading) {
        element.classList.add('active');
    } else {
        element.classList.remove('active');
    }
}

/**
 * 调用后端 API
 */
async function callApi(endpoint, data) {
    try {
        const response = await fetch(`${state.apiBaseUrl}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '请求失败');
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

/**
 * 预览化学式
 */
async function previewFormula() {
    const input = document.getElementById('formula-input').value.trim();
    const preview = document.getElementById('formula-preview');

    if (!input) {
        preview.textContent = '-';
        return;
    }

    try {
        const result = await callApi('/formula', {
            formula: input,
            format: state.currentFormat === 'latex' ? 'mhchem' : 'standard'
        });

        preview.textContent = result.unicode || result.latex || input;
    } catch (error) {
        preview.textContent = input;
    }
}

/**
 * 预览方程式
 */
async function previewEquation() {
    const input = document.getElementById('equation-input').value.trim();
    const preview = document.getElementById('equation-preview');
    const balance = document.getElementById('balance-check').checked;

    if (!input) {
        preview.textContent = '-';
        return;
    }

    try {
        const result = await callApi('/equation', {
            equation: input,
            format: state.currentFormat === 'latex' ? 'mhchem' : 'standard',
            balance: balance
        });

        preview.textContent = result.unicode || result.latex || input;
    } catch (error) {
        preview.textContent = input;
    }
}

/**
 * 转换化学式
 */
async function convertFormula() {
    const input = document.getElementById('formula-input').value.trim();

    if (!input) {
        showStatus('formula-status', '请输入化学式', 'error');
        return;
    }

    setLoading('formula-loading', true);

    try {
        const result = await callApi('/formula', {
            formula: input,
            format: state.currentFormat === 'latex' ? 'mhchem' : 'standard'
        });

        // 更新预览
        document.getElementById('formula-preview').textContent = result.unicode || result.latex;

        // 添加到历史
        addToHistory(input, result.unicode);

        showStatus('formula-status', '转换成功！');
    } catch (error) {
        showStatus('formula-status', `错误: ${error.message}`, 'error');
    } finally {
        setLoading('formula-loading', false);
    }
}

/**
 * 转换方程式
 */
async function convertEquation() {
    const input = document.getElementById('equation-input').value.trim();
    const balance = document.getElementById('balance-check').checked;

    if (!input) {
        showStatus('equation-status', '请输入反应方程式', 'error');
        return;
    }

    setLoading('equation-loading', true);

    try {
        const result = await callApi('/equation', {
            equation: input,
            format: state.currentFormat === 'latex' ? 'mhchem' : 'standard',
            balance: balance
        });

        // 更新预览
        document.getElementById('equation-preview').textContent = result.unicode || result.latex;

        // 添加到历史
        addToHistory(input, result.unicode);

        showStatus('equation-status', '转换成功！');
    } catch (error) {
        showStatus('equation-status', `错误: ${error.message}`, 'error');
    } finally {
        setLoading('equation-loading', false);
    }
}

/**
 * 插入化学式到 Word 文档
 */
async function insertFormula() {
    const preview = document.getElementById('formula-preview').textContent;

    if (!preview || preview === '-') {
        showStatus('formula-status', '请先转换化学式', 'error');
        return;
    }

    try {
        await Word.run(async (context) => {
            const body = context.document.body;
            body.insertParagraph(preview, Word.InsertLocation.end);
            await context.sync();
        });

        showStatus('formula-status', '已插入到文档！');
    } catch (error) {
        showStatus('formula-status', `插入失败: ${error.message}`, 'error');
    }
}

/**
 * 插入方程式到 Word 文档
 */
async function insertEquation() {
    const preview = document.getElementById('equation-preview').textContent;

    if (!preview || preview === '-') {
        showStatus('equation-status', '请先转换方程式', 'error');
        return;
    }

    try {
        await Word.run(async (context) => {
            const body = context.document.body;
            body.insertParagraph(preview, Word.InsertLocation.end);
            await context.sync();
        });

        showStatus('equation-status', '已插入到文档！');
    } catch (error) {
        showStatus('equation-status', `插入失败: ${error.message}`, 'error');
    }
}

/**
 * 批量处理
 */
async function processBatch() {
    const input = document.getElementById('batch-input').value.trim();
    const balance = document.getElementById('batch-balance-check').checked;

    if (!input) {
        showStatus('batch-status', '请输入方程式', 'error');
        return;
    }

    setLoading('batch-loading', true);

    try {
        const equations = input.split('\n').filter(line => line.trim());

        const result = await callApi('/batch', {
            equations: equations,
            format: state.currentFormat === 'latex' ? 'mhchem' : 'standard',
            balance: balance
        });

        // 显示结果
        const preview = document.getElementById('batch-preview');
        const lines = result.results.map((r, i) => `${i + 1}. ${r.unicode || r.latex}`);
        preview.innerHTML = lines.join('<br>');

        // 添加到历史
        result.results.forEach(r => {
            addToHistory(r.original, r.unicode);
        });

        showStatus('batch-status', `成功处理 ${result.count} 个方程式！`);
    } catch (error) {
        showStatus('batch-status', `错误: ${error.message}`, 'error');
    } finally {
        setLoading('batch-loading', false);
    }
}

/**
 * 批量插入
 */
async function insertBatch() {
    const preview = document.getElementById('batch-preview');

    if (!preview || preview.textContent === '-') {
        showStatus('batch-status', '请先批量处理方程式', 'error');
        return;
    }

    try {
        const lines = preview.innerHTML.split('<br>');

        await Word.run(async (context) => {
            const body = context.document.body;

            lines.forEach(line => {
                body.insertParagraph(line, Word.InsertLocation.end);
            });

            await context.sync();
        });

        showStatus('batch-status', '已全部插入到文档！');
    } catch (error) {
        showStatus('batch-status', `插入失败: ${error.message}`, 'error');
    }
}

/**
 * 添加到历史记录
 */
function addToHistory(input, output) {
    const historyItem = {
        input: input,
        output: output,
        time: new Date().toLocaleTimeString()
    };

    state.history.unshift(historyItem);

    // 只保留最近 10 条
    if (state.history.length > 10) {
        state.history = state.history.slice(0, 10);
    }

    // 保存到本地存储
    localStorage.setItem('chemmaster_history', JSON.stringify(state.history));

    // 更新显示
    renderHistory();
}

/**
 * 加载历史记录
 */
function loadHistory() {
    try {
        const saved = localStorage.getItem('chemmaster_history');
        if (saved) {
            state.history = JSON.parse(saved);
            renderHistory();
        }
    } catch (error) {
        console.error('Failed to load history:', error);
    }
}

/**
 * 渲染历史记录
 */
function renderHistory() {
    const historyList = document.getElementById('history-list');

    if (state.history.length === 0) {
        historyList.innerHTML = '<div class="history-item" style="color: #666; text-align: center;">暂无历史记录</div>';
        return;
    }

    historyList.innerHTML = state.history.map((item, index) => `
        <div class="history-item" onclick="useHistory(${index})">
            <div class="formula">${item.output}</div>
            <div class="time">${item.time} - ${item.input}</div>
        </div>
    `).join('');
}

/**
 * 使用历史记录
 */
function useHistory(index) {
    const item = state.history[index];
    if (!item) return;

    // 判断是化学式还是方程式
    if (item.input.includes('->') || item.input.includes('→') || item.input.includes('+')) {
        document.getElementById('equation-input').value = item.input;
        document.getElementById('equation-preview').textContent = item.output;
        // 切换到方程式标签
        document.querySelectorAll('.tab')[1].click();
    } else {
        document.getElementById('formula-input').value = item.input;
        document.getElementById('formula-preview').textContent = item.output;
        // 切换到化学式标签
        document.querySelectorAll('.tab')[0].click();
    }
}

/**
 * 清空历史记录
 */
function clearHistory() {
    state.history = [];
    localStorage.removeItem('chemmaster_history');
    renderHistory();
}
