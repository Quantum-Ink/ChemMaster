/**
 * ChemMaster 3D 分子可视化模块
 * 基于 3Dmol.js 实现 Mercury 风格的分子查看器
 */

class MoleculeViewer {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            width: options.width || 800,
            height: options.height || 500,
            apiBaseUrl: options.apiBaseUrl || '/api/structure',
            backgroundColor: options.backgroundColor || '#ffffff',
            ...options
        };

        this.viewer = null;
        this.currentSmiles = '';
        this.currentSdf = '';
        this.currentStyle = 'ball-and-stick';
        this.is3DmolLoaded = false;

        this.init();
    }

    async init() {
        this.createUI();
        await this.load3Dmol();
        this.bindEvents();
    }

    // ========== UI 构建 ==========

    createUI() {
        this.container.innerHTML = `
            <div class="mol-viewer">
                <div class="viewer-controls">
                    <div class="control-row">
                        <div class="input-group-inline">
                            <label>SMILES / 化合物名称</label>
                            <div class="input-with-btn">
                                <input type="text" id="viewer-input" class="viewer-input"
                                       placeholder="输入 SMILES 或化合物英文名称 (如: aspirin, caffeine)">
                                <button id="viewer-load-btn" class="btn btn-primary">加载</button>
                                <button id="viewer-clear-btn" class="btn btn-outline">清除</button>
                            </div>
                        </div>
                        <div class="input-group-inline">
                            <label>从文件加载</label>
                            <input type="file" id="viewer-file" accept=".sdf,.mol,.pdb,.mol2" class="file-input">
                        </div>
                    </div>

                    <div class="control-row">
                        <div class="style-group">
                            <label>显示模式</label>
                            <div class="style-buttons">
                                <button class="style-btn active" data-style="ball-and-stick" title="球棍模型">
                                    <span class="style-icon">⚛</span> 球棍
                                </button>
                                <button class="style-btn" data-style="spacefill" title="空间填充">
                                    <span class="style-icon">🔴</span> 空间填充
                                </button>
                                <button class="style-btn" data-style="stick" title="棍棒模型">
                                    <span class="style-icon">🥢</span> 棍棒
                                </button>
                                <button class="style-btn" data-style="wireframe" title="线框模型">
                                    <span class="style-icon">🔲</span> 线框
                                </button>
                            </div>
                        </div>

                        <div class="style-group">
                            <label>操作</label>
                            <div class="style-buttons">
                                <button id="viewer-spin-btn" class="style-btn" title="自动旋转">🔄 旋转</button>
                                <button id="viewer-h-btn" class="style-btn" title="显示/隐藏氢原子">H 原子</button>
                                <button id="viewer-label-btn" class="style-btn" title="显示原子标签">标签</button>
                                <button id="viewer-surface-btn" class="style-btn" title="显示分子表面">表面</button>
                            </div>
                        </div>

                        <div class="style-group">
                            <label>导出</label>
                            <div class="style-buttons">
                                <button id="viewer-export-png" class="btn btn-sm btn-primary">📸 截图</button>
                            </div>
                        </div>
                    </div>

                    <div id="viewer-status" class="viewer-status"></div>
                </div>

                <div class="viewer-3d-container" id="viewer-3d-canvas">
                    <div class="viewer-placeholder">
                        <div class="placeholder-icon">🔬</div>
                        <p>输入 SMILES 或化合物名称加载 3D 结构</p>
                        <p class="placeholder-hint">支持鼠标旋转、滚轮缩放、右键平移</p>
                    </div>
                </div>

                <div class="viewer-info" id="viewer-info"></div>
            </div>
        `;

        this.addStyles();
    }

    addStyles() {
        if (document.getElementById('mol-viewer-styles')) return;
        const style = document.createElement('style');
        style.id = 'mol-viewer-styles';
        style.textContent = `
            .mol-viewer {
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                background: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
                overflow: hidden;
            }

            .viewer-controls {
                padding: 16px 20px;
                background: #fafafa;
                border-bottom: 1px solid #e0e0e0;
            }

            .control-row {
                display: flex;
                gap: 20px;
                margin-bottom: 12px;
                flex-wrap: wrap;
                align-items: flex-end;
            }

            .control-row:last-of-type { margin-bottom: 0; }

            .input-group-inline {
                display: flex;
                flex-direction: column;
                gap: 6px;
            }

            .input-group-inline label {
                font-size: 12px;
                font-weight: 600;
                color: #666;
            }

            .input-with-btn {
                display: flex;
                gap: 8px;
            }

            .viewer-input {
                width: 360px;
                padding: 8px 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                font-family: 'Consolas', monospace;
                transition: border-color 0.2s;
            }

            .viewer-input:focus {
                outline: none;
                border-color: #667eea;
            }

            .file-input {
                font-size: 13px;
                padding: 6px;
            }

            .style-group {
                display: flex;
                flex-direction: column;
                gap: 6px;
            }

            .style-group label {
                font-size: 12px;
                font-weight: 600;
                color: #666;
            }

            .style-buttons {
                display: flex;
                gap: 6px;
            }

            .style-btn {
                padding: 6px 12px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                background: white;
                cursor: pointer;
                font-size: 12px;
                font-weight: 500;
                transition: all 0.15s;
                white-space: nowrap;
            }

            .style-btn:hover {
                border-color: #667eea;
                color: #667eea;
            }

            .style-btn.active {
                background: #667eea;
                color: white;
                border-color: #667eea;
            }

            .style-icon {
                font-size: 14px;
            }

            .viewer-status {
                font-size: 13px;
                color: #888;
                min-height: 20px;
                margin-top: 8px;
            }

            .viewer-status.error { color: #dc3545; }
            .viewer-status.success { color: #28a745; }

            .viewer-3d-container {
                width: 100%;
                height: 500px;
                position: relative;
                background: #ffffff;
            }

            .viewer-placeholder {
                position: absolute;
                inset: 0;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                color: #999;
                z-index: 1;
            }

            .placeholder-icon {
                font-size: 64px;
                margin-bottom: 16px;
                opacity: 0.5;
            }

            .viewer-placeholder p {
                font-size: 16px;
                margin: 4px 0;
            }

            .placeholder-hint {
                font-size: 13px !important;
                color: #bbb !important;
            }

            .viewer-info {
                padding: 12px 20px;
                background: #f8f9fa;
                border-top: 1px solid #e0e0e0;
                font-size: 13px;
                color: #666;
                min-height: 20px;
            }

            .viewer-info .info-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 8px;
            }

            .viewer-info .info-item {
                display: flex;
                gap: 6px;
            }

            .viewer-info .info-label {
                font-weight: 600;
                color: #555;
            }

            .btn {
                padding: 8px 16px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 500;
                transition: all 0.15s;
            }

            .btn-sm { padding: 6px 12px; font-size: 12px; }
            .btn-primary { background: #667eea; color: white; }
            .btn-primary:hover { background: #5a6fd6; }
            .btn-outline { background: white; border: 2px solid #e0e0e0; color: #333; }
            .btn-outline:hover { border-color: #667eea; color: #667eea; }
        `;
        document.head.appendChild(style);
    }

    // ========== 3Dmol.js 加载 ==========

    async load3Dmol() {
        return new Promise((resolve) => {
            if (typeof $3Dmol !== 'undefined') {
                this.initViewer();
                resolve();
                return;
            }

            const script = document.createElement('script');
            script.src = 'https://3Dmol.org/build/3Dmol-min.js';
            script.onload = () => {
                setTimeout(() => {
                    this.initViewer();
                    resolve();
                }, 100);
            };
            script.onerror = () => {
                this.showStatus('3Dmol.js 加载失败，请检查网络连接', 'error');
                resolve();
            };
            document.head.appendChild(script);
        });
    }

    initViewer() {
        try {
            const canvasContainer = this.container.querySelector('#viewer-3d-canvas');
            canvasContainer.innerHTML = '';

            this.viewer = $3Dmol.createViewer(canvasContainer, {
                backgroundColor: this.options.backgroundColor,
                antialias: true,
                cartoonQuality: 10
            });

            this.is3DmolLoaded = true;
            this.viewer.render();
        } catch (error) {
            console.error('3Dmol init error:', error);
            this.showStatus('3D 查看器初始化失败: ' + error.message, 'error');
        }
    }

    // ========== 事件绑定 ==========

    bindEvents() {
        const input = this.container.querySelector('#viewer-input');
        const loadBtn = this.container.querySelector('#viewer-load-btn');
        const clearBtn = this.container.querySelector('#viewer-clear-btn');
        const fileInput = this.container.querySelector('#viewer-file');

        // 加载按钮
        loadBtn.addEventListener('click', () => this.loadMolecule(input.value.trim()));

        // 回车加载
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.loadMolecule(input.value.trim());
        });

        // 清除
        clearBtn.addEventListener('click', () => {
            input.value = '';
            this.clearViewer();
        });

        // 文件上传
        fileInput.addEventListener('change', (e) => this.loadFromFile(e));

        // 显示模式
        this.container.querySelectorAll('.style-btn[data-style]').forEach(btn => {
            btn.addEventListener('click', () => {
                this.currentStyle = btn.dataset.style;
                this.container.querySelectorAll('.style-btn[data-style]').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.applyStyle();
            });
        });

        // 自动旋转
        this.container.querySelector('#viewer-spin-btn').addEventListener('click', (e) => {
            if (!this.viewer) return;
            const btn = e.currentTarget;
            const isSpinning = btn.classList.toggle('active');
            this.viewer.spin(isSpinning ? 'y' : false);
        });

        // 氢原子显示
        this.container.querySelector('#viewer-h-btn').addEventListener('click', (e) => {
            e.currentTarget.classList.toggle('active');
            this.toggleHydrogens();
        });

        // 原子标签
        this.container.querySelector('#viewer-label-btn').addEventListener('click', (e) => {
            e.currentTarget.classList.toggle('active');
            this.toggleLabels();
        });

        // 分子表面
        this.container.querySelector('#viewer-surface-btn').addEventListener('click', (e) => {
            e.currentTarget.classList.toggle('active');
            this.toggleSurface();
        });

        // 截图
        this.container.querySelector('#viewer-export-png').addEventListener('click', () => this.exportPNG());
    }

    // ========== 分子加载 ==========

    async loadMolecule(input) {
        if (!input) {
            this.showStatus('请输入 SMILES 或化合物名称', 'error');
            return;
        }

        if (!this.is3DmolLoaded) {
            this.showStatus('3D 查看器尚未加载完成，请稍候', 'error');
            return;
        }

        this.showStatus('加载中...', '');

        // 判断输入类型
        const isSmiles = /[=\#\[\]\(\)@+\\\/]/.test(input) || input.length < 50;

        try {
            if (isSmiles) {
                await this.loadFromSmiles(input);
            } else {
                await this.loadFromPubChem(input);
            }
        } catch (error) {
            this.showStatus(`加载失败: ${error.message}`, 'error');
        }
    }

    async loadFromSmiles(smiles) {
        try {
            // 先验证并获取 3D SDF
            const response = await fetch(`${this.options.apiBaseUrl}/3d`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ smiles })
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || '生成 3D 结构失败');
            }

            const result = await response.json();
            this.currentSmiles = smiles;
            this.currentSdf = result.sdf;

            this.renderSdf(result.sdf);
            this.showStatus(`✓ 已加载: ${result.formula || smiles}`, 'success');
            this.updateInfo(result.info || {});
        } catch (error) {
            throw error;
        }
    }

    async loadFromPubChem(name) {
        try {
            const response = await fetch(`${this.options.apiBaseUrl}/pubchem/3d`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name })
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || 'PubChem 查询失败');
            }

            const result = await response.json();
            this.currentSmiles = result.smiles || '';
            this.currentSdf = result.sdf;

            this.renderSdf(result.sdf);
            this.showStatus(`✓ 已从 PubChem 加载: ${result.name || name}`, 'success');
            this.updateInfo(result.info || {});
        } catch (error) {
            throw error;
        }
    }

    async loadFromFile(event) {
        const file = event.target.files[0];
        if (!file) return;

        if (!this.is3DmolLoaded) {
            this.showStatus('3D 查看器尚未加载完成', 'error');
            return;
        }

        const text = await file.text();
        const ext = file.name.split('.').pop().toLowerCase();

        this.currentSdf = text;

        try {
            this.viewer.removeAllModels();

            const format = ext === 'pdb' ? 'pdb' : ext === 'mol2' ? 'mol2' : 'sdf';
            const model = this.viewer.addModel(text, format);

            this.applyStyle();
            this.viewer.zoomTo();
            this.viewer.render();

            this.showStatus(`✓ 已加载文件: ${file.name}`, 'success');

            // 获取分子信息
            const atoms = model.selectedAtoms();
            this.updateInfo({
                num_atoms: atoms.length,
                formula: this.extractFormulaFromSdf(text)
            });
        } catch (error) {
            this.showStatus(`文件解析失败: ${error.message}`, 'error');
        }
    }

    // ========== 渲染 ==========

    renderSdf(sdf) {
        if (!this.viewer) return;

        this.viewer.removeAllModels();
        const model = this.viewer.addModel(sdf, 'sdf');
        this.applyStyle();
        this.viewer.zoomTo();
        this.viewer.render();

        // 隐藏占位符
        const placeholder = this.container.querySelector('.viewer-placeholder');
        if (placeholder) placeholder.style.display = 'none';
    }

    applyStyle() {
        if (!this.viewer) return;

        this.viewer.setStyle({}, {}); // 清除所有样式

        const showH = this.container.querySelector('#viewer-h-btn')?.classList.contains('active');

        switch (this.currentStyle) {
            case 'ball-and-stick':
                this.viewer.setStyle({}, {
                    stick: { radius: 0.15, colorscheme: 'Jmol' },
                    sphere: { scale: 0.3, colorscheme: 'Jmol' }
                });
                if (showH) {
                    this.viewer.setStyle({ elem: 'H' }, {
                        stick: { radius: 0.1, colorscheme: 'Jmol' },
                        sphere: { scale: 0.2, colorscheme: 'Jmol' }
                    });
                }
                break;

            case 'spacefill':
                this.viewer.setStyle({}, {
                    sphere: { colorscheme: 'Jmol' }
                });
                break;

            case 'stick':
                this.viewer.setStyle({}, {
                    stick: { colorscheme: 'Jmol' }
                });
                break;

            case 'wireframe':
                this.viewer.setStyle({}, {
                    line: { colorscheme: 'Jmol' }
                });
                break;
        }

        if (!showH) {
            this.viewer.setStyle({ elem: 'H' }, {});
        }

        this.viewer.render();
    }

    toggleHydrogens() {
        this.applyStyle();
    }

    toggleLabels() {
        if (!this.viewer) return;

        const showLabels = this.container.querySelector('#viewer-label-btn')?.classList.contains('active');

        if (showLabels) {
            const atoms = this.viewer.getModel().selectedAtoms();
            atoms.forEach((atom, i) => {
                this.viewer.addLabel(atom.elem, {
                    position: { x: atom.x, y: atom.y, z: atom.z },
                    fontSize: 11,
                    fontColor: 'white',
                    backgroundColor: '#333',
                    backgroundOpacity: 0.7,
                    borderRadius: 4
                }, { atomindex: i });
            });
        } else {
            this.viewer.removeAllLabels();
        }

        this.viewer.render();
    }

    toggleSurface() {
        if (!this.viewer) return;

        const showSurface = this.container.querySelector('#viewer-surface-btn')?.classList.contains('active');

        if (showSurface) {
            this.viewer.addSurface($3Dmol.SurfaceType.VDW, {
                opacity: 0.6,
                color: 'white'
            });
        } else {
            this.viewer.removeAllSurfaces();
        }

        this.viewer.render();
    }

    clearViewer() {
        if (this.viewer) {
            this.viewer.removeAllModels();
            this.viewer.removeAllLabels();
            this.viewer.removeAllSurfaces();
            this.viewer.render();
        }

        this.currentSmiles = '';
        this.currentSdf = '';

        const placeholder = this.container.querySelector('.viewer-placeholder');
        if (placeholder) placeholder.style.display = 'flex';

        this.container.querySelector('#viewer-info').innerHTML = '';
        this.showStatus('', '');
    }

    // ========== 导出 ==========

    exportPNG() {
        if (!this.viewer) return;

        const png = this.viewer.pngURI();
        const a = document.createElement('a');
        a.href = png;
        a.download = 'molecule-3d.png';
        a.click();
    }

    // ========== 信息显示 ==========

    updateInfo(info) {
        const infoEl = this.container.querySelector('#viewer-info');
        if (!info || Object.keys(info).length === 0) {
            infoEl.innerHTML = '';
            return;
        }

        const items = [];
        if (info.formula) items.push(`<span class="info-item"><span class="info-label">分子式:</span> ${info.formula}</span>`);
        if (info.molecular_weight) items.push(`<span class="info-item"><span class="info-label">分子量:</span> ${info.molecular_weight.toFixed(2)}</span>`);
        if (info.num_atoms) items.push(`<span class="info-item"><span class="info-label">原子数:</span> ${info.num_atoms}</span>`);
        if (info.num_bonds) items.push(`<span class="info-item"><span class="info-label">键数:</span> ${info.num_bonds}</span>`);
        if (info.num_rings !== undefined) items.push(`<span class="info-item"><span class="info-label">环数:</span> ${info.num_rings}</span>`);
        if (info.iupac_name) items.push(`<span class="info-item"><span class="info-label">IUPAC名:</span> ${info.iupac_name}</span>`);

        infoEl.innerHTML = `<div class="info-grid">${items.join('')}</div>`;
    }

    showStatus(message, type) {
        const status = this.container.querySelector('#viewer-status');
        status.textContent = message;
        status.className = `viewer-status ${type || ''}`;
    }

    extractFormulaFromSdf(sdf) {
        // 简单从 SDF 提取分子式
        try {
            const atoms = {};
            const lines = sdf.split('\n');
            // SDF 第三行通常包含原子数和键数
            const countsLine = lines[3];
            if (countsLine) {
                const parts = countsLine.trim().split(/\s+/);
                const numAtoms = parseInt(parts[0]);
                for (let i = 4; i < 4 + numAtoms && i < lines.length; i++) {
                    const atomLine = lines[i].trim().split(/\s+/);
                    const elem = atomLine[3] || 'C';
                    atoms[elem] = (atoms[elem] || 0) + 1;
                }
            }

            // Hill 系统
            const order = [];
            if (atoms['C']) { order.push(['C', atoms['C']]); delete atoms['C']; }
            if (atoms['H']) { order.push(['H', atoms['H']]); delete atoms['H']; }
            for (const key of Object.keys(atoms).sort()) {
                order.push([key, atoms[key]]);
            }

            return order.map(([e, c]) => c > 1 ? `${e}${c}` : e).join('');
        } catch {
            return '';
        }
    }
}

// 导出到全局
window.MoleculeViewer = MoleculeViewer;
