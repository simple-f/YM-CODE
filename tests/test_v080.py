#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v0.8.0 测试套件

测试所有新增功能
"""

import sys
import asyncio
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from ymcode.skills.git_integration import GitIntegrationSkill
from ymcode.skills.batch_project import BatchProjectSkill


class TestResults:
    """测试结果追踪"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def record(self, name: str, passed: bool, message: str = ""):
        """记录测试结果"""
        self.tests.append({
            'name': name,
            'passed': passed,
            'message': message
        })
        if passed:
            self.passed += 1
            print(f"  ✅ {name}")
        else:
            self.failed += 1
            print(f"  ❌ {name}: {message}")
    
    def summary(self):
        """打印总结"""
        total = self.passed + self.failed
        rate = (self.passed / total * 100) if total > 0 else 0
        print(f"\n{'='*60}")
        print(f"测试结果：{self.passed}/{total} 通过 ({rate:.1f}%)")
        print(f"{'='*60}")
        return self.failed == 0


async def test_git_integration(results: TestResults):
    """测试 Git 集成技能"""
    print(f"\n{'='*60}")
    print("测试 1: Git 集成技能")
    print(f"{'='*60}")
    
    try:
        # 测试 1: 创建技能
        skill = GitIntegrationSkill()
        results.record("创建 Git 集成技能", True)
        
        # 测试 2: 检查 Git 可用性
        if skill.git_available:
            results.record("Git 已安装", True)
        else:
            results.record("Git 已安装", False, "Git 未安装，跳过后续测试")
            return
        
        # 测试 3: 获取状态
        result = await skill.execute({
            'action': 'status',
            'path': '.'
        })
        results.record("获取 Git 状态", result.get('success', False))
        
        # 测试 4: 技能属性
        results.record("技能描述", bool(skill.description))
        results.record("技能能力", len(skill.capabilities) > 0)
        
    except Exception as e:
        results.record("Git 集成测试", False, str(e))


async def test_batch_project(results: TestResults):
    """测试批量项目处理技能"""
    print(f"\n{'='*60}")
    print("测试 2: 批量项目处理技能")
    print(f"{'='*60}")
    
    try:
        # 测试 1: 创建技能
        skill = BatchProjectSkill()
        results.record("创建批量项目处理技能", True)
        
        # 测试 2: 分析当前项目
        result = await skill.execute({
            'action': 'analyze',
            'path': '.',
            'language': 'python',
            'pattern': '*.py'
        })
        
        if result.get('success'):
            summary = result.get('summary', {})
            results.record("分析项目结构", True, 
                          f"文件数：{summary.get('total_files', 0)}")
        else:
            results.record("分析项目结构", False, 
                          result.get('error', '未知错误'))
        
        # 测试 3: 技能属性
        results.record("技能描述", bool(skill.description))
        results.record("技能能力", len(skill.capabilities) > 0)
        
        # 测试 4: 依赖分析
        result = await skill.execute({
            'action': 'dependencies',
            'path': '.',
            'language': 'python'
        })
        results.record("依赖分析", result.get('success', False))
        
    except Exception as e:
        results.record("批量项目处理测试", False, str(e))


async def test_vscode_plugin(results: TestResults):
    """测试 VSCode 插件配置"""
    print(f"\n{'='*60}")
    print("测试 3: VSCode 插件配置")
    print(f"{'='*60}")
    
    try:
        # 测试 1: 检查插件文件
        vscode_dir = Path(__file__).parent.parent / 'extensions' / 'vscode'
        
        files_exist = [
            vscode_dir / 'package.json',
            vscode_dir / 'tsconfig.json',
            vscode_dir / 'src' / 'extension.ts',
            vscode_dir / 'src' / 'client.ts',
            vscode_dir / 'src' / 'analyzer.ts',
        ]
        
        all_exist = all(f.exists() for f in files_exist)
        results.record("VSCode 插件文件完整", all_exist)
        
        # 测试 2: 检查 package.json
        if (vscode_dir / 'package.json').exists():
            import json
            with open(vscode_dir / 'package.json', 'r', encoding='utf-8') as f:
                package = json.load(f)
            
            results.record("package.json 有效", bool(package.get('name')))
            results.record("插件命令", len(package.get('contributes', {}).get('commands', [])) > 0)
        
    except Exception as e:
        results.record("VSCode 插件测试", False, str(e))


async def main():
    """主测试函数"""
    print(f"\n{'#'*60}")
    print("# YM-CODE v0.8.0 测试套件")
    print(f"{'#'*60}")
    
    results = TestResults()
    
    # 运行测试
    await test_git_integration(results)
    await test_batch_project(results)
    await test_vscode_plugin(results)
    
    # 总结
    success = results.summary()
    
    if success:
        print("\n✅ 所有测试通过！v0.8.0 可以发布！")
    else:
        print(f"\n⚠️ {results.failed} 个测试失败，需要修复")
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
