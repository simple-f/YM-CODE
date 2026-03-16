#!/usr/bin/env python3
import os

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
        lines = f.readlines()
    
    new_lines = []
    for line in lines:
        # Fix the f-string with %%
        if '{rate:.1f}%%' in line:
            line = line.replace('{rate:.1f}%%', '{rate:.1f})" + "%"')
            # Also need to fix the opening parenthesis
            line = line.replace('f"\\n📊 测试结果：', 'f"\\n📊 测试结果：')
        new_lines.append(line)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f'Fixed: {filename}')

print('Done!')
