/**
 * YM-CODE Webview Provider
 */

import * as vscode from 'vscode';
import { YMCodeAPI } from './api';

export class YMCodeProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'ym-code.mainPanel';
    private _view?: vscode.WebviewView;
    private _api: YMCodeAPI;
    private _messages: Array<{ role: string; content: string }> = [];

    constructor(
        private readonly _extensionUri: vscode.Uri,
        api: YMCodeAPI
    ) {
        this._api = api;
    }

    /**
     * 解析 webview
     */
    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken
    ) {
        this._view = webviewView;

        // 设置 webview 选项
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };

        // 设置 HTML 内容
        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

        // 监听消息
        webviewView.webview.onDidReceiveMessage(async (message) => {
            switch (message.type) {
                case 'sendMessage':
                    await this._handleUserMessage(message.content);
                    break;
                case 'clearHistory':
                    this._messages = [];
                    break;
            }
        });
    }

    /**
     * 处理用户消息
     */
    private async _handleUserMessage(content: string) {
        // 添加用户消息
        this._messages.push({ role: 'user', content });

        // 显示加载状态
        this._updateWebview();

        try {
            // 调用 API
            const response = await this._api.sendMessage(this._messages);

            // 添加 AI 响应
            this._messages.push({ role: 'assistant', content: response.content });

            // 更新界面
            this._updateWebview();
        } catch (error) {
            vscode.window.showErrorMessage(`YM-CODE 错误：${error}`);
        }
    }

    /**
     * 发送消息
     */
    public async sendMessage(content: string) {
        if (this._view) {
            this._view.webview.postMessage({
                type: 'addMessage',
                content
            });
            await this._handleUserMessage(content);
        }
    }

    /**
     * 显示面板
     */
    public async show() {
        if (!this._view) {
            await vscode.commands.executeCommand('ym-code.mainPanel.focus');
        }
        this._view?.show?.(true);
    }

    /**
     * 清空历史
     */
    public async clearHistory() {
        this._messages = [];
        if (this._view) {
            this._view.webview.postMessage({ type: 'clearHistory' });
        }
    }

    /**
     * 更新 webview
     */
    private _updateWebview() {
        if (this._view) {
            this._view.webview.postMessage({
                type: 'updateMessages',
                messages: this._messages
            });
        }
    }

    /**
     * 生成 HTML
     */
    private _getHtmlForWebview(webview: vscode.Webview) {
        const styleUri = webview.asWebviewUri(
            vscode.Uri.joinPath(this._extensionUri, 'media', 'styles.css')
        );

        const scriptUri = webview.asWebviewUri(
            vscode.Uri.joinPath(this._extensionUri, 'media', 'script.js')
        );

        const nonce = this._getNonce();

        return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource} 'unsafe-inline'; script-src 'nonce-${nonce}';">
    <title>YM-CODE Assistant</title>
    <link href="${styleUri}" rel="stylesheet">
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 YM-CODE</h1>
            <span class="subtitle">AI Programming Assistant</span>
        </div>
        
        <div id="messages" class="messages">
            <div class="welcome-message">
                <p>👋 你好！我是 YM-CODE，你的 AI 编程助手。</p>
                <p>我可以帮你：</p>
                <ul>
                    <li>解释代码</li>
                    <li>重构代码</li>
                    <li>调试问题</li>
                    <li>生成测试</li>
                    <li>Code Review</li>
                </ul>
                <p>在下方输入你的问题吧！</p>
            </div>
        </div>
        
        <div class="input-area">
            <textarea 
                id="input" 
                placeholder="输入你的问题... (Ctrl+Enter 发送)"
                rows="3"
            ></textarea>
            <button id="send" class="send-button">发送</button>
        </div>
        
        <div class="footer">
            <span>Powered by YM-CODE</span>
            <button id="clear" class="clear-button">清空历史</button>
        </div>
    </div>
    
    <script nonce="${nonce}" src="${scriptUri}"></script>
</body>
</html>`;
    }

    /**
     * 生成 nonce
     */
    private _getNonce() {
        let text = '';
        const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        for (let i = 0; i < 32; i++) {
            text += possible.charAt(Math.floor(Math.random() * possible.length));
        }
        return text;
    }
}
