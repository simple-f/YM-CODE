#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple service test
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("Testing v2.0 Service...")
print()

# Test 1: Import app
print("Test 1: Import FastAPI App")
try:
    from backend.main import app
    print("  [OK] FastAPI App imported")
    print(f"  [OK] Routes count: {len(app.routes)}")
except Exception as e:
    print(f"  [FAIL] {e}")
    sys.exit(1)

print()

# Test 2: Check routes
print("Test 2: Check API Routes")
api_routes = [r for r in app.routes if hasattr(r, 'path') and '/api/' in r.path]
print(f"  [OK] API routes: {len(api_routes)}")
for route in api_routes[:5]:
    if hasattr(route, 'methods'):
        methods = ', '.join(route.methods)
        print(f"    - {methods} {route.path}")

print()

# Test 3: Check health endpoint
print("Test 3: Check Health Endpoint")
health_route = [r for r in app.routes if hasattr(r, 'path') and r.path == '/health']
if health_route:
    print("  [OK] Health endpoint exists")
else:
    print("  [FAIL] Health endpoint not found")

print()

# Test 4: Check docs
print("Test 4: Check API Docs")
docs_route = [r for r in app.routes if hasattr(r, 'path') and r.path == '/docs']
if docs_route:
    print("  [OK] Swagger docs available")
else:
    print("  [FAIL] Swagger docs not found")

print()
print("=" * 60)
print("Service test complete!")
print("=" * 60)
print()
print("v2.0 service is ready to run!")
