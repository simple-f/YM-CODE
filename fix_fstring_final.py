#!/usr/bin/env python3
import os
import re

files = [
    'test_cli.py',
    'test_lsp_completion.py', 
    'test_mcp_client_v2.py',
    'test_memory.py',
    'test_project_context.py',
    'test_skills.py',
    'test_tools_integration.py'
]

for filename in files:
    filepath = os.path.join('tests', filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace all problematic f-strings with .format()
    def replace_fstring(match):
        return 'print("\\n📊 测试结果：{}/{} 通过 ({:.1f}%)".format(self.passed, total, rate))'
    
    content = re.sub(
        r'print\(f"[^"]*测试结果[^"]*\{rate:[^}]*\}[^"]*"\)',
        replace_fstring,
        content
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'Fixed: {filename}')

print('Done!')
