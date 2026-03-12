#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Skill Tests - 记忆技能测试
"""

import pytest
from ymcode.skills.memory import MemorySkill


class TestMemorySkill:
    """记忆技能测试"""
    
    @pytest.mark.asyncio
    async def test_init(self):
        """测试初始化"""
        skill = MemorySkill()
        assert skill is not None
        assert skill.name == "memory"
        assert skill.description is not None
    
    @pytest.mark.asyncio
    async def test_save_memory(self, tmp_path):
        """测试保存记忆"""
        skill = MemorySkill()
        result = await skill.execute({
            "action": "save",
            "session_id": "test_session",
            "content": "test memory content"
        })
        
        assert result["success"] is True
        assert "memory_id" in result
        assert result["session_id"] == "test_session"
    
    @pytest.mark.asyncio
    async def test_load_memory(self, tmp_path):
        """测试加载记忆"""
        skill = MemorySkill()
        
        # 先保存
        await skill.execute({
            "action": "save",
            "session_id": "test_load",
            "content": "test content"
        })
        
        # 再加载
        result = await skill.execute({
            "action": "load",
            "session_id": "test_load"
        })
        
        assert result["success"] is True
        assert "memories" in result
        assert result["session_id"] == "test_load"
    
    @pytest.mark.asyncio
    async def test_search_memory(self, tmp_path):
        """测试搜索记忆"""
        skill = MemorySkill()
        
        # 保存一些记忆
        await skill.execute({
            "action": "save",
            "session_id": "test_search",
            "content": "python programming is great"
        })
        
        # 搜索
        result = await skill.execute({
            "action": "search",
            "query": "python"
        })
        
        assert result["success"] is True
        assert "results" in result
        assert result["query"] == "python"
    
    @pytest.mark.asyncio
    async def test_forget_memory(self, tmp_path):
        """测试忘记记忆"""
        skill = MemorySkill()
        
        # 先保存
        save_result = await skill.execute({
            "action": "save",
            "session_id": "test_forget",
            "content": "temporary memory"
        })
        
        memory_id = save_result["memory_id"]
        
        # 忘记
        result = await skill.execute({
            "action": "forget",
            "memory_id": memory_id
        })
        
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_clear_memory(self, tmp_path):
        """测试清空记忆"""
        skill = MemorySkill()
        
        # 清空短期记忆
        result = await skill.execute({
            "action": "clear",
            "memory_type": "short"
        })
        
        assert result["success"] is True
        assert result["type"] == "short"
    
    @pytest.mark.asyncio
    async def test_get_status(self, tmp_path):
        """测试获取状态"""
        skill = MemorySkill()
        result = await skill.execute({
            "action": "status"
        })
        
        assert isinstance(result, dict)
        assert "short_term_count" in result
        assert "long_term_count" in result
    
    @pytest.mark.asyncio
    async def test_invalid_action(self, tmp_path):
        """测试无效操作"""
        skill = MemorySkill()
        result = await skill.execute({
            "action": "invalid_action"
        })
        
        assert "error" in result
        assert "无效操作" in result["error"] or "未知操作" in result["error"]
    
    @pytest.mark.asyncio
    async def test_memory_persistence(self, tmp_path):
        """测试记忆持久化"""
        skill = MemorySkill()
        
        # 保存记忆
        await skill.execute({
            "action": "save",
            "session_id": "persist_test",
            "content": "persistent memory"
        })
        
        # 验证长期记忆文件存在
        data_file = skill.data_dir / "long_term_memory.json"
        assert data_file.exists()


class TestMemorySkillInputSchema:
    """记忆技能输入 Schema 测试"""
    
    def test_input_schema(self):
        """测试输入 schema"""
        skill = MemorySkill()
        schema = skill.get_input_schema()
        
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "action" in schema["properties"]
        assert schema["required"] == ["action"]
        
        # 检查 action 的枚举值
        action_enum = schema["properties"]["action"]["enum"]
        assert "save" in action_enum
        assert "load" in action_enum
        assert "search" in action_enum
        assert "forget" in action_enum
        assert "clear" in action_enum
        assert "status" in action_enum
