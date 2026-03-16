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
    
    # Fix f-string: {rate:.1f}% -> {rate:.1f}"%"
    # The % sign needs to be outside f-string or escaped
    content = re.sub(r'\{rate:[^}]+\}%', r'{rate:.1f}"%"', content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'Fixed: {filename}')

print('Done!')
