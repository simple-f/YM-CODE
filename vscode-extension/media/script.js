/**
 * YM-CODE Webview Script
 */

(function() {
    const vscode = acquireVsCodeApi();
    
    const messagesDiv = document.getElementById('messages');
    const input = document.getElementById('input');
    const sendButton = document.getElementById('send');
    const clearButton = document.getElementById('clear');

    let messageHistory = [];

    /**
     * 发送消息
     */
    function sendMessage() {
        const content = input.value.trim();
        if (!content) return;

        vscode.postMessage({
            type: 'sendMessage',
            content
        });

        input.value = '';
        input.style.height = 'auto';
    }

    /**
     * 添加消息到界面
     */
    function addMessage(role, content) {
        // 移除欢迎消息
        const welcomeMsg = messagesDiv.querySelector('.welcome-message');
        if (welcomeMsg) {
            welcomeMsg.remove();
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = content;
        
        messageDiv.appendChild(contentDiv);
        messagesDiv.appendChild(messageDiv);
        
        // 滚动到底部
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    /**
     * 显示加载状态
     */
    function showLoading() {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message assistant loading';
        loadingDiv.id = 'loading-message';
        loadingDiv.textContent = '思考中...';
        messagesDiv.appendChild(loadingDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    /**
     * 移除加载状态
     */
    function removeLoading() {
        const loadingMsg = document.getElementById('loading-message');
        if (loadingMsg) {
            loadingMsg.remove();
        }
    }

    /**
     * 清空历史
     */
    function clearHistory() {
        messageHistory = [];
        messagesDiv.innerHTML = `
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
        `;
        vscode.postMessage({ type: 'clearHistory' });
    }

    // 事件监听
    sendButton.addEventListener('click', sendMessage);

    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
            e.preventDefault();
            sendMessage();
        }
    });

    clearButton.addEventListener('click', clearHistory);

    // 自动调整输入框高度
    input.addEventListener('input', () => {
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 120) + 'px';
    });

    // 监听来自扩展的消息
    window.addEventListener('message', (event) => {
        const message = event.data;
        
        switch (message.type) {
            case 'addMessage':
                addMessage('user', message.content);
                showLoading();
                break;
            
            case 'updateMessages':
                removeLoading();
                // 清空并重新渲染所有消息
                const welcomeMsg = messagesDiv.querySelector('.welcome-message');
                if (welcomeMsg) {
                    welcomeMsg.remove();
                }
                messagesDiv.innerHTML = '';
                message.messages.forEach(msg => {
                    addMessage(msg.role, msg.content);
                });
                break;
            
            case 'clearHistory':
                clearHistory();
                break;
        }
    });

    // 初始化
    console.log('YM-CODE Webview 已初始化');
})();
