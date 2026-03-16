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
    with open(filepath, 'rb') as f:
        content = f.read()
    
    # Find the summary method and replace the print line
    # Look for the pattern in bytes
    old_pattern = b'print(f"\\n'
    new_pattern = b'print("\\n'
    
    content = content.replace(old_pattern, new_pattern)
    
    # Also replace the closing
    old_pattern2 = b'rate:.1f}%)")'
    new_pattern2 = b'rate:.1f}%)" +  "")'
    
    content = content.replace(old_pattern2, new_pattern2)
    
    with open(filepath, 'wb') as f:
        f.write(content)
    
    print(f'Fixed: {filename}')

print('Done!')
