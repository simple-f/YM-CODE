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
        lines = f.readlines()
    
    new_lines = []
    skip_until_blank = False
    in_results_tracker = False
    
    for i, line in enumerate(lines):
        # Detect start of ResultsTracker class
        if 'class ResultsTracker:' in line:
            in_results_tracker = True
            skip_until_blank = True
            continue
        
        # Skip lines while in ResultsTracker class
        if skip_until_blank:
            if line.strip() == '' or (line.startswith('@') and 'fixture' in line):
                skip_until_blank = False
                in_results_tracker = False
            continue
        
        # Skip summary method that has the problematic print
        if 'def summary(self):' in line:
            # Skip this method until next method or end of class
            continue
        
        # Remove the @pytest.fixture for results (now in conftest)
        if '@pytest.fixture' in line and i+1 < len(lines) and 'def results' in lines[i+1]:
            continue
        if 'def results' in line and '()->' in line or '-> ResultsTracker' in line:
            continue
        
        new_lines.append(line)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f'Cleaned: {filename}')

print('Done!')
