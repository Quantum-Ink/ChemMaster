/**
 * ChemMaster 主编辑器逻辑
 * 处理页面交互和功能调用
 */

// API 基础 URL
const API_BASE_URL = '/api';

// 当前选中的格式
let currentFormulaFormat = 'subscript';
let currentEquationFormat = 'subscript';

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initFormulaSection();
    initEquationSection();
    initIonSection();
    initBatchSection();
    initMoleculeCanvas();
    initMoleculeViewer();
});

/**
 * 初始化导航标签
 */
function initNavigation() {
    const tabs = document.querySelectorAll('.nav-tab');
    const contents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetId = tab.dataset.tab + '-tab';

            // 更新标签状态
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // 更新内容显示
            contents.forEach(c => c.classList.remove('active'));
            document.getElementById(targetId).classList.add('active');

            // 通知组件标签已显示（用于画布/3D查看器重新调整尺寸）
            window.dispatchEvent(new CustomEvent('tab-shown', { detail: { tabId: targetId } }));
        });
    });
}

/**
 * 初始化化学式转换部分
 */
function initFormulaSection() {
    const input = document.getElementById('formula-input');
    const convertBtn = document.getElementById('formula-convert-btn');
    const clearBtn = document.getElementById('formula-clear-btn');
    const copyBtn = document.getElementById('formula-copy-btn');
    const insertWordBtn = document.getElementById('formula-insert-word-btn');
    const exportLatexBtn = document.getElementById('formula-export-latex-btn');
    const preview = document.getElementById('formula-preview');
    const status = document.getElementById('formula-status');

    // 格式切换
    document.querySelectorAll('#formula-tab .format-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('#formula-tab .format-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFormulaFormat = btn.dataset.format;
            if (input.value.trim()) {
                convertFormula();
            }
        });
    });

    // 示例点击
    document.querySelectorAll('#formula-tab .chip').forEach(chip => {
        chip.addEventListener('click', () => {
            input.value = chip.dataset.formula;
            convertFormula();
        });
    });

    // 转换按钮
    convertBtn.addEventListener('click', convertFormula);

    // 输入框回车
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            convertFormula();
        }
    });

    // 清除按钮
    clearBtn.addEventListener('click', () => {
        input.value = '';
        preview.innerHTML = '<span style="color: #999;">输入化学式以预览</span>';
        hideStatus(status);
    });

    // 复制按钮
    copyBtn.addEventListener('click', () => {
        const text = preview.textContent;
        if (text && !text.includes('输入化学式')) {
            copyToClipboard(text);
            showStatus(status, '已复制到剪贴板！', 'success');
        }
    });

    // 插入 Word 按钮
    insertWordBtn.addEventListener('click', () => {
        const text = preview.textContent;
        if (text && !text.includes('输入化学式')) {
            copyToClipboard(text);
            showStatus(status, '已复制，请在 Word 中粘贴', 'success');
        }
    });

    // 导出 LaTeX 按钮
    exportLatexBtn.addEventListener('click', () => {
        if (input.value.trim()) {
            exportFormulaLatex(input.value.trim());
        }
    });

    // 实时预览
    let debounceTimer;
    input.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            if (input.value.trim()) {
                convertFormula();
            }
        }, 500);
    });
}

/**
 * 转换化学式
 */
