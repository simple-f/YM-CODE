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
    
    # Replace the broken pattern with correct string concatenation
    # From: print(f"...({rate:.1f}%%)")
    # To:   print(f"...({rate:.1f})" + "%")
    content = re.sub(
        r'print\(f"(.*?)(\{rate:[^}]+\})%%"\)',
        r'print(f"\1\2") + "%"',
        content
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'Fixed: {filename}')

print('Done!')
