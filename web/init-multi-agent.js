// 多 Agent 协作页面初始化脚本

const API_BASE = '';

// 当前状态
let currentWorkspace = null;
let allAgents = [];
let selectedAgents = new Set();
let chatHistory = [];

// 初始化
document.addEventListener('DOMContentLoaded', async () => {
    await loadTeam();
    initForm();
});

// 加载 Agent 团队
async function loadTeam() {
    try {
        const resp = await fetch(`${API_BASE}/api/team/list`);
        const data = await resp.json();
        
        allAgents = data.team?.agents || [];
        
        const agentList = document.getElementById('agentList');
        if (allAgents.length === 0) {
            agentList.innerHTML = `
                <div style="text-align: center; padding: 40px; color: #888;">
                    暂无 Agent
                    <br>
                    <small>请检查 configs/team.json 配置</small>
                </div>
            `;
            return;
        }
        
        // 渲染 Agent 列表
        agentList.innerHTML = allAgents.map((agent, index) => `
            <div class="agent-card" onclick="toggleAgent('${agent.id}')" data-id="${agent.id}">
                <div class="agent-avatar">${getAgentAvatar(index)}</div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong>${escapeHtml(agent.name)}</strong>
                    <span class="status-badge" style="background: #4ade80; color: #1a1a2e;">✓</span>
                </div>
                <div style="color: #888; font-size: 12px; margin-top: 5px;">
                    ${agent.model}
                </div>
            </div>
        `).join('');
        
        // 默认选择所有 Agent
        allAgents.forEach(agent => {
            selectedAgents.add(agent.id);
        });
        updateAgentSelection();
        
    } catch (error) {
        console.error('加载 Agent 失败:', error);
    }
}

function toggleAgent(agentId) {
    if (selectedAgents.has(agentId)) {
        if (selectedAgents.size > 1) {
            selectedAgents.delete(agentId);
        } else {
            alert('至少需要一个 Agent 参与对话');
            return;
        }
    } else {
        selectedAgents.add(agentId);
    }
    updateAgentSelection();
}

function updateAgentSelection() {
    document.querySelectorAll('.agent-card').forEach(card => {
        const agentId = card.dataset.id;
        if (selectedAgents.has(agentId)) {
            card.classList.add('active');
        } else {
            card.classList.remove('active');
        }
    });
}

function getAgentAvatar(index) {
    const avatars = ['🎨', '💻', '🎨', '🔧', '✅', '💡', '📊'];
    return avatars[index % avatars.length];
}

function initForm() {
    const form = document.getElementById('chatForm');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await sendMessage();
        });
    }
}

async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message) return;
    if (selectedAgents.size === 0) {
        alert('请至少选择一个 Agent');
        return;
    }
    
    // 添加用户消息
    addMessage(message, 'user');
    input.value = '';
    
    // 清空欢迎消息
    const chatContainer = document.getElementById('chatContainer');
    if (chatContainer.querySelector('h3')) {
        chatContainer.innerHTML = '';
    }
    
    // 调用真实 API
    updateStatus('thinking', '思考中...');
    
    const participatingAgents = allAgents.filter(a => selectedAgents.has(a.id));
    
    // 依次调用每个 Agent
    for (const agent of participatingAgents) {
        highlightAgent(agent.id);
        updateStatus('thinking', `${agent.name} 正在思考...`);
        
        try {
            const resp = await fetch(`${API_BASE}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    agent_id: agent.id,
                    agent_name: agent.name
                })
            });
            
            const data = await resp.json();
            await sleep(500);
            addMessage(data.response || '...', 'agent', agent);
        } catch (error) {
            addMessage(`错误：${error.message}`, 'agent', agent);
        }
    }
    
    clearAgentHighlight();
    updateStatus('ready', '就绪');
    addSummaryMessage(participatingAgents);
}

function addMessage(content, type, agent = null) {
    const container = document.getElementById('chatContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    if (type === 'agent' && agent) {
        const avatar = getAgentAvatar(allAgents.findIndex(a => a.id === agent.id));
        messageDiv.innerHTML = `
            <div style="width: 50px; height: 50px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; font-size: 24px; flex-shrink: 0;">
                ${avatar}
            </div>
            <div>
                <div class="message-sender" style="color: #667eea;">${escapeHtml(agent.name)}</div>
                <div class="message-content">${formatMessage(content)}</div>
            </div>
        `;
    } else if (type === 'user') {
        messageDiv.innerHTML = `
            <div class="message-content" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">${escapeHtml(content)}</div>
        `;
    }
    
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}

function addSummaryMessage(agents) {
    const container = document.getElementById('chatContainer');
    const summaryDiv = document.createElement('div');
    summaryDiv.style.cssText = 'text-align: center; padding: 20px; color: #888; border-top: 1px solid #0f3460; margin-top: 20px;';
    summaryDiv.innerHTML = `
        <p>🎉 本轮讨论完成！共 ${agents.length} 位 Agent 参与</p>
        <p style="font-size: 13px; margin-top: 10px;">
            参与者：${agents.map(a => escapeHtml(a.name)).join('、')}
        </p>
    `;
    container.appendChild(summaryDiv);
}

function highlightAgent(agentId) {
    clearAgentHighlight();
    const card = document.querySelector(`.agent-card[data-id="${agentId}"]`);
    if (card) {
        card.classList.add('speaking');
    }
}

function clearAgentHighlight() {
    document.querySelectorAll('.agent-card').forEach(card => {
        card.classList.remove('speaking');
    });
}

function updateStatus(status, text) {
    const dot = document.getElementById('statusDot');
    const textEl = document.getElementById('statusText');
    
    dot.className = `status-dot ${status === 'thinking' ? 'thinking' : ''}`;
    textEl.textContent = text;
}

function formatMessage(text) {
    return escapeHtml(text)
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
