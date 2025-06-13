#!/usr/bin/env python3

# Test automation workflow generation
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.routes.automation import get_default_automations, get_basic_workflow
import json

# Test default automations
print("Testing default automations...")
automations = get_default_automations()
print(f"Number of automations: {len(automations)}")

for i, automation in enumerate(automations):
    print(f"\nAutomation {i+1}: {automation['task_name']}")
    print(f"Has n8n_workflow: {'n8n_workflow' in automation}")
    
    if 'n8n_workflow' in automation and automation['n8n_workflow']:
        workflow = automation['n8n_workflow']
        print(f"Workflow name: {workflow.get('name', 'No name')}")
        print(f"Number of nodes: {len(workflow.get('nodes', []))}")
        print(f"Has connections: {bool(workflow.get('connections'))}")
        print(f"Workflow ID: {workflow.get('id', 'No ID')}")
        
        # Test JSON serialization
        try:
            workflow_json = json.dumps(workflow, indent=2)
            print(f"JSON serialization: OK ({len(workflow_json)} chars)")
        except Exception as e:
            print(f"JSON serialization ERROR: {e}")
    else:
        print("No workflow found!")

# Test basic workflow generation
print("\n\nTesting basic workflow generation...")
basic_workflow = get_basic_workflow("Test Task")
print(f"Basic workflow created: {bool(basic_workflow)}")
if basic_workflow:
    print(f"Name: {basic_workflow.get('name')}")
    print(f"Nodes: {len(basic_workflow.get('nodes', []))}")
    try:
        json.dumps(basic_workflow)
        print("Basic workflow JSON: OK")
    except Exception as e:
        print(f"Basic workflow JSON ERROR: {e}")

print("\nTest completed!") 