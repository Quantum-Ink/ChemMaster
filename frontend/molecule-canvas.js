/**
 * ChemMaster Canvas 画布式分子结构编辑器
 * 参考 GeoGebra 简洁模式，支持拖拽绘制有机物结构
 */

class MoleculeCanvas {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.options = {
            width: options.width || 900,
            height: options.height || 560,
            atomRadius: options.atomRadius || 18,
            bondLength: options.bondLength || 50,
            ...options
        };

        // 分子数据
        this.atoms = [];
        this.bonds = [];
        this.nextAtomId = 1;
        this.nextBondId = 1;

        // 编辑器状态
        this.currentTool = 'atom';
        this.currentElement = 'C';
        this.currentBondType = 1; // 1=单键, 2=双键, 3=三键
        this.hoveredAtom = null;
        this.selectedAtom = null;
        this.dragStartAtom = null;
        this.dragLine = null;
        this.isDragging = false;

        // 画布状态
        this.offsetX = 0;
        this.offsetY = 0;
        this.scale = 1;
        this.isPanning = false;
        this.panStart = { x: 0, y: 0 };

        // 撤销/重做
        this.undoStack = [];
        this.redoStack = [];

        // 元素颜色
        this.ELEMENT_COLORS = {
            'C': '#333333', 'N': '#3050F8', 'O': '#FF0D0D',
            'S': '#FFFF30', 'P': '#FF8000', 'F': '#90E050',
            'Cl': '#1FF01F', 'Br': '#A62929', 'I': '#940094',
            'H': '#CCCCCC'
        };

        // 元素默认价态
        this.ELEMENT_VALENCE = {
            'C': 4, 'N': 3, 'O': 2, 'S': 2, 'P': 3,
            'F': 1, 'Cl': 1, 'Br': 1, 'I': 1, 'H': 1
        };

