#!/usr/bin/env python3
"""Test script to verify PowerMake node functionality without external dependencies."""

import sys
from pathlib import Path

# Add the powermake module to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    # Test basic node imports and functionality
    from powermake.nodes import ReadFileNode, RunScriptNode, WriteFileNode, create_node
    print("✓ Node modules imported successfully")
    
    # Test node creation
    tmp_dir = Path("test_tmp")
    tmp_dir.mkdir(exist_ok=True)
    
    # Test ReadFileNode creation
    config = {"node": "readfile", "id": "test", "path": "example_data.csv"}
    node = create_node(config, tmp_dir)
    print(f"✓ Created ReadFileNode: {node.node_id} ({node.node_type})")
    
    # Test RunScriptNode creation
    config = {"node": "runscript", "id": "test2", "path": "echo hello"}
    node = create_node(config, tmp_dir)
    print(f"✓ Created RunScriptNode: {node.node_id} ({node.node_type})")
    
    # Test WriteFileNode creation
    config = {"node": "writefile", "id": "test3", "input": "src", "output": "output.txt"}
    node = create_node(config, tmp_dir)
    print(f"✓ Created WriteFileNode: {node.node_id} ({node.node_type})")
    
    # Test validation
    read_node = ReadFileNode({"node": "readfile", "id": "read_test", "path": "example_data.csv"}, tmp_dir)
    read_node.validate({})
    print("✓ ReadFileNode validation passed")
    
    print("\n✓ Node functionality test passed!")
    print("\nPowerMake v1 is ready!")
    print("\nTo use PowerMake:")
    print("1. Install dependencies: pip install typer pyyaml rich pytest")
    print("2. Run pipeline: python -m powermake.cli example_pipeline.yml --verbose")
    print("3. Run tests: python -m pytest tests/")
    
except Exception as e:
    print(f"✗ Test failed: {e}")
    import traceback
    traceback.print_exc()
finally:
    # Clean up
    test_tmp = Path("test_tmp")
    if test_tmp.exists():
        import shutil
        shutil.rmtree(test_tmp)