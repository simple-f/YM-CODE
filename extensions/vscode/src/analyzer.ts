import * as vscode from 'vscode';
import YMCodeClient from './client';

/**
 * 代码分析器
 */
export class CodeAnalyzer {
    private client: YMCodeClient;
    private diagnosticCollection: vscode.DiagnosticCollection;

    constructor() {
        this.client = new YMCodeClient();
        this.diagnosticCollection = vscode.languages.createDiagnosticCollection('ymcode');
    }

    /**
     * 分析当前文档
     */
    async analyzeDocument(document: vscode.TextDocument): Promise<void> {
        const code = document.getText();
        const language = document.languageId;

        try {
            const result = await this.client.analyzeCode(code, language);
            
            if (result.success && result.results) {
                this.showAnalysisResult(document, result);
            }
        } catch (error: any) {
            vscode.window.showErrorMessage(`YM-CODE 分析失败：${error.message}`);
        }
    }

    /**
     * 显示分析结果
     */
    private showAnalysisResult(document: vscode.TextDocument, result: any): void {
        const diagnostics: vscode.Diagnostic[] = [];

        for (const toolResult of result.results) {
            if (toolResult.error) {
                continue;
            }

            const analysis = toolResult.result;
            if (analysis.issues) {
                for (const issue of analysis.issues) {
                    const line = issue.line - 1; // 转换为 0-based
                    const range = new vscode.Range(line, 0, line, 100);
                    
                    const diagnostic = new vscode.Diagnostic(
                        range,
                        `${issue.message} (${issue.code})`,
                        this.getSeverity(issue.type)
                    );
                    
                    diagnostics.push(diagnostic);
                }
            }
        }

        this.diagnosticCollection.set(document.uri, diagnostics);
    }

    /**
     * 获取问题严重程度
     */
    private getSeverity(type: string): vscode.DiagnosticSeverity {
        switch (type.toLowerCase()) {
            case 'error':
                return vscode.DiagnosticSeverity.Error;
            case 'warning':
                return vscode.DiagnosticSeverity.Warning;
            case 'information':
                return vscode.DiagnosticSeverity.Information;
            default:
                return vscode.DiagnosticSeverity.Hint;
        }
    }

    /**
     * 格式化文档
     */
    async formatDocument(document: vscode.TextDocument): Promise<void> {
        const code = document.getText();
        const language = document.languageId;

        try {
            const result = await this.client.formatCode(code, language);
            
            if (result.success && result.results) {
                const formatted = result.results[0]?.result?.formatted_code;
                if (formatted) {
                    const edit = new vscode.WorkspaceEdit();
                    const fullRange = new vscode.Range(
                        document.positionAt(0),
                        document.positionAt(code.length)
                    );
                    edit.replace(document.uri, fullRange, formatted);
                    await vscode.workspace.applyEdit(edit);
                    
                    vscode.window.showInformationMessage('YM-CODE 格式化完成');
                }
            }
        } catch (error: any) {
            vscode.window.showErrorMessage(`YM-CODE 格式化失败：${error.message}`);
        }
    }

    /**
     * 检查代码
     */
    async checkCode(document: vscode.TextDocument): Promise<void> {
        const code = document.getText();
        const language = document.languageId;

        try {
            const result = await this.client.checkCode(code, language);
            
            if (result.success) {
                const summary = result.summary;
                vscode.window.showInformationMessage(
                    `YM-CODE 检查完成：${summary.total_issues} 个问题，` +
                    `${summary.total_errors} 个错误，${summary.total_warnings} 个警告`
                );
            }
        } catch (error: any) {
            vscode.window.showErrorMessage(`YM-CODE 检查失败：${error.message}`);
        }
    }

    /**
     * 清理诊断
     */
    dispose(): void {
        this.diagnosticCollection.dispose();
    }
}