        // 延迟初始化：等待标签页可见后再创建画布
        this._initialized = false;
        this._onTabShown = (e) => {
            if (e.detail.tabId === 'structure-tab' && !this._initialized) {
                this._initialized = true;
                this.init();
            } else if (e.detail.tabId === 'structure-tab' && this._initialized) {
                this.resize();
            }
        };
        window.addEventListener('tab-shown', this._onTabShown);
    }

    init() {
        this.createUI();
        this.setupCanvas();
        this.bindEvents();
        this.draw();
    }

    resize() {
        const area = this.container.querySelector('.mol-canvas-area');
        if (!area) return;
        const rect = area.getBoundingClientRect();
        if (rect.width < 10 || rect.height < 10) return;
        this.canvas.width = rect.width;
        this.canvas.height = rect.height;
        this.offsetX = this.canvas.width / 2;
        this.offsetY = this.canvas.height / 2;
        this.draw();
    }

    // ========== UI 构建 ==========

    createUI() {
        this.container.innerHTML = `
            <div class="mol-canvas-editor">
                <div class="mol-canvas-toolbar">
                    <!-- 原子工具 -->
                    <div class="tool-group">
                        <div class="tool-group-label">原子</div>
                        <div class="atom-tools">
                            <button class="atom-btn active" data-element="C" title="碳 C">C</button>
                            <button class="atom-btn" data-element="N" title="氮 N">N</button>
                            <button class="atom-btn" data-element="O" title="氧 O">O</button>
                            <button class="atom-btn" data-element="S" title="硫 S">S</button>
                            <button class="atom-btn" data-element="P" title="磷 P">P</button>
                            <button class="atom-btn" data-element="F" title="氟 F">F</button>
                            <button class="atom-btn" data-element="Cl" title="氯 Cl">Cl</button>
                            <button class="atom-btn" data-element="Br" title="溴 Br">Br</button>
                            <button class="atom-btn" data-element="I" title="碘 I">I</button>
                            <button class="atom-btn" data-element="H" title="氢 H">H</button>
                        </div>
                    </div>

                    <!-- 键型工具 -->
                    <div class="tool-group">
                        <div class="tool-group-label">键型</div>
                        <div class="bond-tools">
                            <button class="bond-btn active" data-bond="1" title="单键">
                                <svg width="24" height="24"><line x1="4" y1="12" x2="20" y2="12" stroke="currentColor" stroke-width="2"/></svg>
                            </button>
                            <button class="bond-btn" data-bond="2" title="双键">
                                <svg width="24" height="24"><line x1="4" y1="9" x2="20" y2="9" stroke="currentColor" stroke-width="2"/><line x1="4" y1="15" x2="20" y2="15" stroke="currentColor" stroke-width="2"/></svg>
                            </button>
                            <button class="bond-btn" data-bond="3" title="三键">
                                <svg width="24" height="24"><line x1="4" y1="7" x2="20" y2="7" stroke="currentColor" stroke-width="2"/><line x1="4" y1="12" x2="20" y2="12" stroke="currentColor" stroke-width="2"/><line x1="4" y1="17" x2="20" y2="17" stroke="currentColor" stroke-width="2"/></svg>
                            </button>
                        </div>
                    </div>

                    <!-- 操作工具 -->
                    <div class="tool-group">
                        <div class="tool-group-label">工具</div>
                        <div class="action-tools">
                            <button class="tool-btn" id="eraser-btn" title="橡皮擦">🗑️</button>
                            <button class="tool-btn" id="undo-btn" title="撤销 (Ctrl+Z)">↩️</button>
                            <button class="tool-btn" id="redo-btn" title="重做 (Ctrl+Y)">↪️</button>
                            <button class="tool-btn" id="clear-btn" title="清空画布">❌</button>
                        </div>
                    </div>

                    <!-- 模板 -->
                    <div class="tool-group">
                        <div class="tool-group-label">模板</div>
                        <div class="template-tools">
                            <button class="template-btn" data-template="benzene" title="苯环">⬡</button>
                            <button class="template-btn" data-template="cyclohexane" title="环己烷">⬡H</button>
                            <button class="template-btn" data-template="cyclopentane" title="环戊烷">⬠</button>
                            <button class="template-btn" data-template="oh" title="羟基 -OH">OH</button>
                            <button class="template-btn" data-template="cooh" title="羧基 -COOH">COOH</button>
                            <button class="template-btn" data-template="nh2" title="氨基 -NH₂">NH₂</button>
                            <button class="template-btn" data-template="cho" title="醛基 -CHO">CHO</button>
                            <button class="template-btn" data-template="no2" title="硝基 -NO₂">NO₂</button>
                        </div>
                    </div>
                </div>

                <div class="mol-canvas-area">
                    <canvas id="${this.containerId}-canvas"></canvas>
                </div>

                <div class="mol-canvas-footer">
                    <div class="footer-left">
                        <span class="mol-formula" id="${this.containerId}-formula">分子式: —</span>
                        <span class="mol-weight" id="${this.containerId}-weight">分子量: —</span>
                    </div>
                    <div class="footer-center">
                        <input type="text" class="smiles-output" id="${this.containerId}-smiles"
                               placeholder="SMILES 输出" readonly>
                        <button class="btn btn-sm btn-copy" id="${this.containerId}-copy-smiles">复制</button>
                    </div>
                    <div class="footer-right">
                        <button class="btn btn-sm btn-primary" id="${this.containerId}-export-svg">导出 SVG</button>
                        <button class="btn btn-sm btn-primary" id="${this.containerId}-export-png">导出 PNG</button>
                    </div>
                </div>
            </div>
        `;

        this.addStyles();
    }

    addStyles() {
        if (document.getElementById('mol-canvas-styles')) return;
        const style = document.createElement('style');
        style.id = 'mol-canvas-styles';
        style.textContent = `
            .mol-canvas-editor {
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                background: #fafafa;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
                overflow: hidden;
                display: flex;
                flex-direction: column;
            }

            .mol-canvas-toolbar {
                display: flex;
                align-items: center;
                gap: 16px;
                padding: 10px 16px;
                background: white;
                border-bottom: 1px solid #e0e0e0;
                flex-wrap: wrap;
            }

            .tool-group {
                display: flex;
                align-items: center;
                gap: 6px;
            }

            .tool-group-label {
                font-size: 11px;
                color: #888;
                margin-right: 4px;
                white-space: nowrap;
            }

            .atom-tools, .bond-tools, .action-tools, .template-tools {
                display: flex;
                gap: 4px;
            }

            .atom-btn {
                width: 32px;
                height: 32px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                background: white;
                font-weight: 700;
                font-size: 13px;
                cursor: pointer;
                transition: all 0.15s;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .atom-btn:hover { border-color: #667eea; color: #667eea; }
            .atom-btn.active { background: #667eea; color: white; border-color: #667eea; }

            .bond-btn {
                width: 32px;
                height: 32px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                background: white;
                cursor: pointer;
                transition: all 0.15s;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #555;
            }

            .bond-btn:hover { border-color: #667eea; color: #667eea; }
            .bond-btn.active { background: #667eea; color: white; border-color: #667eea; }

            .tool-btn {
                width: 32px;
                height: 32px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                background: white;
                cursor: pointer;
                transition: all 0.15s;
                font-size: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .tool-btn:hover { border-color: #667eea; }
            .tool-btn.active { background: #ff4757; color: white; border-color: #ff4757; }

            .template-btn {
                height: 30px;
                padding: 0 10px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                background: white;
                cursor: pointer;
                transition: all 0.15s;
                font-size: 12px;
                font-weight: 600;
                color: #555;
            }

            .template-btn:hover { border-color: #2ed573; color: #2ed573; }

            .mol-canvas-area {
                flex: 1;
                display: flex;
                align-items: center;
                justify-content: center;
                background: white;
                cursor: crosshair;
                min-height: 400px;
            }

            .mol-canvas-area canvas {
                display: block;
            }

            .mol-canvas-footer {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 10px 16px;
                background: white;
                border-top: 1px solid #e0e0e0;
                gap: 12px;
                flex-wrap: wrap;
            }

            .footer-left {
                display: flex;
                gap: 16px;
                font-size: 13px;
                color: #666;
            }

            .footer-center {
                display: flex;
                gap: 8px;
                align-items: center;
                flex: 1;
                max-width: 400px;
            }

            .smiles-output {
                flex: 1;
                padding: 6px 10px;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                font-family: 'Consolas', monospace;
                font-size: 13px;
                background: #f8f9fa;
                color: #333;
            }

            .footer-right {
                display: flex;
                gap: 8px;
            }

            .btn {
                padding: 6px 14px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 13px;
                font-weight: 500;
                transition: all 0.15s;
            }

            .btn-sm { padding: 5px 12px; font-size: 12px; }
            .btn-primary { background: #667eea; color: white; }
            .btn-primary:hover { background: #5a6fd6; }
            .btn-copy { background: #f0f0f0; color: #333; }
            .btn-copy:hover { background: #e0e0e0; }
        `;
        document.head.appendChild(style);
    }

    // ========== Canvas 设置 ==========

    setupCanvas() {
        this.canvas = this.container.querySelector('canvas');
        this.ctx = this.canvas.getContext('2d');

        const area = this.container.querySelector('.mol-canvas-area');
        const rect = area.getBoundingClientRect();
        this.canvas.width = rect.width || this.options.width;
        this.canvas.height = rect.height || this.options.height;

        // 居中偏移
        this.offsetX = this.canvas.width / 2;
        this.offsetY = this.canvas.height / 2;
    }

    // ========== 事件绑定 ==========

    bindEvents() {
        const area = this.container.querySelector('.mol-canvas-area');

        // Canvas 鼠标事件
        this.canvas.addEventListener('mousedown', (e) => this.onMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.onMouseMove(e));
        this.canvas.addEventListener('mouseup', (e) => this.onMouseUp(e));
        this.canvas.addEventListener('wheel', (e) => this.onWheel(e));
        this.canvas.addEventListener('contextmenu', (e) => e.preventDefault());

        // 原子按钮
        this.container.querySelectorAll('.atom-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.currentTool = 'atom';
                this.currentElement = btn.dataset.element;
                this.container.querySelectorAll('.atom-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.container.querySelector('#eraser-btn').classList.remove('active');
            });
        });

        // 键型按钮
        this.container.querySelectorAll('.bond-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.currentBondType = parseInt(btn.dataset.bond);
                this.container.querySelectorAll('.bond-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });

        // 橡皮擦
        this.container.querySelector('#eraser-btn').addEventListener('click', () => {
            this.currentTool = this.currentTool === 'eraser' ? 'atom' : 'eraser';
            this.container.querySelector('#eraser-btn').classList.toggle('active');
        });

        // 撤销/重做
        this.container.querySelector('#undo-btn').addEventListener('click', () => this.undo());
        this.container.querySelector('#redo-btn').addEventListener('click', () => this.redo());

        // 清空
        this.container.querySelector('#clear-btn').addEventListener('click', () => this.clearAll());

        // 模板
        this.container.querySelectorAll('.template-btn').forEach(btn => {
            btn.addEventListener('click', () => this.placeTemplate(btn.dataset.template));
        });

        // 导出按钮
        this.container.querySelector(`#${this.container.id}-export-svg`)
            .addEventListener('click', () => this.exportSVG());
        this.container.querySelector(`#${this.container.id}-export-png`)
            .addEventListener('click', () => this.exportPNG());
        this.container.querySelector(`#${this.container.id}-copy-smiles`)
            .addEventListener('click', () => this.copySmiles());

        // 键盘快捷键
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'z') { e.preventDefault(); this.undo(); }
            if (e.ctrlKey && e.key === 'y') { e.preventDefault(); this.redo(); }
        });

        // 窗口大小变化
        window.addEventListener('resize', () => this.setupCanvas());
    }

    // ========== 坐标转换 ==========

    screenToCanvas(x, y) {
        const rect = this.canvas.getBoundingClientRect();
        return {
            x: (x - rect.left - this.offsetX) / this.scale,
            y: (y - rect.top - this.offsetY) / this.scale
        };
    }

    canvasToScreen(x, y) {
        return {
            x: x * this.scale + this.offsetX,
            y: y * this.scale + this.offsetY
        };
    }

    // ========== 鼠标交互 ==========

    onMouseDown(e) {
        const pos = this.screenToCanvas(e.clientX, e.clientY);

        // 右键平移
        if (e.button === 2) {
            this.isPanning = true;
            this.panStart = { x: e.clientX - this.offsetX, y: e.clientY - this.offsetY };
            return;
        }

        // 中键平移
        if (e.button === 1) {
            this.isPanning = true;
            this.panStart = { x: e.clientX - this.offsetX, y: e.clientY - this.offsetY };
            return;
        }

        const hovered = this.findAtomAt(pos.x, pos.y);

        if (this.currentTool === 'eraser') {
            if (hovered) {
                this.saveState();
                this.removeAtom(hovered.id);
            } else {
                const bond = this.findBondAt(pos.x, pos.y);
                if (bond) {
                    this.saveState();
                    this.removeBond(bond.id);
                }
            }
            return;
        }

        if (hovered) {
            this.dragStartAtom = hovered;
            this.isDragging = true;
        } else {
            this.saveState();
            this.addAtom(this.currentElement, pos.x, pos.y);
        }
    }

    onMouseMove(e) {
        const pos = this.screenToCanvas(e.clientX, e.clientY);

        if (this.isPanning) {
            this.offsetX = e.clientX - this.panStart.x;
            this.offsetY = e.clientY - this.panStart.y;
            this.draw();
            return;
        }

        this.hoveredAtom = this.findAtomAt(pos.x, pos.y);

        if (this.isDragging && this.dragStartAtom) {
            this.dragLine = { x: pos.x, y: pos.y };
        }

        this.draw();
    }

    onMouseUp(e) {
        if (this.isPanning) {
            this.isPanning = false;
            return;
        }

        if (this.isDragging && this.dragStartAtom) {
            const pos = this.screenToCanvas(e.clientX, e.clientY);
            const target = this.findAtomAt(pos.x, pos.y);

            if (target && target.id !== this.dragStartAtom.id) {
                // 检查是否已存在键
                const existing = this.findBond(this.dragStartAtom.id, target.id);
                if (existing) {
                    // 循环切换键型
                    this.saveState();
                    existing.type = existing.type >= 3 ? 1 : existing.type + 1;
                } else {
                    this.saveState();
                    this.addBond(this.dragStartAtom.id, target.id, this.currentBondType);
                }
            } else if (!target) {
                // 拖拽到空白处：在目标位置创建新原子并连接
                const dx = pos.x - this.dragStartAtom.x;
                const dy = pos.y - this.dragStartAtom.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist > 10) {
                    this.saveState();
                    // 按标准键长对齐
                    const bl = this.options.bondLength;
                    const angle = Math.atan2(dy, dx);
                    const nx = this.dragStartAtom.x + bl * Math.cos(angle);
                    const ny = this.dragStartAtom.y + bl * Math.sin(angle);
                    const newAtom = this.addAtom(this.currentElement, nx, ny);
                    this.addBond(this.dragStartAtom.id, newAtom.id, this.currentBondType);
                }
            }
        }

        this.isDragging = false;
        this.dragStartAtom = null;
        this.dragLine = null;
        this.draw();
    }

    onWheel(e) {
        e.preventDefault();
        const pos = this.screenToCanvas(e.clientX, e.clientY);
        const zoomFactor = e.deltaY > 0 ? 0.9 : 1.1;
        const newScale = Math.max(0.3, Math.min(3, this.scale * zoomFactor));

        // 以鼠标位置为中心缩放
        this.offsetX = e.clientX - (e.clientX - this.offsetX) * (newScale / this.scale);
        this.offsetY = e.clientY - (e.clientY - this.offsetY) * (newScale / this.scale);
        this.scale = newScale;

        this.draw();
    }

    // ========== 分子数据操作 ==========

    addAtom(element, x, y) {
        const atom = { id: this.nextAtomId++, element, x, y };
        this.atoms.push(atom);
        this.updateInfo();
        return atom;
    }

    addBond(fromId, toId, type) {
        const bond = { id: this.nextBondId++, from: fromId, to: toId, type };
        this.bonds.push(bond);
        this.updateInfo();
        return bond;
    }

    removeAtom(id) {
        this.atoms = this.atoms.filter(a => a.id !== id);
        this.bonds = this.bonds.filter(b => b.from !== id && b.to !== id);
        this.updateInfo();
    }

    removeBond(id) {
        this.bonds = this.bonds.filter(b => b.id !== id);
        this.updateInfo();
    }

    findAtomAt(x, y) {
        const r = this.options.atomRadius / this.scale;
        for (let i = this.atoms.length - 1; i >= 0; i--) {
            const a = this.atoms[i];
            const dx = a.x - x;
            const dy = a.y - y;
            if (dx * dx + dy * dy < r * r * 2) return a;
        }
        return null;
    }

    findBondAt(x, y) {
        const threshold = 8 / this.scale;
        for (const bond of this.bonds) {
            const a = this.atoms.find(a => a.id === bond.from);
            const b = this.atoms.find(a => a.id === bond.to);
            if (!a || !b) continue;
            const dist = this.pointToSegmentDist(x, y, a.x, a.y, b.x, b.y);
            if (dist < threshold) return bond;
        }
        return null;
    }

    findBond(fromId, toId) {
        return this.bonds.find(b =>
            (b.from === fromId && b.to === toId) ||
            (b.from === toId && b.to === fromId)
        );
    }

    pointToSegmentDist(px, py, ax, ay, bx, by) {
        const dx = bx - ax, dy = by - ay;
        const len2 = dx * dx + dy * dy;
        if (len2 === 0) return Math.sqrt((px - ax) ** 2 + (py - ay) ** 2);
        let t = ((px - ax) * dx + (py - ay) * dy) / len2;
        t = Math.max(0, Math.min(1, t));
        const projX = ax + t * dx, projY = ay + t * dy;
        return Math.sqrt((px - projX) ** 2 + (py - projY) ** 2);
    }

    // ========== 撤销/重做 ==========

    saveState() {
        this.undoStack.push({
            atoms: JSON.parse(JSON.stringify(this.atoms)),
            bonds: JSON.parse(JSON.stringify(this.bonds))
        });
        this.redoStack = [];
        if (this.undoStack.length > 50) this.undoStack.shift();
    }

    undo() {
        if (this.undoStack.length === 0) return;
        this.redoStack.push({
            atoms: JSON.parse(JSON.stringify(this.atoms)),
            bonds: JSON.parse(JSON.stringify(this.bonds))
        });
        const state = this.undoStack.pop();
        this.atoms = state.atoms;
        this.bonds = state.bonds;
        this.updateInfo();
        this.draw();
    }

    redo() {
        if (this.redoStack.length === 0) return;
        this.undoStack.push({
            atoms: JSON.parse(JSON.stringify(this.atoms)),
            bonds: JSON.parse(JSON.stringify(this.bonds))
        });
        const state = this.redoStack.pop();
        this.atoms = state.atoms;
        this.bonds = state.bonds;
        this.updateInfo();
        this.draw();
    }

    clearAll() {
        if (this.atoms.length === 0) return;
        this.saveState();
        this.atoms = [];
        this.bonds = [];
        this.updateInfo();
        this.draw();
    }

    // ========== 模板 ==========

    placeTemplate(template) {
        this.saveState();
        const cx = 0, cy = 0;
        const bl = this.options.bondLength;

        const templates = {
            benzene: () => {
                const atoms = [];
                for (let i = 0; i < 6; i++) {
                    const angle = (Math.PI / 3) * i - Math.PI / 2;
                    atoms.push(this.addAtom('C', cx + bl * Math.cos(angle), cy + bl * Math.sin(angle)));
                }
                for (let i = 0; i < 6; i++) {
                    const bondType = i % 2 === 0 ? 2 : 1;
                    this.addBond(atoms[i].id, atoms[(i + 1) % 6].id, bondType);
                }
            },
            cyclohexane: () => {
                const atoms = [];
                for (let i = 0; i < 6; i++) {
                    const angle = (Math.PI / 3) * i - Math.PI / 2;
                    atoms.push(this.addAtom('C', cx + bl * Math.cos(angle), cy + bl * Math.sin(angle)));
                }
                for (let i = 0; i < 6; i++) {
                    this.addBond(atoms[i].id, atoms[(i + 1) % 6].id, 1);
                }
            },
            cyclopentane: () => {
                const atoms = [];
                for (let i = 0; i < 5; i++) {
                    const angle = (2 * Math.PI / 5) * i - Math.PI / 2;
                    atoms.push(this.addAtom('C', cx + bl * 0.85 * Math.cos(angle), cy + bl * 0.85 * Math.sin(angle)));
                }
                for (let i = 0; i < 5; i++) {
                    this.addBond(atoms[i].id, atoms[(i + 1) % 5].id, 1);
                }
            },
            oh: () => {
                const o = this.addAtom('O', cx, cy);
                const h = this.addAtom('H', cx + bl, cy);
                this.addBond(o.id, h.id, 1);
            },
            cooh: () => {
                const c = this.addAtom('C', cx, cy);
                const o1 = this.addAtom('O', cx + bl * 0.87, cy - bl * 0.5);
                const o2 = this.addAtom('O', cx + bl * 0.87, cy + bl * 0.5);
                const h = this.addAtom('H', cx + bl * 1.7, cy + bl * 0.5);
                this.addBond(c.id, o1.id, 2);
                this.addBond(c.id, o2.id, 1);
                this.addBond(o2.id, h.id, 1);
            },
            nh2: () => {
                const n = this.addAtom('N', cx, cy);
                const h1 = this.addAtom('H', cx + bl * 0.87, cy - bl * 0.5);
                const h2 = this.addAtom('H', cx + bl * 0.87, cy + bl * 0.5);
                this.addBond(n.id, h1.id, 1);
                this.addBond(n.id, h2.id, 1);
            },
            cho: () => {
                const c = this.addAtom('C', cx, cy);
                const o = this.addAtom('O', cx + bl * 0.87, cy - bl * 0.5);
                const h = this.addAtom('H', cx + bl * 0.87, cy + bl * 0.5);
                this.addBond(c.id, o.id, 2);
                this.addBond(c.id, h.id, 1);
            },
            no2: () => {
                const n = this.addAtom('N', cx, cy);
                const o1 = this.addAtom('O', cx + bl * 0.87, cy - bl * 0.5);
                const o2 = this.addAtom('O', cx + bl * 0.87, cy + bl * 0.5);
                this.addBond(n.id, o1.id, 2);
                this.addBond(n.id, o2.id, 1);
            }
        };

        if (templates[template]) {
            templates[template]();
            this.updateInfo();
            this.draw();
        }
    }

    // ========== 绘制 ==========

    draw() {
        const ctx = this.ctx;
        const w = this.canvas.width;
        const h = this.canvas.height;

        // 清空
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, w, h);

        // 绘制网格
        this.drawGrid(ctx, w, h);

        ctx.save();
        ctx.translate(this.offsetX, this.offsetY);
        ctx.scale(this.scale, this.scale);

        // 绘制键
        for (const bond of this.bonds) {
            this.drawBond(ctx, bond);
        }

        // 绘制拖拽线
        if (this.isDragging && this.dragStartAtom && this.dragLine) {
            ctx.strokeStyle = '#667eea';
            ctx.lineWidth = 2 / this.scale;
            ctx.setLineDash([6 / this.scale, 4 / this.scale]);
            ctx.beginPath();
            ctx.moveTo(this.dragStartAtom.x, this.dragStartAtom.y);
            ctx.lineTo(this.dragLine.x, this.dragLine.y);
            ctx.stroke();
            ctx.setLineDash([]);
        }

        // 绘制原子
        for (const atom of this.atoms) {
            this.drawAtom(ctx, atom, atom === this.hoveredAtom);
        }

        ctx.restore();
    }

    drawGrid(ctx, w, h) {
        const gridSize = 20 * this.scale;
        const ox = this.offsetX % gridSize;
        const oy = this.offsetY % gridSize;

        ctx.strokeStyle = '#f0f0f0';
        ctx.lineWidth = 1;

        for (let x = ox; x < w; x += gridSize) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, h);
            ctx.stroke();
        }
        for (let y = oy; y < h; y += gridSize) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(w, y);
            ctx.stroke();
        }
    }

    drawAtom(ctx, atom, hovered) {
        const color = this.ELEMENT_COLORS[atom.element] || '#333';
        const r = this.options.atomRadius;

        // 高亮
        if (hovered) {
            ctx.fillStyle = 'rgba(102, 126, 234, 0.15)';
            ctx.beginPath();
            ctx.arc(atom.x, atom.y, r * 1.5, 0, Math.PI * 2);
            ctx.fill();
        }

        // 原子标签背景
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(atom.x, atom.y, r, 0, Math.PI * 2);
        ctx.fill();

        // 原子标签
        ctx.fillStyle = color;
        ctx.font = `bold ${r * 1.1}px 'Segoe UI', sans-serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(atom.element, atom.x, atom.y);
    }

    drawBond(ctx, bond) {
        const a = this.atoms.find(at => at.id === bond.from);
        const b = this.atoms.find(at => at.id === bond.to);
        if (!a || !b) return;

        const dx = b.x - a.x;
        const dy = b.y - a.y;
        const len = Math.sqrt(dx * dx + dy * dy);
        if (len === 0) return;

        // 法线方向
        const nx = -dy / len;
        const ny = dx / len;

        ctx.strokeStyle = '#333';
        ctx.lineWidth = 2;
        ctx.lineCap = 'round';

        if (bond.type === 1) {
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.stroke();
        } else if (bond.type === 2) {
            const offset = 3;
            ctx.beginPath();
            ctx.moveTo(a.x + nx * offset, a.y + ny * offset);
            ctx.lineTo(b.x + nx * offset, b.y + ny * offset);
            ctx.stroke();
            ctx.beginPath();
            ctx.moveTo(a.x - nx * offset, a.y - ny * offset);
            ctx.lineTo(b.x - nx * offset, b.y - ny * offset);
            ctx.stroke();
        } else if (bond.type === 3) {
            const offset = 4;
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.stroke();
            ctx.beginPath();
            ctx.moveTo(a.x + nx * offset, a.y + ny * offset);
            ctx.lineTo(b.x + nx * offset, b.y + ny * offset);
            ctx.stroke();
            ctx.beginPath();
            ctx.moveTo(a.x - nx * offset, a.y - ny * offset);
            ctx.lineTo(b.x - nx * offset, b.y - ny * offset);
            ctx.stroke();
        }
    }

    // ========== SMILES 生成 ==========

    toSmiles() {
        if (this.atoms.length === 0) return '';

        // 构建邻接表
        const adj = {};
        for (const a of this.atoms) {
            adj[a.id] = [];
        }
        for (const b of this.bonds) {
            const bondSymbol = b.type === 1 ? '' : b.type === 2 ? '=' : '#';
            adj[b.from].push({ to: b.to, bond: bondSymbol });
            adj[b.to].push({ to: b.from, bond: bondSymbol });
        }

        // DFS 遍历生成 SMILES
        const visited = new Set();
        const smilesParts = [];

        const dfs = (atomId, bondSymbol) => {
            if (visited.has(atomId)) return '';
            visited.add(atomId);

            const atom = this.atoms.find(a => a.id === atomId);
            if (!atom) return '';

            let result = bondSymbol;

            // 非碳原子需要显示符号
            const needsBrackets = atom.element !== 'C' || adj[atomId].length === 0;
            if (needsBrackets) {
                result += `[${atom.element}]`;
            } else {
                result += atom.element;
            }

            // 获取未访问的邻居
            const neighbors = adj[atomId].filter(n => !visited.has(n.to));

            // 遍历所有邻居（除最后一个，直接追加）
            for (let i = 0; i < neighbors.length; i++) {
                const n = neighbors[i];
                if (i < neighbors.length - 1) {
                    // 分支
                    const branch = dfs(n.to, n.bond);
                    if (branch) result += `(${branch})`;
                } else {
                    // 直接追加
                    const chain = dfs(n.to, n.bond);
                    result += chain;
                }
            }

            return result;
        };

        // 从第一个原子开始
        const smiles = dfs(this.atoms[0].id, '');
        return smiles;
    }

    // ========== 分子信息 ==========

    getMolecularFormula() {
        const counts = {};
        for (const atom of this.atoms) {
            counts[atom.element] = (counts[atom.element] || 0) + 1;
        }

        // Hill 系统：C 先，H 其次，其余按字母
        const order = [];
        if (counts['C']) { order.push(['C', counts['C']]); delete counts['C']; }
        if (counts['H']) { order.push(['H', counts['H']]); delete counts['H']; }
        for (const key of Object.keys(counts).sort()) {
            order.push([key, counts[key]]);
        }

        return order.map(([elem, count]) => count > 1 ? `${elem}${count}` : elem).join('');
    }

    getMolecularWeight() {
        const WEIGHTS = {
            'C': 12.011, 'H': 1.008, 'N': 14.007, 'O': 15.999,
            'S': 32.065, 'P': 30.974, 'F': 18.998, 'Cl': 35.453,
            'Br': 79.904, 'I': 126.904
        };
        let mw = 0;
        for (const atom of this.atoms) {
            mw += WEIGHTS[atom.element] || 0;
        }
        return mw;
    }

    updateInfo() {
        const id = this.container.id;
        const formulaEl = document.getElementById(`${id}-formula`);
        const weightEl = document.getElementById(`${id}-weight`);
        const smilesEl = document.getElementById(`${id}-smiles`);

        if (this.atoms.length === 0) {
            if (formulaEl) formulaEl.textContent = '分子式: —';
            if (weightEl) weightEl.textContent = '分子量: —';
            if (smilesEl) smilesEl.value = '';
            return;
        }

        const formula = this.getMolecularFormula();
        const weight = this.getMolecularWeight().toFixed(2);
        const smiles = this.toSmiles();

        if (formulaEl) formulaEl.textContent = `分子式: ${formula}`;
        if (weightEl) weightEl.textContent = `分子量: ${weight}`;
        if (smilesEl) smilesEl.value = smiles;
    }

    // ========== 导出 ==========

    exportSVG() {
        if (this.atoms.length === 0) return;

        // 计算边界
        let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
        for (const a of this.atoms) {
            minX = Math.min(minX, a.x);
            minY = Math.min(minY, a.y);
            maxX = Math.max(maxX, a.x);
            maxY = Math.max(maxY, a.y);
        }

        const padding = 40;
        const w = maxX - minX + padding * 2;
        const h = maxY - minY + padding * 2;
        const ox = -minX + padding;
        const oy = -minY + padding;

        let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">`;
        svg += `<rect width="${w}" height="${h}" fill="white"/>`;

        // 键
        for (const bond of this.bonds) {
            const a = this.atoms.find(at => at.id === bond.from);
            const b = this.atoms.find(at => at.id === bond.to);
            if (!a || !b) continue;

            const ax = a.x + ox, ay = a.y + oy;
            const bx = b.x + ox, by = b.y + oy;
            const dx = bx - ax, dy = by - ay;
            const len = Math.sqrt(dx * dx + dy * dy);
            const nx = -dy / len * 3, ny = dx / len * 3;

            if (bond.type === 1) {
                svg += `<line x1="${ax}" y1="${ay}" x2="${bx}" y2="${by}" stroke="#333" stroke-width="2" stroke-linecap="round"/>`;
            } else if (bond.type === 2) {
                svg += `<line x1="${ax + nx}" y1="${ay + ny}" x2="${bx + nx}" y2="${by + ny}" stroke="#333" stroke-width="2" stroke-linecap="round"/>`;
                svg += `<line x1="${ax - nx}" y1="${ay - ny}" x2="${bx - nx}" y2="${by - ny}" stroke="#333" stroke-width="2" stroke-linecap="round"/>`;
            } else {
                svg += `<line x1="${ax}" y1="${ay}" x2="${bx}" y2="${by}" stroke="#333" stroke-width="2" stroke-linecap="round"/>`;
                svg += `<line x1="${ax + nx}" y1="${ay + ny}" x2="${bx + nx}" y2="${by + ny}" stroke="#333" stroke-width="2" stroke-linecap="round"/>`;
                svg += `<line x1="${ax - nx}" y1="${ay - ny}" x2="${bx - nx}" y2="${by - ny}" stroke="#333" stroke-width="2" stroke-linecap="round"/>`;
            }
        }

        // 原子
        for (const atom of this.atoms) {
            const color = this.ELEMENT_COLORS[atom.element] || '#333';
            const x = atom.x + ox, y = atom.y + oy;
            svg += `<circle cx="${x}" cy="${y}" r="16" fill="white"/>`;
            svg += `<text x="${x}" y="${y}" text-anchor="middle" dominant-baseline="central" font-weight="bold" font-size="15" fill="${color}" font-family="Segoe UI, sans-serif">${atom.element}</text>`;
        }

        svg += '</svg>';

        const blob = new Blob([svg], { type: 'image/svg+xml' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'molecule.svg';
        a.click();
        URL.revokeObjectURL(url);
    }

    exportPNG() {
        if (this.atoms.length === 0) return;

        // 使用当前 canvas 导出
        const tempCanvas = document.createElement('canvas');
        const tempCtx = tempCanvas.getContext('2d');

        // 计算边界
        let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
        for (const a of this.atoms) {
            minX = Math.min(minX, a.x);
            minY = Math.min(minY, a.y);
            maxX = Math.max(maxX, a.x);
            maxY = Math.max(maxY, a.y);
        }

        const padding = 40;
        const scale = 2; // 高清
        const w = (maxX - minX + padding * 2) * scale;
        const h = (maxY - minY + padding * 2) * scale;
        tempCanvas.width = w;
        tempCanvas.height = h;

        tempCtx.fillStyle = '#ffffff';
        tempCtx.fillRect(0, 0, w, h);
        tempCtx.scale(scale, scale);
        tempCtx.translate(-minX + padding, -minY + padding);

        // 绘制键
        for (const bond of this.bonds) {
            this.drawBond(tempCtx, bond);
        }

        // 绘制原子
        for (const atom of this.atoms) {
            this.drawAtom(tempCtx, atom, false);
        }

        tempCanvas.toBlob((blob) => {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'molecule.png';
            a.click();
            URL.revokeObjectURL(url);
        });
    }

    copySmiles() {
        const smiles = this.toSmiles();
        if (!smiles) return;
        navigator.clipboard.writeText(smiles).then(() => {
            const btn = this.container.querySelector(`#${this.container.id}-copy-smiles`);
            btn.textContent = '已复制 ✓';
            setTimeout(() => btn.textContent = '复制', 1500);
        });
    }

    // ========== 公共 API ==========

    getSmiles() { return this.toSmiles(); }
    getFormula() { return this.getMolecularFormula(); }
    getWeight() { return this.getMolecularWeight(); }
    getAtomCount() { return this.atoms.length; }
    getBondCount() { return this.bonds.length; }

    setSmiles(smiles) {
        // 简单 SMILES 解析（由后端处理更复杂的场景）
        console.log('SMILES import should be handled by backend');
    }
}

// 导出到全局
window.MoleculeCanvas = MoleculeCanvas;
