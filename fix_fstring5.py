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
        content = f.read()
    
    # Replace the problematic line entirely
    old_line = '''        print(f"\\n📊 测试结果：{self.passed}/{total} 通过 ({rate:.1f}%%)")'''
    new_line = '''        print(f"\\n📊 测试结果：{self.passed}/{total} 通过 ({rate:.1f})%")'''
    
    # Try different variations
    content = content.replace('{rate:.1f}%%', '{rate:.1f}')
    content = content.replace('}" + "%"')', '}" + "%")')
    content = content.replace(')" + "%")"', ')" + "%")')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'Fixed: {filename}')

print('Done!')
