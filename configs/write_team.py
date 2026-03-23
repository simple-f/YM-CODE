# -*- coding: utf-8 -*-
import json

data = {
    "name": "全栈开发团队",
    "description": "多模型协作的全栈开发团队，每个 Agent 使用最适合的模型",
    "created_at": "2026-03-19",
    "agents": [
        {"id": "ai1", "name": "架构师", "role": "system", "description": "负责系统架构设计和技术选型", "model": "qwen3.5-plus"},
        {"id": "ai2", "name": "后端开发", "role": "developer", "description": "负责后端 API 开发和数据库设计", "model": "qwen3-coder-plus"},
        {"id": "ai3", "name": "前端开发", "role": "developer", "description": "负责前端界面和用户体验", "model": "qwen3-coder-next"},
        {"id": "ai4", "name": "全栈开发", "role": "developer", "description": "负责全栈开发和集成", "model": "glm-5"},
        {"id": "ai5", "name": "测试工程师", "role": "reviewer", "description": "负责代码审查和质量保证", "model": "kimi-k2.5"},
        {"id": "ai6", "name": "技术顾问", "role": "advisor", "description": "提供技术咨询和最佳实践建议", "model": "qwen3-max-2026-01-23"},
        {"id": "ai7", "name": "产品顾问", "role": "advisor", "description": "提供产品设计和用户体验建议", "model": "MiniMax-M2.5"}
    ]
}

with open('team.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Written successfully")

# Verify
with open('team.json', 'r', encoding='utf-8') as f:
    verify = json.load(f)
print(f"Verified: {verify['name']}")
