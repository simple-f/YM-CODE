import * as vscode from 'vscode';
import { CodeAnalyzer } from './analyzer';

export function activate(context: vscode.ExtensionContext) {
    console.log('YM-CODE 插件已激活');

    const analyzer = new CodeAnalyzer();

    // 注册命令：分析代码
    context.subscriptions.push(
        vscode.commands.registerCommand('ymcode.analyze', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('请先打开一个文件');
                return;
            }

            await analyzer.analyzeDocument(editor.document);
        })
    );

    // 注册命令：格式化代码
    context.subscriptions.push(
        vscode.commands.registerCommand('ymcode.format', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('请先打开一个文件');
                return;
            }

            await analyzer.formatDocument(editor.document);
        })
    );

    // 注册命令：检查代码
    context.subscriptions.push(
        vscode.commands.registerCommand('ymcode.check', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('请先打开一个文件');
                return;
            }

            await analyzer.checkCode(editor.document);
        })
    );

    // 监听文件保存，自动分析
    context.subscriptions.push(
        vscode.workspace.onDidSaveTextDocument(async (document) => {
            const config = vscode.workspace.getConfiguration('ymcode');
            if (config.get('autoAnalyzeOnSave')) {
                await analyzer.analyzeDocument(document);
            }
        })
    );
}

export function deactivate() {
    console.log('YM-CODE 插件已停用');
}
