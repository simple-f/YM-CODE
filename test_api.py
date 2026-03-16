#!/usr/bin/env python3
"""API 测试脚本"""

import requests
import json

API_BASE = 'http://localhost:18770/api'

print('=' * 60)
print('YM-CODE v0.6.0 API 测试')
print('=' * 60)
print()

# 测试 1: 技能列表
print('测试 1: 获取技能列表...')
try:
    response = requests.get(f'{API_BASE}/skills/list')
    if response.status_code == 200:
        data = response.json()
        skills = data.get('skills', [])
        print(f'  [OK] 成功获取 {len(skills)} 个技能')
        for skill in skills[:3]:
            name = skill.get('name', 'Unknown')
            role = skill.get('role', 'unknown')
            enabled = skill.get('enabled', True)
            print(f'    - {name} ({role}) - 已启用：{enabled}')
    else:
        print(f'  [FAIL] 失败：{response.status_code}')
except Exception as e:
    print(f'  [FAIL] 错误：{e}')

print()

# 测试 2: 工作区列表
print('测试 2: 获取工作区列表...')
try:
    response = requests.get(f'{API_BASE}/workspace/list')
    if response.status_code == 200:
        data = response.json()
        workspaces = data.get('workspaces', [])
        print(f'  [OK] 当前有 {len(workspaces)} 个工作区')
    else:
        print(f'  [FAIL] 失败：{response.status_code}')
except Exception as e:
    print(f'  [FAIL] 错误：{e}')

print()

# 测试 3: 创建工作区
print('测试 3: 创建工作区...')
try:
    response = requests.post(f'{API_BASE}/workspace/create', json={
        'name': '测试项目',
        'description': 'AI 测试创建的工作区'
    })
    if response.status_code == 200:
        workspace = response.json()
        ws_name = workspace.get('name', 'Unknown')
        ws_id = workspace.get('id', 'Unknown')
        print(f'  [OK] 工作区创建成功：{ws_name} (ID: {ws_id})')
    else:
        print(f'  [FAIL] 失败：{response.status_code}')
except Exception as e:
    print(f'  [FAIL] 错误：{e}')

print()

# 测试 4: Agent 列表
print('测试 4: 获取可用 Agent...')
try:
    from ymcode.agents.base import get_agent_registry
    registry = get_agent_registry()
    agents = registry.list_agents()
    print(f'  [OK] 注册表中有 {len(agents)} 个 Agent')
    for agent in agents[:3]:
        name = agent.get('name', 'Unknown')
        role = agent.get('role', 'unknown')
        print(f'    - {name} ({role})')
except Exception as e:
    print(f'  [FAIL] 错误：{e}')

print()
print('=' * 60)
print('API 测试完成')
print('=' * 60)
