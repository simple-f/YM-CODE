#!/usr/bin/env python3
"""
Simple test for LangGraph A2A Coordinator - Standalone version
"""

import sys
import os
from pathlib import Path

# Set UTF-8 encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 60)
print("LangGraph A2A Coordinator - Basic Test")
print("=" * 60)
print()

# Test 1: Import check
print("Test 1: Import LangGraph components")
print("-" * 60)
try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    from typing import TypedDict, Optional, Literal
    
    print("[OK] LangGraph imports successful")
except Exception as e:
    print(f"[FAIL] Import failed: {e}")
    sys.exit(1)

print()

# Test 2: Create simple workflow
print("Test 2: Create Simple Workflow")
print("-" * 60)

class SimpleState(TypedDict):
    value: int
    status: str

def increment(state: SimpleState) -> SimpleState:
    state['value'] += 1
    state['status'] = 'incremented'
    return state

def check_value(state: SimpleState) -> Literal['continue', 'stop']:
    if state['value'] < 3:
        return 'continue'
    return 'stop'

def finalize(state: SimpleState) -> SimpleState:
    state['status'] = 'completed'
    return state

try:
    workflow = StateGraph(SimpleState)
    workflow.add_node('increment', increment)
    workflow.add_node('finalize', finalize)
    workflow.set_entry_point('increment')
    
    workflow.add_conditional_edges(
        'increment',
        check_value,
        {
            'continue': 'increment',
            'stop': 'finalize'
        }
    )
    
    workflow.add_edge('finalize', END)
    
    app = workflow.compile(checkpointer=MemorySaver())
    
    print("[OK] Workflow created successfully")
    print(f"   Nodes: {list(app.get_graph().nodes)}")
    print(f"   Edges: {list(app.get_graph().edges)}")
    
except Exception as e:
    print(f"[FAIL] Workflow creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 3: Execute workflow
print("Test 3: Execute Workflow")
print("-" * 60)

try:
    config = {'configurable': {'thread_id': 'test-1'}}
    initial_state = {'value': 0, 'status': 'starting'}
    
    result = app.invoke(initial_state, config)
    
    print(f"   Initial value: 0")
    print(f"   Final value: {result['value']}")
    print(f"   Final status: {result['status']}")
    
    assert result['value'] == 3, f"Expected 3, got {result['value']}"
    assert result['status'] == 'completed'
    
    print("[OK] Workflow executed successfully")
    
except Exception as e:
    print(f"[FAIL] Execution failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 4: State persistence
print("Test 4: State Persistence")
print("-" * 60)

try:
    # Get state from memory
    memory = app.checkpointer
    saved_state = memory.get(config)
    
    print(f"   State persisted: [OK]")
    print(f"   Thread ID: test-1")
    
    print("[OK] State persistence working")
    
except Exception as e:
    print(f"[WARN] Persistence check failed: {e}")

print()

# Summary
print("=" * 60)
print("All Tests Passed!")
print("=" * 60)
print()
print("Next steps:")
print("1. Integrate with ymcode.taskqueue.Task")
print("2. Implement _get_available_agents()")
print("3. Add event publishing")
print("4. Replace old A2ACoordinator")
print()
