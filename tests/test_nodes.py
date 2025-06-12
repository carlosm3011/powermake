"""Tests for PowerMake nodes."""

import pytest
import tempfile
import shutil
from pathlib import Path

from powermake.nodes import (
    ReadFileNode, RunScriptNode, WriteFileNode, create_node,
    NodeValidationError, NodeExecutionError
)


@pytest.fixture
def tmp_dir():
    """Create a temporary directory for tests."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_file(tmp_dir):
    """Create a test file."""
    test_file = tmp_dir / "test.txt"
    test_file.write_text("Hello, World!")
    return test_file


class TestReadFileNode:
    
    def test_create_readfile_node(self, tmp_dir, test_file):
        config = {"node": "readfile", "id": "test", "path": str(test_file)}
        node = ReadFileNode(config, tmp_dir)
        assert node.node_type == "readfile"
        assert node.node_id == "test"
    
    def test_validate_success(self, tmp_dir, test_file):
        config = {"node": "readfile", "id": "test", "path": str(test_file)}
        node = ReadFileNode(config, tmp_dir)
        node.validate({})  # Should not raise
    
    def test_validate_missing_path(self, tmp_dir):
        config = {"node": "readfile", "id": "test"}
        node = ReadFileNode(config, tmp_dir)
        with pytest.raises(NodeValidationError, match="missing 'path' field"):
            node.validate({})
    
    def test_validate_nonexistent_file(self, tmp_dir):
        config = {"node": "readfile", "id": "test", "path": "/nonexistent/file.txt"}
        node = ReadFileNode(config, tmp_dir)
        with pytest.raises(NodeValidationError, match="does not exist"):
            node.validate({})
    
    def test_execute_success(self, tmp_dir, test_file):
        config = {"node": "readfile", "id": "test", "path": str(test_file)}
        node = ReadFileNode(config, tmp_dir)
        output_path = node.execute({})
        assert output_path.exists()
        assert output_path.read_text() == "Hello, World!"


class TestRunScriptNode:
    
    def test_create_runscript_node(self, tmp_dir):
        config = {"node": "runscript", "id": "test", "path": "echo hello"}
        node = RunScriptNode(config, tmp_dir)
        assert node.node_type == "runscript"
        assert node.node_id == "test"
    
    def test_execute_simple_command(self, tmp_dir):
        config = {"node": "runscript", "id": "test", "path": "echo 'Hello, World!'"}
        node = RunScriptNode(config, tmp_dir)
        output_path = node.execute({})
        assert output_path.exists()
        assert "Hello, World!" in output_path.read_text()
    
    def test_expand_variables(self, tmp_dir, test_file):
        config = {"node": "runscript", "id": "test", "path": "cat ${input_file}"}
        node = RunScriptNode(config, tmp_dir)
        node_outputs = {"input_file": test_file}
        expanded = node._expand_variables(config["path"], node_outputs)
        assert expanded == f"cat {test_file}"


class TestWriteFileNode:
    
    def test_create_writefile_node(self, tmp_dir):
        config = {"node": "writefile", "id": "test", "input": "src", "output": "/tmp/output.txt"}
        node = WriteFileNode(config, tmp_dir)
        assert node.node_type == "writefile"
        assert node.node_id == "test"
    
    def test_validate_missing_input(self, tmp_dir):
        config = {"node": "writefile", "id": "test", "output": "/tmp/output.txt"}
        node = WriteFileNode(config, tmp_dir)
        with pytest.raises(NodeValidationError, match="missing 'input' field"):
            node.validate({})
    
    def test_validate_missing_output(self, tmp_dir):
        config = {"node": "writefile", "id": "test", "input": "src"}
        node = WriteFileNode(config, tmp_dir)
        with pytest.raises(NodeValidationError, match="missing 'output' field"):
            node.validate({})
    
    def test_execute_success(self, tmp_dir, test_file):
        output_path = tmp_dir / "output.txt"
        config = {"node": "writefile", "id": "test", "input": "src", "output": str(output_path)}
        node = WriteFileNode(config, tmp_dir)
        node_outputs = {"src": test_file}
        result_path = node.execute(node_outputs)
        assert result_path == output_path
        assert output_path.exists()
        assert output_path.read_text() == "Hello, World!"


class TestCreateNode:
    
    def test_create_readfile_node(self, tmp_dir):
        config = {"node": "readfile", "id": "test", "path": "/tmp/test.txt"}
        node = create_node(config, tmp_dir)
        assert isinstance(node, ReadFileNode)
    
    def test_create_runscript_node(self, tmp_dir):
        config = {"node": "runscript", "id": "test", "path": "echo hello"}
        node = create_node(config, tmp_dir)
        assert isinstance(node, RunScriptNode)
    
    def test_create_writefile_node(self, tmp_dir):
        config = {"node": "writefile", "id": "test", "input": "src", "output": "/tmp/out.txt"}
        node = create_node(config, tmp_dir)
        assert isinstance(node, WriteFileNode)
    
    def test_unknown_node_type(self, tmp_dir):
        config = {"node": "unknown", "id": "test"}
        with pytest.raises(NodeValidationError, match="Unknown node type: unknown"):
            create_node(config, tmp_dir)