async function convertFormula() {
    const input = document.getElementById('formula-input');
    const preview = document.getElementById('formula-preview');
    const status = document.getElementById('formula-status');
    const formula = input.value.trim();

    if (!formula) {
        showStatus(status, '请输入化学式', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/export/formula`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                formula: formula,
                format: currentFormulaFormat === 'latex' ? 'mhchem' : 'standard'
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '转换失败');
        }

        const result = await response.json();

        if (currentFormulaFormat === 'subscript') {
            preview.innerHTML = `<span class="formula-display">${result.unicode}</span>`;
        } else {
            preview.innerHTML = `<div class="latex-code">${result.latex}</div>`;
        }

        hideStatus(status);
    } catch (error) {
        showStatus(status, `错误: ${error.message}`, 'error');
        preview.innerHTML = '<span style="color: #999;">转换失败</span>';
    }
}

/**
 * 导出化学式 LaTeX
 */
async function exportFormulaLatex(formula) {
    try {
        const response = await fetch(`${API_BASE_URL}/export/latex/formula`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                formula: formula,
                format: 'mhchem'
            })
        });

        if (!response.ok) {
            throw new Error('导出失败');
        }

        const result = await response.json();
        downloadFile(result.latex, 'formula.tex', 'text/plain');
        showStatus(document.getElementById('formula-status'), '已导出 LaTeX 文件', 'success');
    } catch (error) {
        showStatus(document.getElementById('formula-status'), `导出失败: ${error.message}`, 'error');
    }
}

/**
 * 初始化反应方程式部分
 */
function initEquationSection() {
    const input = document.getElementById('equation-input');
    const convertBtn = document.getElementById('equation-convert-btn');
    const clearBtn = document.getElementById('equation-clear-btn');
    const copyBtn = document.getElementById('equation-copy-btn');
    const insertWordBtn = document.getElementById('equation-insert-word-btn');
    const exportLatexBtn = document.getElementById('equation-export-latex-btn');
    const preview = document.getElementById('equation-preview');
    const status = document.getElementById('equation-status');

    // 格式切换
    document.querySelectorAll('#equation-tab .format-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('#equation-tab .format-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentEquationFormat = btn.dataset.format;
            if (input.value.trim()) {
                convertEquation();
            }
        });
    });

    // 示例点击
    document.querySelectorAll('#equation-tab .chip').forEach(chip => {
        chip.addEventListener('click', () => {
            input.value = chip.dataset.equation;
            convertEquation();
        });
    });

    // 转换按钮
    convertBtn.addEventListener('click', convertEquation);

    // 输入框回车
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            convertEquation();
        }
    });

    // 清除按钮
    clearBtn.addEventListener('click', () => {
        input.value = '';
        preview.innerHTML = '<span style="color: #999;">输入方程式以预览</span>';
        hideStatus(status);
    });

    // 复制按钮
    copyBtn.addEventListener('click', () => {
        const text = preview.textContent;
        if (text && !text.includes('输入方程式')) {
            copyToClipboard(text);
            showStatus(status, '已复制到剪贴板！', 'success');
        }
    });

    // 插入 Word 按钮
    insertWordBtn.addEventListener('click', () => {
        const text = preview.textContent;
        if (text && !text.includes('输入方程式')) {
            copyToClipboard(text);
            showStatus(status, '已复制，请在 Word 中粘贴', 'success');
        }
    });

    // 导出 LaTeX 按钮
    exportLatexBtn.addEventListener('click', () => {
        if (input.value.trim()) {
            exportEquationLatex(input.value.trim());
        }
    });

    // 实时预览
    let debounceTimer;
    input.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            if (input.value.trim()) {
                convertEquation();
            }
        }, 500);
    });
}

/**
 * 转换反应方程式
 */
async function convertEquation() {
    const input = document.getElementById('equation-input');
    const preview = document.getElementById('equation-preview');
    const status = document.getElementById('equation-status');
    const balance = document.getElementById('balance-check').checked;
    const equation = input.value.trim();

    if (!equation) {
        showStatus(status, '请输入反应方程式', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/export/equation`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                equation: equation,
                format: currentEquationFormat === 'latex' ? 'mhchem' : 'standard',
                balance: balance
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '转换失败');
        }

        const result = await response.json();

        if (currentEquationFormat === 'subscript') {
            preview.innerHTML = `<span class="formula-display">${result.unicode}</span>`;
        } else {
            preview.innerHTML = `<div class="latex-code">${result.latex}</div>`;
        }

        if (!result.is_balanced && balance) {
            showStatus(status, '方程式已自动平衡', 'success');
        } else {
            hideStatus(status);
        }
    } catch (error) {
        showStatus(status, `错误: ${error.message}`, 'error');
        preview.innerHTML = '<span style="color: #999;">转换失败</span>';
    }
}

/**
 * 导出方程式 LaTeX
 */
async function exportEquationLatex(equation) {
    const balance = document.getElementById('balance-check').checked;

    try {
        const response = await fetch(`${API_BASE_URL}/export/latex/equation`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                equation: equation,
                format: 'mhchem',
                balance: balance
            })
        });

        if (!response.ok) {
            throw new Error('导出失败');
        }

        const result = await response.json();
        downloadFile(result.latex, 'equation.tex', 'text/plain');
        showStatus(document.getElementById('equation-status'), '已导出 LaTeX 文件', 'success');
    } catch (error) {
        showStatus(document.getElementById('equation-status'), `导出失败: ${error.message}`, 'error');
    }
}

