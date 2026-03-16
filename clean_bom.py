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
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    # Write back without BOM
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'Cleaned BOM: {filename}')

print('Done!')
