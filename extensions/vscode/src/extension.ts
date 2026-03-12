import * as vscode from 'vscode';

// YM-CODE API 配置
const YM_CODE_API_URL = 'http://localhost:8000/api';

/**
 * 激活插件
 */
export function activate(context: vscode.ExtensionContext) {
    console.log('YM-CODE 插件已激活');

    // 注册命令：运行 AI Agent
    const runCommand = vscode.commands.registerCommand('ym-code.run', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('请先打开一个文件');
            return;
        }

        const selection = editor.selection;
        const code = editor.document.getText(selection);

        if (!code) {
            vscode.window.showErrorMessage('请先选择一些代码');
            return;
        }

        await runAI(code, 'run');
    });

    // 注册命令：解释代码
    const explainCommand = vscode.commands.registerCommand('ym-code.explain', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('请先打开一个文件');
            return;
        }

        const selection = editor.selection;
        const code = editor.document.getText(selection);

        if (!code) {
            vscode.window.showErrorMessage('请先选择一些代码');
            return;
        }

        await runAI(code, 'explain');
    });

    // 注册命令：审查代码
    const reviewCommand = vscode.commands.registerCommand('ym-code.review', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('请先打开一个文件');
            return;
        }

        const selection = editor.selection;
        const code = editor.document.getText(selection);

        if (!code) {
            vscode.window.showErrorMessage('请先选择一些代码');
            return;
        }

        await runAI(code, 'review');
    });

    // 添加到上下文
    context.subscriptions.push(runCommand, explainCommand, reviewCommand);
}

/**
 * 运行 AI 请求
 */
async function runAI(code: string, mode: 'run' | 'explain' | 'review') {
    const panel = vscode.window.createWebviewPanel(
        'ymcode',
        'YM-CODE',
        vscode.ViewColumn.Beside,
        {}
    );

    panel.webview.html = getLoadingHtml();

    try {
        // 模拟 API 调用（实际应该调用 YM-CODE API）
        const result = await mockAICall(code, mode);
        
        panel.webview.html = getResultHtml(result, mode);
    } catch (error) {
        panel.webview.html = getErrorHtml(error);
    }
}

/**
 * 模拟 AI 调用
 */
async function mockAICall(code: string, mode: string): Promise<string> {
    // 模拟延迟
    await new Promise(resolve => setTimeout(resolve, 2000));

    switch (mode) {
        case 'explain':
            return `## 代码解释

这段代码实现了一个函数，主要功能如下：

1. **输入处理**：接收参数并验证
2. **核心逻辑**：执行主要业务逻辑
3. **输出结果**：返回处理结果

**关键点：**
- 使用了异步编程
- 包含错误处理
- 遵循最佳实践`;

        case 'review':
            return `## 代码审查报告

### ✅ 优点
- 代码结构清晰
- 命名规范
- 包含错误处理

### ⚠️ 改进建议
1. 可以添加更多注释
2. 考虑边界条件
3. 添加单元测试

### 📊 评分：8.5/10`;

        case 'run':
        default:
            return `## 执行结果

代码已成功执行！

**输出：**
\`\`\`
执行成功
\`\`\`

**建议：**
- 代码运行正常
- 性能良好
- 无错误`;
    }
}

/**
 * 获取加载页面 HTML
 */
function getLoadingHtml(): string {
    return `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: var(--vscode-font-family);
            padding: 20px;
            color: var(--vscode-foreground);
        }
        .loading {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 200px;
        }
        .spinner {
            border: 4px solid var(--vscode-progressBar-background);
            border-top: 4px solid var(--vscode-button-background);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="loading">
        <div class="spinner"></div>
        <span style="margin-left: 10px;">YM-CODE 正在思考中...</span>
    </div>
</body>
</html>
    `;
}

/**
 * 获取结果页面 HTML
 */
function getResultHtml(result: string, mode: string): string {
    const title = mode === 'explain' ? '代码解释' : mode === 'review' ? '代码审查' : '执行结果';
    
    return `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: var(--vscode-font-family);
            padding: 20px;
            color: var(--vscode-foreground);
            line-height: 1.6;
        }
        h1 {
            color: var(--vscode-button-background);
        }
        h2 {
            color: var(--vscode-editor-foreground);
            border-bottom: 1px solid var(--vscode-editor-lineHighlightBorder);
            padding-bottom: 10px;
        }
        code {
            background-color: var(--vscode-textCodeBlock-background);
            padding: 2px 4px;
            border-radius: 3px;
        }
        pre {
            background-color: var(--vscode-textCodeBlock-background);
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <h1>${title}</h1>
    <div id="content">
        ${result.replace(/\n/g, '<br>')}
    </div>
</body>
</html>
    `;
}

/**
 * 获取错误页面 HTML
 */
function getErrorHtml(error: any): string {
    return `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: var(--vscode-font-family);
            padding: 20px;
            color: var(--vscode-errorForeground);
        }
        .error {
            border: 1px solid var(--vscode-errorForeground);
            padding: 20px;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="error">
        <h2>❌ 错误</h2>
        <p>${error.message || '发生未知错误'}</p>
    </div>
</body>
</html>
    `;
}

/**
 * 停用插件
 */
export function deactivate() {}