/**
 * 初始化离子方程式部分
 */
function initIonSection() {
    const input = document.getElementById('ion-input');
    const analyzeBtn = document.getElementById('ion-analyze-btn');
    const balanceBtn = document.getElementById('ion-balance-btn');
    const clearBtn = document.getElementById('ion-clear-btn');
    const status = document.getElementById('ion-status');

    // 示例点击
    document.querySelectorAll('#ion-tab .chip').forEach(chip => {
        chip.addEventListener('click', () => {
            input.value = chip.dataset.ion;
            analyzeIon();
        });
    });

    // 分析按钮
    analyzeBtn.addEventListener('click', analyzeIon);

    // 配平按钮
    balanceBtn.addEventListener('click', balanceIon);

    // 输入框回车
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            analyzeIon();
        }
    });

    // 清除按钮
    clearBtn.addEventListener('click', () => {
        input.value = '';
        document.getElementById('ion-result').style.display = 'none';
        hideStatus(status);
    });
}

/**
 * 分析离子方程式
 */
async function analyzeIon() {
    const input = document.getElementById('ion-input');
    const status = document.getElementById('ion-status');
    const resultDiv = document.getElementById('ion-result');
    const equation = input.value.trim();

    if (!equation) {
        showStatus(status, '请输入方程式', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/ion/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ equation: equation })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '分析失败');
        }

        const result = await response.json();

        // 隐藏所有结果
        document.querySelectorAll('.ion-result-item').forEach(el => el.style.display = 'none');

        resultDiv.style.display = 'block';

        if (result.type === 'molecular') {
            // 分子方程式转换结果
            document.getElementById('ion-molecular-result').style.display = 'block';
            document.getElementById('ion-balanced-molecular').textContent = result.balanced_molecular;

            document.getElementById('ion-full-ionic-result').style.display = 'block';
            document.getElementById('ion-full-ionic').textContent = result.full_ionic;

            document.getElementById('ion-net-ionic-result').style.display = 'block';
            document.getElementById('ion-net-ionic').textContent = result.net_ionic;

            if (result.spectator_ions && result.spectator_ions.length > 0) {
                document.getElementById('ion-spectator-result').style.display = 'block';
                const ionsDiv = document.getElementById('ion-spectator-ions');
                ionsDiv.innerHTML = result.spectator_ions.map(ion =>
                    `<span class="spectator-ion">${ion}</span>`
                ).join('');
            }

            showStatus(status, '分析完成', 'success');
        } else if (result.type === 'ionic') {
            // 离子方程式配平结果
            document.getElementById('ion-balance-result').style.display = 'block';
            document.getElementById('ion-balanced-equation').textContent = result.balanced;

            document.getElementById('ion-charge-result').style.display = 'block';
            const chargeInfo = result.charge_balanced
                ? `✅ 电荷守恒：反应物总电荷 ${result.reactant_charges} = 生成物总电荷 ${result.product_charges}`
                : `❌ 电荷不守恒：反应物总电荷 ${result.reactant_charges} ≠ 生成物总电荷 ${result.product_charges}`;
            document.getElementById('ion-charge-info').textContent = chargeInfo;

            showStatus(status, '配平完成', 'success');
        }
    } catch (error) {
        showStatus(status, `错误: ${error.message}`, 'error');
    }
}

/**
 * 配平离子方程式
 */
