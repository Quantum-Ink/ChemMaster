/**
 * ChemMaster 结构编辑器模块
 * 支持 SMILES 输入和可视化编辑
 */

class StructureEditor {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.options = {
            width: options.width || 800,
            height: options.height || 600,
            apiBaseUrl: options.apiBaseUrl || '/api/structure',
            onStructureChange: options.onStructureChange || null,
            showCommonStructures: options.showCommonStructures !== false,
            showPreview: options.showPreview !== false,
            ...options
        };

        this.currentSmiles = '';
        this.currentFormat = 'svg';
        this.ketcher = null;
        this.isKetcherLoaded = false;

        this.init();
    }

    /**
     * 初始化编辑器
     */
    async init() {
        this.createUI();
        this.bindEvents();

        // 尝试加载 Ketcher
        await this.loadKetcher();

        // 加载常见结构
        if (this.options.showCommonStructures) {
            await this.loadCommonStructures();
        }
    }

    /**
     * 创建 UI
     */
    createUI() {
        this.container.innerHTML = `
            <div class="structure-editor">
                <div class="editor-header">
                    <h2>🧪 化学结构编辑器</h2>
                    <div class="editor-tabs">
                        <button class="tab-btn active" data-tab="smiles">SMILES 输入</button>
                        <button class="tab-btn" data-tab="visual">可视化编辑</button>
                        <button class="tab-btn" data-tab="common">常见结构</button>
                    </div>
                </div>

                <div class="editor-content">
                    <!-- SMILES 输入面板 -->
                    <div class="tab-panel active" id="smiles-panel">
                        <div class="smiles-input-group">
                            <label for="smiles-input">输入 SMILES 字符串：</label>
                            <div class="input-wrapper">
                                <input type="text" id="smiles-input" placeholder="例如: CC(=O)O (乙酸), c1ccccc1 (苯)">
                                <button id="validate-btn" class="btn btn-secondary">验证</button>
                                <button id="clear-btn" class="btn btn-outline">清除</button>
                            </div>
                            <div id="smiles-status" class="status-message"></div>
                        </div>

                        <div class="smiles-examples">
                            <h4>示例：</h4>
                            <div class="example-chips">
                                <span class="chip" data-smiles="CC(=O)O">乙酸</span>
                                <span class="chip" data-smiles="c1ccccc1">苯</span>
                                <span class="chip" data-smiles="CCO">乙醇</span>
                                <span class="chip" data-smiles="CC(=O)OCC">乙酸乙酯</span>
                                <span class="chip" data-smiles="c1ccc(O)cc1">苯酚</span>
                                <span class="chip" data-smiles="CC(N)C(=O)O">丙氨酸</span>
                            </div>
                        </div>
                    </div>

                    <!-- 可视化编辑面板 -->
                    <div class="tab-panel" id="visual-panel">
                        <div id="ketcher-container" class="ketcher-container">
                            <div class="loading-message">
                                <div class="spinner"></div>
                                <p>正在加载可视化编辑器...</p>
                            </div>
                        </div>
                        <div class="visual-controls">
                            <button id="get-smiles-btn" class="btn btn-primary">获取 SMILES</button>
                            <button id="clear-canvas-btn" class="btn btn-outline">清空画布</button>
                        </div>
                    </div>

                    <!-- 常见结构面板 -->
                    <div class="tab-panel" id="common-panel">
                        <div class="common-structures">
                            <h4>常见有机物结构</h4>
                            <div class="structure-grid" id="structure-grid">
                                <div class="loading-message">加载中...</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 预览区域 -->
                <div class="preview-section" id="preview-section">
                    <div class="preview-header">
                        <h3>结构预览</h3>
                        <div class="format-selector">
                            <button class="format-btn active" data-format="svg">SVG</button>
                            <button class="format-btn" data-format="png">PNG</button>
                            <button class="format-btn" data-format="latex">LaTeX</button>
                        </div>
                    </div>
                    <div class="preview-content">
                        <div id="structure-preview" class="structure-preview">
                            <div class="placeholder">输入 SMILES 或绘制结构以预览</div>
                        </div>
                    </div>
                    <div class="preview-info" id="preview-info"></div>
                </div>

                <!-- 导出按钮 -->
                <div class="export-section">
                    <button id="export-svg-btn" class="btn btn-primary">导出 SVG</button>
                    <button id="export-png-btn" class="btn btn-primary">导出 PNG</button>
                    <button id="export-latex-btn" class="btn btn-primary">导出 LaTeX</button>
                    <button id="export-word-btn" class="btn btn-success">插入 Word</button>
                    <button id="copy-smiles-btn" class="btn btn-secondary">复制 SMILES</button>
                </div>
            </div>
        `;

        // 添加样式
        this.addStyles();
    }

    /**
     * 添加样式
     */
    addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .structure-editor {
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                background: white;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                overflow: hidden;
            }

            .editor-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
            }

            .editor-header h2 {
                margin: 0 0 15px 0;
                font-size: 1.5rem;
            }

            .editor-tabs {
                display: flex;
                gap: 10px;
            }

            .tab-btn {
                padding: 8px 16px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                background: transparent;
                color: white;
                border-radius: 6px;
                cursor: pointer;
                transition: all 0.3s;
            }

            .tab-btn:hover {
                background: rgba(255, 255, 255, 0.1);
            }

            .tab-btn.active {
                background: white;
                color: #667eea;
                border-color: white;
            }

            .editor-content {
                padding: 20px;
            }

            .tab-panel {
                display: none;
            }

            .tab-panel.active {
                display: block;
            }

            .smiles-input-group {
                margin-bottom: 20px;
            }

            .smiles-input-group label {
                display: block;
                margin-bottom: 8px;
                font-weight: 500;
                color: #333;
            }

            .input-wrapper {
                display: flex;
                gap: 10px;
            }

            .input-wrapper input {
                flex: 1;
                padding: 12px 16px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 16px;
                font-family: 'Consolas', 'Monaco', monospace;
                transition: border-color 0.3s;
            }

            .input-wrapper input:focus {
                outline: none;
                border-color: #667eea;
            }

            .status-message {
                margin-top: 8px;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 14px;
            }

            .status-message.success {
                background: #d4edda;
                color: #155724;
            }

            .status-message.error {
                background: #f8d7da;
                color: #721c24;
            }

            .smiles-examples {
                margin-top: 20px;
            }

            .smiles-examples h4 {
                margin-bottom: 10px;
                color: #666;
            }

            .example-chips {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
            }

            .chip {
                padding: 6px 12px;
                background: #f0f0f0;
                border-radius: 20px;
                cursor: pointer;
                transition: all 0.2s;
                font-size: 14px;
            }

            .chip:hover {
                background: #667eea;
                color: white;
            }

            .ketcher-container {
                width: 100%;
                height: 400px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                overflow: hidden;
                position: relative;
            }

            .visual-controls {
                margin-top: 15px;
                display: flex;
                gap: 10px;
            }

            .common-structures h4 {
                margin-bottom: 15px;
                color: #333;
            }

            .structure-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                gap: 10px;
            }

            .structure-item {
                padding: 10px;
                background: #f8f9fa;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                cursor: pointer;
                text-align: center;
                transition: all 0.2s;
            }

            .structure-item:hover {
                border-color: #667eea;
                background: #f0f3ff;
            }

            .structure-item .name {
                font-weight: 500;
                margin-bottom: 4px;
            }

            .structure-item .smiles {
                font-size: 12px;
                color: #666;
                font-family: monospace;
            }

            .preview-section {
                margin: 20px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 8px;
            }

            .preview-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
            }

            .preview-header h3 {
                margin: 0;
                color: #333;
            }

            .format-selector {
                display: flex;
                gap: 8px;
            }

            .format-btn {
                padding: 6px 12px;
                border: 2px solid #e0e0e0;
                background: white;
                border-radius: 6px;
                cursor: pointer;
                transition: all 0.2s;
            }

            .format-btn:hover {
                border-color: #667eea;
            }

            .format-btn.active {
                background: #667eea;
                color: white;
                border-color: #667eea;
            }

            .structure-preview {
                min-height: 200px;
                background: white;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }

            .structure-preview svg {
                max-width: 100%;
                height: auto;
            }

            .structure-preview img {
                max-width: 100%;
                height: auto;
            }

            .structure-preview .latex-code {
                width: 100%;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 6px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 14px;
                white-space: pre-wrap;
                word-break: break-all;
            }

            .placeholder {
                color: #999;
                font-style: italic;
            }

            .preview-info {
                margin-top: 15px;
                padding: 10px;
                background: white;
                border-radius: 6px;
                font-size: 14px;
            }

            .export-section {
                padding: 20px;
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
                border-top: 1px solid #e0e0e0;
            }

            .btn {
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 500;
                transition: all 0.2s;
            }

            .btn-primary {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }

            .btn-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            }

            .btn-secondary {
                background: #6c757d;
                color: white;
            }

            .btn-success {
                background: #28a745;
                color: white;
            }

            .btn-outline {
                background: white;
                border: 2px solid #e0e0e0;
                color: #333;
            }

            .btn-outline:hover {
                border-color: #667eea;
                color: #667eea;
            }

            .loading-message {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 40px;
                color: #666;
            }

            .spinner {
                width: 40px;
                height: 40px;
                border: 4px solid #e0e0e0;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-bottom: 10px;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * 绑定事件
     */
    bindEvents() {
        // 标签页切换
        this.container.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // SMILES 输入
        const smilesInput = this.container.querySelector('#smiles-input');
        smilesInput.addEventListener('input', debounce(() => {
            this.onSmilesInput(smilesInput.value);
        }, 500));

        // 验证按钮
        this.container.querySelector('#validate-btn').addEventListener('click', () => {
            this.validateSmiles(smilesInput.value);
        });

        // 清除按钮
        this.container.querySelector('#clear-btn').addEventListener('click', () => {
            smilesInput.value = '';
            this.clearPreview();
        });

        // 示例点击
        this.container.querySelectorAll('.chip').forEach(chip => {
            chip.addEventListener('click', () => {
                smilesInput.value = chip.dataset.smiles;
                this.onSmilesInput(chip.dataset.smiles);
            });
        });

        // 格式切换
        this.container.querySelectorAll('.format-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchFormat(e.target.dataset.format);
            });
        });

        // 导出按钮
        this.container.querySelector('#export-svg-btn').addEventListener('click', () => this.exportStructure('svg'));
        this.container.querySelector('#export-png-btn').addEventListener('click', () => this.exportStructure('png'));
        this.container.querySelector('#export-latex-btn').addEventListener('click', () => this.exportStructure('latex'));
        this.container.querySelector('#export-word-btn').addEventListener('click', () => this.exportToWord());
        this.container.querySelector('#copy-smiles-btn').addEventListener('click', () => this.copySmiles());

        // 可视化编辑器按钮
        this.container.querySelector('#get-smiles-btn')?.addEventListener('click', () => this.getSmilesFromKetcher());
        this.container.querySelector('#clear-canvas-btn')?.addEventListener('click', () => this.clearKetcher());
    }

    /**
     * 切换标签页
     */
    switchTab(tabName) {
        // 更新按钮状态
        this.container.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });

        // 更新面板显示
        this.container.querySelectorAll('.tab-panel').forEach(panel => {
            panel.classList.toggle('active', panel.id === `${tabName}-panel`);
        });
    }

    /**
     * 切换预览格式
     */
    switchFormat(format) {
        this.currentFormat = format;

        // 更新按钮状态
        this.container.querySelectorAll('.format-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.format === format);
        });

        // 更新预览
        if (this.currentSmiles) {
            this.updatePreview(this.currentSmiles);
        }
    }

    /**
     * SMILES 输入处理
     */
    async onSmilesInput(smiles) {
        if (!smiles.trim()) {
            this.clearPreview();
            return;
        }

        this.currentSmiles = smiles.trim();
        await this.updatePreview(this.currentSmiles);
    }

    /**
     * 验证 SMILES
     */
    async validateSmiles(smiles) {
        if (!smiles.trim()) {
            this.showStatus('请输入 SMILES', 'error');
            return;
        }

        try {
            const response = await fetch(`${this.options.apiBaseUrl}/validate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ smiles: smiles.trim() })
            });

            const result = await response.json();

            if (result.valid) {
                this.showStatus(`✓ 有效的 SMILES: ${result.canonical_smiles}`, 'success');
                this.currentSmiles = smiles.trim();
                await this.updatePreview(this.currentSmiles);
            } else {
                this.showStatus(`✗ 无效的 SMILES: ${result.error || '格式错误'}`, 'error');
            }
        } catch (error) {
            this.showStatus(`验证失败: ${error.message}`, 'error');
        }
    }

    /**
     * 更新预览
     */
    async updatePreview(smiles) {
        const preview = this.container.querySelector('#structure-preview');
        const info = this.container.querySelector('#preview-info');

        preview.innerHTML = '<div class="loading-message"><div class="spinner"></div><p>渲染中...</p></div>';

        try {
            if (this.currentFormat === 'svg') {
                const response = await fetch(`${this.options.apiBaseUrl}/render/svg`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ smiles, width: 600, height: 400 })
                });

                if (response.ok) {
                    const svg = await response.text();
                    preview.innerHTML = svg;
                } else {
                    preview.innerHTML = '<div class="placeholder">渲染失败</div>';
                }
            } else if (this.currentFormat === 'png') {
                const response = await fetch(`${this.options.apiBaseUrl}/render/png`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ smiles, width: 600, height: 400 })
                });

                if (response.ok) {
                    const result = await response.json();
                    preview.innerHTML = `<img src="data:image/png;base64,${result.data}" alt="分子结构">`;
                } else {
                    preview.innerHTML = '<div class="placeholder">渲染失败</div>';
                }
            } else if (this.currentFormat === 'latex') {
                const response = await fetch(`${this.options.apiBaseUrl}/export`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ smiles, format: 'latex' })
                });

                if (response.ok) {
                    const result = await response.json();
                    preview.innerHTML = `<div class="latex-code">${result.data}</div>`;
                } else {
                    preview.innerHTML = '<div class="placeholder">生成失败</div>';
                }
            }

            // 获取分子信息
            const infoResponse = await fetch(`${this.options.apiBaseUrl}/info`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ smiles })
            });

            if (infoResponse.ok) {
                const molInfo = await infoResponse.json();
                info.innerHTML = `
                    <strong>分子式:</strong> ${molInfo.formula || '-'} |
                    <strong>分子量:</strong> ${molInfo.molecular_weight ? molInfo.molecular_weight.toFixed(2) : '-'} |
                    <strong>原子数:</strong> ${molInfo.num_atoms || '-'} |
                    <strong>环数:</strong> ${molInfo.num_rings || '-'}
                `;
            }
        } catch (error) {
            preview.innerHTML = `<div class="placeholder">预览失败: ${error.message}</div>`;
        }
    }

    /**
     * 清空预览
     */
    clearPreview() {
        this.container.querySelector('#structure-preview').innerHTML =
            '<div class="placeholder">输入 SMILES 或绘制结构以预览</div>';
        this.container.querySelector('#preview-info').innerHTML = '';
        this.currentSmiles = '';
    }

    /**
     * 显示状态消息
     */
    showStatus(message, type) {
        const status = this.container.querySelector('#smiles-status');
        status.textContent = message;
        status.className = `status-message ${type}`;
    }

    /**
     * 加载 Ketcher 编辑器
     */
    async loadKetcher() {
        try {
            // 检查 Ketcher 是否已加载
            if (typeof Ketcher !== 'undefined') {
                await this.initKetcher();
                return;
            }

            // 动态加载 Ketcher
            const script = document.createElement('script');
            script.src = 'https://unpkg.com/ketcher@latest/dist/ketcher.min.js';
            script.onload = async () => {
                await this.initKetcher();
            };
            script.onerror = () => {
                console.warn('Failed to load Ketcher');
                this.container.querySelector('#ketcher-container').innerHTML =
                    '<div class="loading-message">可视化编辑器加载失败，请使用 SMILES 输入</div>';
            };
            document.head.appendChild(script);
        } catch (error) {
            console.error('Error loading Ketcher:', error);
        }
    }

    /**
     * 初始化 Ketcher
     */
    async initKetcher() {
        try {
            const ketcherContainer = this.container.querySelector('#ketcher-container');
            ketcherContainer.innerHTML = '';

            // 初始化 Ketcher
            this.ketcher = await Ketcher.init(ketcherContainer, {
                staticResourcesUrl: 'https://unpkg.com/ketcher@latest/dist/'
            });

            this.isKetcherLoaded = true;
            console.log('Ketcher loaded successfully');
        } catch (error) {
            console.error('Error initializing Ketcher:', error);
            this.container.querySelector('#ketcher-container').innerHTML =
                '<div class="loading-message">可视化编辑器初始化失败</div>';
        }
    }

    /**
     * 从 Ketcher 获取 SMILES
     */
    async getSmilesFromKetcher() {
        if (!this.ketcher) {
            this.showStatus('可视化编辑器未加载', 'error');
            return;
        }

        try {
            const smiles = await this.ketcher.getSmiles();
            if (smiles) {
                this.container.querySelector('#smiles-input').value = smiles;
                this.currentSmiles = smiles;
                await this.updatePreview(smiles);
                this.switchTab('smiles');
                this.showStatus(`从编辑器获取: ${smiles}`, 'success');
            } else {
                this.showStatus('画布为空', 'error');
            }
        } catch (error) {
            this.showStatus(`获取 SMILES 失败: ${error.message}`, 'error');
        }
    }

    /**
     * 清空 Ketcher 画布
     */
    clearKetcher() {
        if (this.ketcher) {
            this.ketcher.clear();
        }
    }

    /**
     * 加载常见结构
     */
    async loadCommonStructures() {
        try {
            const response = await fetch(`${this.options.apiBaseUrl}/common`);
            const structures = await response.json();

            const grid = this.container.querySelector('#structure-grid');
            grid.innerHTML = '';

            Object.entries(structures).forEach(([name, smiles]) => {
                const item = document.createElement('div');
                item.className = 'structure-item';
                item.innerHTML = `
                    <div class="name">${name}</div>
                    <div class="smiles">${smiles}</div>
                `;
                item.addEventListener('click', () => {
                    this.container.querySelector('#smiles-input').value = smiles;
                    this.onSmilesInput(smiles);
                    this.switchTab('smiles');
                });
                grid.appendChild(item);
            });
        } catch (error) {
            console.error('Error loading common structures:', error);
        }
    }

    /**
     * 导出结构
     */
    async exportStructure(format) {
        if (!this.currentSmiles) {
            this.showStatus('请先输入或绘制结构', 'error');
            return;
        }

        try {
            const response = await fetch(`${this.options.apiBaseUrl}/export`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    smiles: this.currentSmiles,
                    format: format,
                    width: 800,
                    height: 600
                })
            });

            if (!response.ok) {
                throw new Error('导出失败');
            }

            const result = await response.json();

            if (format === 'svg') {
                this.downloadFile(result.data, 'structure.svg', 'image/svg+xml');
            } else if (format === 'png') {
                this.downloadBase64(result.data, 'structure.png', 'image/png');
            } else if (format === 'latex') {
                this.downloadFile(result.data, 'structure.tex', 'text/plain');
            }

            this.showStatus(`✓ 已导出 ${format.toUpperCase()} 格式`, 'success');
        } catch (error) {
            this.showStatus(`导出失败: ${error.message}`, 'error');
        }
    }

    /**
     * 导出到 Word
     */
    async exportToWord() {
        if (!this.currentSmiles) {
            this.showStatus('请先输入或绘制结构', 'error');
            return;
        }

        try {
            const response = await fetch(`${this.options.apiBaseUrl}/export`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    smiles: this.currentSmiles,
                    format: 'svg',
                    width: 600,
                    height: 400
                })
            });

            if (!response.ok) {
                throw new Error('导出失败');
            }

            const result = await response.json();

            // 复制 SVG 到剪贴板
            await navigator.clipboard.writeText(result.data);
            this.showStatus('✓ 已复制 SVG 到剪贴板，可直接粘贴到 Word', 'success');
        } catch (error) {
            this.showStatus(`导出失败: ${error.message}`, 'error');
        }
    }

    /**
     * 复制 SMILES
     */
    async copySmiles() {
        if (!this.currentSmiles) {
            this.showStatus('没有可复制的 SMILES', 'error');
            return;
        }

        try {
            await navigator.clipboard.writeText(this.currentSmiles);
            this.showStatus('✓ 已复制 SMILES 到剪贴板', 'success');
        } catch (error) {
            this.showStatus(`复制失败: ${error.message}`, 'error');
        }
    }

    /**
     * 下载文件
     */
    downloadFile(content, filename, mimeType) {
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
     * 下载 base64 文件
     */
    downloadBase64(base64Data, filename, mimeType) {
        const byteCharacters = atob(base64Data);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: mimeType });
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
     * 获取当前 SMILES
     */
    getCurrentSmiles() {
        return this.currentSmiles;
    }

    /**
     * 设置 SMILES
     */
    async setSmiles(smiles) {
        this.container.querySelector('#smiles-input').value = smiles;
        this.currentSmiles = smiles;
        await this.updatePreview(smiles);
    }
}

// 工具函数：防抖
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

// 导出到全局
window.StructureEditor = StructureEditor;
