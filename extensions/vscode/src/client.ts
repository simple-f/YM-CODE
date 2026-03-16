import * as vscode from 'vscode';
import axios from 'axios';

const YM_CODE_API = 'http://localhost:18770/api';

/**
 * YM-CODE API 客户端
 */
class YMCodeClient {
    private baseUrl: string;

    constructor(baseUrl: string = YM_CODE_API) {
        this.baseUrl = baseUrl;
    }

    /**
     * 分析代码
     */
    async analyzeCode(code: string, language: string = 'python'): Promise<any> {
        try {
            const response = await axios.post(`${this.baseUrl}/skills/execute`, {
                skill: 'code_analyzer',
                arguments: {
                    code: code,
                    language: language
                }
            });
            return response.data;
        } catch (error: any) {
            throw new Error(`YM-CODE API 调用失败：${error.message}`);
        }
    }

    /**
     * 格式化代码
     */
    async formatCode(code: string, language: string = 'python'): Promise<any> {
        try {
            const response = await axios.post(`${this.baseUrl}/skills/execute`, {
                skill: 'code_analyzer',
                arguments: {
                    code: code,
                    language: language,
                    tools: ['black']
                }
            });
            return response.data;
        } catch (error: any) {
            throw new Error(`YM-CODE API 调用失败：${error.message}`);
        }
    }

    /**
     * 检查代码
     */
    async checkCode(code: string, language: string = 'python'): Promise<any> {
        try {
            const response = await axios.post(`${this.baseUrl}/skills/execute`, {
                skill: 'code_analyzer',
                arguments: {
                    code: code,
                    language: language,
                    tools: ['pylint', 'flake8']
                }
            });
            return response.data;
        } catch (error: any) {
            throw new Error(`YM-CODE API 调用失败：${error.message}`);
        }
    }
}

export default YMCodeClient;
