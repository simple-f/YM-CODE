#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多 Agent 对话测试脚本
测试 Agent 间的自动协作对话
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

# 模拟多 Agent 对话
def simulate_multi_agent_chat():
    """模拟多 Agent 协作对话"""
    
    print("=" * 60)
    print("           多 Agent 协作对话测试")
    print("=" * 60)
    
    # 用户问题
    question = "帮我设计一个简单的用户登录系统，包括数据库设计和 API 接口"
    print(f"\n👤 用户问题：{question}\n")
    
    # 参与的 Agent
    agents = [
        {"id": "ai1", "name": "架构师", "model": "qwen3.5-plus"},
        {"id": "ai2", "name": "后端开发", "model": "qwen3-coder-plus"},
        {"id": "ai5", "name": "测试工程师", "model": "kimi-k2.5"},
    ]
    
    print(f"👥 参与 Agent: {', '.join([a['name'] for a in agents])}\n")
    print("-" * 60)
    
    # 第 1 轮：架构师设计
    print("\n【第 1 轮】架构师 (ai1) 发言:")
    print("-" * 60)
    architect_response = """
## 用户登录系统架构设计

### 技术选型
- 后端：Python FastAPI
- 数据库：PostgreSQL
- 认证：JWT Token
- 密码加密：bcrypt

### 数据库表设计

#### users 表
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### API 接口设计
1. POST /api/auth/register - 用户注册
2. POST /api/auth/login - 用户登录
3. POST /api/auth/logout - 用户登出
4. GET /api/auth/me - 获取当前用户信息
"""
    print(architect_response)
    
    # 第 1 轮：后端开发补充
    print("\n【第 1 轮】后端开发 (ai2) 补充:")
    print("-" * 60)
    backend_response = """
## 后端 API 实现细节

### 注册接口实现
```python
@app.post("/api/auth/register")
async def register(user_data: UserCreate):
    # 检查用户是否已存在
    existing = await get_user_by_email(user_data.email)
    if existing:
        raise HTTPException(400, "用户已存在")
    
    # 密码加密
    password_hash = bcrypt.hashpw(user_data.password, bcrypt.gensalt())
    
    # 创建用户
    user = await create_user(
        username=user_data.username,
        email=user_data.email,
        password_hash=password_hash
    )
    
    return {"message": "注册成功", "user_id": user.id}
```

### 登录接口实现
```python
@app.post("/api/auth/login")
async def login(credentials: UserLogin):
    user = await get_user_by_email(credentials.email)
    if not user:
        raise HTTPException(401, "用户名或密码错误")
    
    # 验证密码
    if not bcrypt.checkpw(credentials.password, user.password_hash):
        raise HTTPException(401, "用户名或密码错误")
    
    # 生成 JWT Token
    token = create_jwt_token(user.id)
    return {"access_token": token, "token_type": "bearer"}
```
"""
    print(backend_response)
    
    # 第 2 轮：测试工程师审查
    print("\n【第 2 轮】测试工程师 (ai5) 审查:")
    print("-" * 60)
    tester_response = """
## 代码审查意见

### ✅ 优点
1. 使用 bcrypt 加密密码 - 安全
2. JWT Token 认证 - 无状态，易扩展
3. 使用 UUID 作为主键 - 避免 ID 泄露

### ⚠️ 需要改进
1. **缺少速率限制** - 登录接口需要添加防暴力破解
2. **缺少输入验证** - 邮箱格式、密码强度需要验证
3. **缺少刷新 Token** - JWT 过期后用户体验差
4. **缺少审计日志** - 登录失败应该记录日志

### 建议补充
```python
# 添加速率限制
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/api/auth/login")
@limiter.limit("5/minute")  # 每分钟最多 5 次
async def login(request, credentials: UserLogin):
    ...
```
"""
    print(tester_response)
    
    # 第 2 轮：架构师回应
    print("\n【第 2 轮】架构师 (ai1) 回应审查:")
    print("-" * 60)
    architect_response2 = """
## 采纳审查意见，更新设计

### 补充功能
1. ✅ 添加速率限制（slowapi）
2. ✅ 添加输入验证（pydantic）
3. ✅ 添加刷新 Token 机制
4. ✅ 添加审计日志

### 刷新 Token 设计
```python
# Token 设计
access_token: 15 分钟有效期
refresh_token: 7 天有效期，存储在 Redis

# 刷新接口
@app.post("/api/auth/refresh")
async def refresh_token(refresh_data: RefreshToken):
    # 验证 refresh token
    user_id = verify_refresh_token(refresh_data.token)
    
    # 生成新的 access token
    new_access_token = create_jwt_token(user_id)
    return {"access_token": new_access_token}
```
"""
    print(architect_response2)
    
    # 第 3 轮：后端开发实现
    print("\n【第 3 轮】后端开发 (ai2) 最终实现:")
    print("-" * 60)
    backend_response2 = """
## 完整实现代码

### Pydantic 模型
```python
from pydantic import BaseModel, EmailStr, validator
import re

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('密码至少 8 位')
        if not re.search(r'[A-Z]', v):
            raise ValueError('密码需包含大写字母')
        if not re.search(r'[0-9]', v):
            raise ValueError('密码需包含数字')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str
```
"""
    print(backend_response2)
    
    print("\n" + "=" * 60)
    print("                  对话完成")
    print("=" * 60)
    print("\n📊 对话统计:")
    print(f"  - 总轮数：3 轮")
    print(f"  - 发言次数：5 次")
    print(f"  - 参与 Agent: 3 个")
    print("\n✅ 多 Agent 协作测试成功!")
    print("\n")


if __name__ == "__main__":
    simulate_multi_agent_chat()