async function balanceIon() {
    const input = document.getElementById('ion-input');
    const status = document.getElementById('ion-status');
    const resultDiv = document.getElementById('ion-result');
    const equation = input.value.trim();

    if (!equation) {
        showStatus(status, '请输入离子方程式', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/ion/balance`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ equation: equation })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '配平失败');
        }

        const result = await response.json();

        // 隐藏所有结果
        document.querySelectorAll('.ion-result-item').forEach(el => el.style.display = 'none');

        resultDiv.style.display = 'block';

        // 显示配平结果
        document.getElementById('ion-balance-result').style.display = 'block';
        document.getElementById('ion-balanced-equation').textContent = result.balanced;

        // 显示电荷信息
        document.getElementById('ion-charge-result').style.display = 'block';
        const chargeInfo = result.charge_balanced
            ? `✅ 电荷守恒：反应物总电荷 ${result.reactant_charges} = 生成物总电荷 ${result.product_charges}`
            : `❌ 电荷不守恒：反应物总电荷 ${result.reactant_charges} ≠ 生成物总电荷 ${result.product_charges}`;
        document.getElementById('ion-charge-info').textContent = chargeInfo;

        showStatus(status, '配平完成', 'success');
    } catch (error) {
        showStatus(status, `错误: ${error.message}`, 'error');
    }
}

/**
 * 初始化批量处理部分
 */
function initBatchSection() {
    const input = document.getElementById('batch-input');
    const processBtn = document.getElementById('batch-process-btn');
    const copyBtn = document.getElementById('batch-copy-btn');
    const exportBtn = document.getElementById('batch-export-btn');
    const preview = document.getElementById('batch-preview');

    // 批量处理按钮
    processBtn.addEventListener('click', async () => {
        const content = input.value.trim();
        if (!content) {
            preview.innerHTML = '<span style="color: #999;">请输入内容</span>';
            return;
        }

        const lines = content.split('\n').filter(line => line.trim());
        const balance = document.getElementById('batch-balance-check').checked;

        preview.innerHTML = '<div class="loading">处理中...</div>';

        try {
            const results = [];
            for (const line of lines) {
                const trimmed = line.trim();
                if (!trimmed) continue;

                // 判断是化学式还是方程式
                if (trimmed.includes('->') || trimmed.includes('→')) {
                    // 方程式
                    const response = await fetch(`${API_BASE_URL}/export/equation`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            equation: trimmed,
                            format: 'standard',
                            balance: balance
                        })
                    });

                    if (response.ok) {
                        const result = await response.json();
                        results.push({
                            original: trimmed,
                            converted: result.unicode,
                            type: 'equation'
                        });
                    }
                } else {
                    // 化学式
                    const response = await fetch(`${API_BASE_URL}/export/formula`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            formula: trimmed,
                            format: 'standard'
                        })
                    });

                    if (response.ok) {
                        const result = await response.json();
                        results.push({
                            original: trimmed,
                            converted: result.unicode,
                            type: 'formula'
                        });
                    }
                }
            }

            // 显示结果
            preview.innerHTML = results.map((r, i) =>
                `${i + 1}. ${r.converted}`
            ).join('\n');

        } catch (error) {
            preview.innerHTML = `<span style="color: #721c24;">处理失败: ${error.message}</span>`;
        }
    });

    // 复制按钮
    copyBtn.addEventListener('click', () => {
        const text = preview.textContent;
        if (text && !text.includes('请输入内容') && !text.includes('处理中')) {
            copyToClipboard(text);
            alert('已复制到剪贴板！');
        }
    });

    // 导出按钮
    exportBtn.addEventListener('click', () => {
        const text = preview.textContent;
        if (text && !text.includes('请输入内容') && !text.includes('处理中')) {
            downloadFile(text, 'batch_results.txt', 'text/plain');
        }
    });
}

/**
 * 初始化 Canvas 分子结构编辑器
 */
function initMoleculeCanvas() {
    const container = document.getElementById('molecule-canvas-container');
    if (!container) return;

    // MoleculeCanvas 内部监听 tab-shown 事件延迟初始化
    window.moleculeCanvas = new MoleculeCanvas('molecule-canvas-container');
}

/**
 * 初始化 3D 分子可视化器
 */
function initMoleculeViewer() {
    const container = document.getElementById('molecule-viewer-container');
    if (!container) return;

    // MoleculeViewer 内部监听 tab-shown 事件延迟初始化
    window.moleculeViewer = new MoleculeViewer('molecule-viewer-container', {
        apiBaseUrl: '/api/structure'
    });
}

/**
 * 复制到剪贴板
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
    } catch (error) {
        // 降级方案
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
    }
}

/**
 * 下载文件
 */
function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
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
 * 显示状态消息
 */
function showStatus(element, message, type) {
    element.textContent = message;
    element.className = `status-message ${type}`;
}

/**
 * 隐藏状态消息
 */
function hideStatus(element) {
    element.className = 'status-message';
    element.textContent = '';
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
