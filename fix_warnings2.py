#!/usr/bin/env python3
import os

# Fix test_mcp_client_v2.py - add pytestmark back and remove from non-async tests
filepath = 'tests/test_mcp_client_v2.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Add pytestmark at the top (after imports)
if 'pytestmark = pytest.mark.asyncio' not in content:
    content = content.replace(
        'logger = get_logger(__name__)',
        'logger = get_logger(__name__)\n\n# Mark all async tests\npytestmark = pytest.mark.asyncio'
    )

# Remove the bad replacements we made
content = content.replace(
    '# Non-async test - no asyncio needed\n@pytest.mark.asyncio  # Removed: this is not async\n',
    ''
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed test_mcp_client_v2.py')
print('Done!')
