/**
 * YM-CODE VSCode Extension
 * AI Programming Assistant
 */

import * as vscode from 'vscode';
import { YMCodeProvider } from './provider';
import { YMCodeAPI } from './api';

let api: YMCodeAPI;
let panelProvider: YMCodeProvider;

/**
 * 激活扩展
 */
export function activate(context: vscode.ExtensionContext) {
    console.log('YM-CODE 扩展已激活');

    // 初始化 API
    const config = vscode.workspace.getConfiguration('ym-code');
    api = new YMCodeAPI(config.get('apiEndpoint', 'http://localhost:8080'));

    // 注册提供者
    panelProvider = new YMCodeProvider(context.extensionUri, api);

    // 注册侧边栏面板
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider(
            'ym-code.mainPanel',
            panelProvider,
            {
                webviewOptions: {
                    retainContextWhenHidden: true
                }
            }
        )
    );

    // 注册命令
    registerCommands(context);

    // 显示通知
    vscode.window.showInformationMessage('YM-CODE 已就绪！使用 Ctrl+Shift+M 打开面板');
}

/**
 * 注册命令
 */
function registerCommands(context: vscode.ExtensionContext) {
    // Ask AI
    context.subscriptions.push(
        vscode.commands.registerCommand('ym-code.ask', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('请先打开一个文件');
                return;
            }

            const selection = editor.selection;
            const selectedText = editor.document.getText(selection);

            const question = await vscode.window.showInputBox({
                prompt: '请输入你的问题',
                placeHolder: '例如：这段代码有什么问题？',
                value: selectedText ? `请解释这段代码：\n${selectedText}` : ''
            });

            if (question) {
                await panelProvider.sendMessage(question);
                await panelProvider.show();
            }
        })
    );

    // Explain Code
    context.subscriptions.push(
        vscode.commands.registerCommand('ym-code.explain', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('请先打开一个文件');
                return;
            }

            const selection = editor.selection;
            const selectedText = editor.document.getText(selection);

            if (!selectedText) {
                vscode.window.showWarningMessage('请先选择一段代码');
                return;
            }

            await panelProvider.sendMessage(`请解释这段代码：\n${selectedText}`);
            await panelProvider.show();
        })
    );

    // Refactor Code
    context.subscriptions.push(
        vscode.commands.registerCommand('ym-code.refactor', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('请先打开一个文件');
                return;
            }

            const selection = editor.selection;
            const selectedText = editor.document.getText(selection);

            if (!selectedText) {
                vscode.window.showWarningMessage('请先选择一段代码');
                return;
            }

            await panelProvider.sendMessage(`请重构这段代码，使其更清晰、更易维护：\n${selectedText}`);
            await panelProvider.show();
        })
    );

    // Debug Code
    context.subscriptions.push(
        vscode.commands.registerCommand('ym-code.debug', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('请先打开一个文件');
                return;
            }

            const selection = editor.selection;
            const selectedText = editor.document.getText(selection);

            if (!selectedText) {
                vscode.window.showWarningMessage('请先选择一段代码');
                return;
            }

            await panelProvider.sendMessage(`请帮我调试这段代码，找出可能的问题：\n${selectedText}`);
            await panelProvider.show();
        })
    );

    // Generate Tests
    context.subscriptions.push(
        vscode.commands.registerCommand('ym-code.test', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('请先打开一个文件');
                return;
            }

            const selectedText = editor.document.getText();

            await panelProvider.sendMessage(`请为这段代码生成单元测试：\n${selectedText}`);
            await panelProvider.show();
        })
    );

    // Code Review
    context.subscriptions.push(
        vscode.commands.registerCommand('ym-code.review', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('请先打开一个文件');
                return;
            }

            const selectedText = editor.document.getText();

            await panelProvider.sendMessage(`请对这段代码进行 Code Review，指出问题和改进建议：\n${selectedText}`);
            await panelProvider.show();
        })
    );

    // Show Panel
    context.subscriptions.push(
        vscode.commands.registerCommand('ym-code.showPanel', async () => {
            await panelProvider.show();
        })
    );

    // Clear History
    context.subscriptions.push(
        vscode.commands.registerCommand('ym-code.clearHistory', async () => {
            await panelProvider.clearHistory();
            vscode.window.showInformationMessage('YM-CODE 历史记录已清空');
        })
    );
}

/**
 * 停用扩展
 */
export function deactivate() {
    console.log('YM-CODE 扩展已停用');
}
