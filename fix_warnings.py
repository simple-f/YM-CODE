#!/usr/bin/env python3
import os

# Fix test_mcp_client_v2.py - remove async mark from non-async functions
filepath = 'tests/test_mcp_client_v2.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Add comment before non-async tests to explain they don't need asyncio
content = content.replace(
    'def test_server_registry(results: TestResults):',
    '# Non-async test - no asyncio needed\n@pytest.mark.asyncio  # Removed: this is not async\ndef test_server_registry(results: TestResults):'
)

content = content.replace(
    'def test_prompts(results: TestResults):',
    '# Non-async test - no asyncio needed\n@pytest.mark.asyncio  # Removed: this is not async\ndef test_prompts(results: TestResults):'
)

# Actually, just remove the global pytestmark
content_lines = content.split('\n')
new_lines = [line for line in content_lines if not line.strip().startswith('pytestmark = pytest.mark.asyncio')]
content = '\n'.join(new_lines)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed test_mcp_client_v2.py')
print('Done!')
