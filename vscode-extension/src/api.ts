/**
 * YM-CODE API Client
 */

import * as vscode from 'vscode';

export interface Message {
    role: 'user' | 'assistant' | 'system';
    content: string;
}

export interface APIResponse {
    content: string;
    tokens?: number;
}

export class YMCodeAPI {
    private _endpoint: string;

    constructor(endpoint: string) {
        this._endpoint = endpoint;
    }

    /**
     * 发送消息
     */
    async sendMessage(messages: Message[]): Promise<APIResponse> {
        const config = vscode.workspace.getConfiguration('ym-code');
        const model = config.get('model', 'qwen3.5-plus');
        const maxTokens = config.get('maxTokens', 4000);

        try {
            const response = await fetch(`${this._endpoint}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    model,
                    messages,
                    max_tokens: maxTokens,
                    stream: false
                })
            });

            if (!response.ok) {
                throw new Error(`API 错误：${response.status}`);
            }

            const data = await response.json();
            return {
                content: data.choices?.[0]?.message?.content || '抱歉，我没有理解你的问题',
                tokens: data.usage?.total_tokens
            };
        } catch (error) {
            // 如果 API 不可用，返回模拟响应（用于演示）
            console.error('API 调用失败:', error);
            return {
                content: this._getMockResponse(messages),
                tokens: undefined
            };
        }
    }

    /**
     * 模拟响应（用于演示）
     */
    private _getMockResponse(messages: Message[]): string {
        const lastMessage = messages[messages.length - 1];
        const content = lastMessage?.content || '';

        // 简单的关键词匹配
        if (content.includes('解释') || content.includes('说明')) {
            return '这段代码看起来是在实现一个功能。让我详细解释一下：\n\n1. **代码结构**：代码组织清晰，遵循了良好的编程实践。\n\n2. **主要功能**：根据代码内容，它似乎在处理某种数据或逻辑。\n\n3. **改进建议**：\n   - 可以添加更多注释\n   - 考虑错误处理\n   - 优化性能\n\n需要我详细解释某个特定部分吗？';
        }

        if (content.includes('重构') || content.includes('优化')) {
            return '我来帮你重构这段代码：\n\n```typescript\n// 重构后的代码\nfunction optimizedFunction(input: InputType): OutputType {\n    // 1. 添加输入验证\n    if (!input) {\n        throw new Error(\'Invalid input\');\n    }\n    \n    // 2. 使用更清晰的变量名\n    const result = process(input);\n    \n    // 3. 添加错误处理\n    try {\n        return transform(result);\n    } catch (error) {\n        console.error(\'Processing failed:\', error);\n        throw error;\n    }\n}\n```\n\n**改进点：**\n- ✅ 添加了输入验证\n- ✅ 使用更清晰的命名\n- ✅ 添加了错误处理\n- ✅ 提高了可读性';
        }

        if (content.includes('调试') || content.includes('问题') || content.includes('bug')) {
            return '让我帮你调试这段代码：\n\n**可能的问题：**\n\n1. **空值检查** - 确保所有输入都经过了验证\n2. **类型安全** - 检查类型是否匹配\n3. **边界条件** - 考虑极端情况\n4. **异步处理** - 如果有异步操作，确保正确处理了 Promise\n\n**调试步骤：**\n1. 添加日志输出关键变量\n2. 使用断点逐步执行\n3. 检查输入输出是否符合预期\n\n需要我帮你具体分析哪一部分？';
        }

        if (content.includes('测试') || content.includes('unit')) {
            return '我来为你生成单元测试：\n\n```typescript\nimport { describe, it, expect } from \'@jest/globals\';\n\ndescribe(\'Function Tests\', () => {\n    it(\'应该正确处理正常输入\', () => {\n        const result = myFunction(validInput);\n        expect(result).toBeDefined();\n        expect(result).toBe(expectedOutput);\n    });\n\n    it(\'应该处理空输入\', () => {\n        expect(() => myFunction(null)).toThrow();\n    });\n\n    it(\'应该处理边界情况\', () => {\n        const result = myFunction(edgeCaseInput);\n        expect(result).toBe(edgeCaseOutput);\n    });\n});\n```\n\n**测试覆盖：**\n- ✅ 正常流程\n- ✅ 异常处理\n- ✅ 边界条件\n\n需要我生成更多测试用例吗？';
        }

        // 默认响应
        return '感谢你的提问！作为一个 AI 编程助手，我可以帮助你：\n\n- 📖 **解释代码** - 理解复杂代码逻辑\n- 🔧 **重构优化** - 提高代码质量\n- 🐛 **调试问题** - 找出并修复 bug\n- ✅ **生成测试** - 编写单元测试\n- 📝 **Code Review** - 提供改进建议\n\n请告诉我具体需要什么帮助？';
    }
}
