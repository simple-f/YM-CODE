#!/usr/bin/env python3
"""
整理 Git 仓库文件结构

移动临时文件到合适位置
"""

import shutil
from pathlib import Path

root = Path(__file__).parent

# 创建目录
scripts_dir = root / 'scripts'
scripts_dir.mkdir(exist_ok=True)

reports_dir = root / 'reports'
reports_dir.mkdir(exist_ok=True)

# 移动测试脚本到 scripts/
test_scripts = [
    'check_models.py',
    'test-api-connection.py',
    'test-api-response.py',
    'test-commands.py',
    'test-full.py',
    'test-llm.py',
    'test-session.py',
    'test_api_simple.py',
    'test_coding.py',
    'test_full_integration.py',
    'test_mcp.py',
    'test_memory_store.py',
    'test_multi_agent.py',
    'test_simple.py',
    'test_skills_marketplace.py',
    'test_skills_mcp.py',
    'test_tool_call.py',
    'test_ymcode.py',
]

for script in test_scripts:
    src = root / script
    if src.exists():
        dst = scripts_dir / script
        shutil.move(str(src), str(dst))
        print(f"✅ 移动 {script} → scripts/")

# 移动报告文件到 reports/
report_files = [
    'AGENT_USAGE.md',
    'BRAND_IDENTITY.md',
    'BUG_FIX_REPORT.md',
    'BUG_REPORT.md',
    'CODE_REVIEW_REPORT.md',
    'COMPARISON.md',
    'COMPARISON_ANALYSIS.md',
    'CONFIG_GUIDE.md',
    'CONTRIBUTING.md',
    'CROSS_PLATFORM.md',
    'DOCS_COMPLETE_REPORT.md',
    'FEATURES_SUMMARY.md',
    'FEATURE_COMPLETION_REPORT.md',
    'FINAL_CHECK_REPORT.md',
    'FINAL_FIX_CONFIRMATION.md',
    'FINAL_REVIEW_CONFIRMATION.md',
    'FINAL_SUMMARY.md',
    'FINAL_TEST_REPORT.md',
    'FIX_REPORT.md',
    'LLM-SETUP.md',
    'LOCAL_TEAM_SETUP.md',
    'MCP_GUIDE.md',
    'MCP_QUICKSTART.md',
    'MCP_SETUP.md',
    'MISSING_ITEMS.md',
    'MISSING_TEAM_FEATURES.md',
    'MODELS_GUIDE.md',
    'MULTI_AGENT_DESIGN.md',
    'PROJECT_SUMMARY.md',
    'RELEASE_FINAL_v0.5.0.md',
    'RELEASE_v0.5.0.md',
    'REVIEW_REQUEST_CLARIFICATION.md',
    'ROADMAP.md',
    'SECURITY.md',
    'SESSION_OPTIMIZATION.md',
    'SESSION_SUMMARY.md',
    'SETUP.md',
    'setup_mcp.py',
    'SKILLS_MARKETPLACE.md',
    'SKILLS_MCP_INTEGRATION.md',
    'TASKS.md',
    'TEAM_COLLABORATION.md',
    'TEAM_FEATURES.md',
    'TEAM_FEATURE_COMPLETE.md',
    'TEST_ENV_SETUP.md',
    'TEST_FIX_REPORT_v0.3.4.md',
    'TEST_REPORT.md',
]

for report in report_files:
    src = root / report
    if src.exists():
        dst = reports_dir / report
        shutil.move(str(src), str(dst))
        print(f"✅ 移动 {report} → reports/")

print("\n整理完成！")
