#!/usr/bin/env python3
"""Basic test script to verify PowerMake functionality without external dependencies."""

import sys
import os
from pathlib import Path

# Add the powermake module to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    # Test basic imports
    from powermake.nodes import ReadFileNode, RunScriptNode, WriteFileNode, create_node
    from powermake.pipeline import Pipeline
    print("✓ All modules imported successfully")
    
    # Test node creation
    tmp_dir = Path("test_tmp")
    tmp_dir.mkdir(exist_ok=True)
    
    # Test ReadFileNode creation
    config = {"node": "readfile", "id": "test", "path": "example_data.csv"}
    node = create_node(config, tmp_dir)
    print(f"✓ Created ReadFileNode: {node.node_id}")
    
    # Test RunScriptNode creation
    config = {"node": "runscript", "id": "test", "path": "echo hello"}
    node = create_node(config, tmp_dir)
    print(f"✓ Created RunScriptNode: {node.node_id}")
    
    # Test WriteFileNode creation
    config = {"node": "writefile", "id": "test", "input": "src", "output": "output.txt"}
    node = create_node(config, tmp_dir)
    print(f"✓ Created WriteFileNode: {node.node_id}")
    
    print("\n✓ Basic functionality test passed!")
    print("\nTo run PowerMake:")
    print("1. Install dependencies: pip install typer pyyaml rich")
    print("2. Run: python -m powermake.cli example_pipeline.yml --verbose")
    
except Exception as e:
    print(f"✗ Test failed: {e}")
    import traceback
    traceback.print_exc()
finally:
    # Clean up
    if tmp_dir.exists():
        import shutil
        shutil.rmtree(tmp_dir)