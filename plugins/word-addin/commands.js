/**
 * ChemMaster Word Add-in 命令处理
 * 处理功能区按钮点击事件
 */

// Office 初始化
Office.onReady((info) => {
    console.log('Commands.js initialized');
});

/**
 * 插入化学式命令
 * 从功能区按钮触发
 */
function insertFormula(event) {
    // 显示输入对话框
    const formula = prompt('请输入化学式（例如: H2SO4）:');

    if (!formula) {
        event.completed();
        return;
    }

    // 转换并插入
    convertAndInsert(formula, 'formula')
        .then(() => {
            event.completed();
        })
        .catch((error) => {
            console.error('Insert formula error:', error);
            event.completed();
        });
}

/**
 * 转换并插入到文档
 */
async function convertAndInsert(input, type) {
    const apiBaseUrl = 'http://localhost:8000/api/export';

    try {
        let result;

        if (type === 'formula') {
            const response = await fetch(`${apiBaseUrl}/formula`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    formula: input,
                    format: 'standard'
                })
            });

            if (!response.ok) {
                throw new Error('转换失败');
            }

            result = await response.json();
        } else {
            const response = await fetch(`${apiBaseUrl}/equation`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    equation: input,
                    format: 'standard',
                    balance: true
                })
            });

            if (!response.ok) {
                throw new Error('转换失败');
            }

            result = await response.json();
        }

        // 插入到 Word
        await Word.run(async (context) => {
            const body = context.document.body;
            const content = result.unicode || result.latex || input;
            body.insertParagraph(content, Word.InsertLocation.end);
            await context.sync();
        });

        return result;
    } catch (error) {
        console.error('Convert and insert error:', error);
        throw error;
    }
}

/**
 * 快速插入预设化学式
 */
function insertPresetFormula(event) {
    const presets = [
        { name: '水', formula: 'H2O' },
        { name: '硫酸', formula: 'H2SO4' },
        { name: '氢氧化钠', formula: 'NaOH' },
        { name: '氯化钠', formula: 'NaCl' },
        { name: '二氧化碳', formula: 'CO2' },
        { name: '碳酸钙', formula: 'CaCO3' }
    ];

    const selected = prompt(
        '选择预设化学式:\n' +
        presets.map((p, i) => `${i + 1}. ${p.name} (${p.formula})`).join('\n') +
        '\n\n输入序号:'
    );

    const index = parseInt(selected) - 1;

    if (index >= 0 && index < presets.length) {
        convertAndInsert(presets[index].formula, 'formula')
            .then(() => event.completed())
            .catch(() => event.completed());
    } else {
        event.completed();
    }
}

// 导出函数供 Office.js 使用
if (typeof Office !== 'undefined') {
    Office.actions = {
        insertFormula: insertFormula,
        insertPresetFormula: insertPresetFormula
    };
}
