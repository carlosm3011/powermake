"""Tests for PowerMake pipeline."""

import pytest
import tempfile
import shutil
import yaml
from pathlib import Path

from powermake.pipeline import Pipeline
from powermake.nodes import PowerMakeError


@pytest.fixture
def tmp_dir():
    """Create a temporary directory for tests."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def valid_pipeline_yaml(tmp_dir):
    """Create a valid pipeline YAML file."""
    # Create test input file
    input_file = tmp_dir / "input.txt"
    input_file.write_text("test data")
    
    # Create pipeline YAML
    pipeline_data = [
        {"node": "readfile", "id": "input", "path": str(input_file)},
        {"node": "runscript", "id": "process", "path": "cat ${input}"},
        {"node": "writefile", "id": "output", "input": "process", "output": str(tmp_dir / "output.txt")}
    ]
    
    pipeline_file = tmp_dir / "pipeline.yml"
    with open(pipeline_file, 'w') as f:
        yaml.dump(pipeline_data, f)
    
    return pipeline_file


class TestPipeline:
    
    def test_load_valid_pipeline(self, tmp_dir, valid_pipeline_yaml):
        pipeline = Pipeline(valid_pipeline_yaml, tmp_dir / "tmp")
        assert len(pipeline.nodes) == 3
        assert pipeline.nodes[0].node_id == "input"
        assert pipeline.nodes[1].node_id == "process"
        assert pipeline.nodes[2].node_id == "output"
    
    def test_load_nonexistent_file(self, tmp_dir):
        nonexistent_file = tmp_dir / "nonexistent.yml"
        with pytest.raises(PowerMakeError, match="Failed to load pipeline file"):
            Pipeline(nonexistent_file, tmp_dir / "tmp")
    
    def test_empty_pipeline(self, tmp_dir):
        empty_pipeline = tmp_dir / "empty.yml"
        empty_pipeline.write_text("[]")
        with pytest.raises(PowerMakeError, match="Pipeline file is empty"):
            Pipeline(empty_pipeline, tmp_dir / "tmp")
    
    def test_invalid_yaml(self, tmp_dir):
        invalid_pipeline = tmp_dir / "invalid.yml"
        invalid_pipeline.write_text("not a list")
        with pytest.raises(PowerMakeError, match="must contain a list of nodes"):
            Pipeline(invalid_pipeline, tmp_dir / "tmp")
    
    def test_duplicate_node_ids(self, tmp_dir):
        input_file = tmp_dir / "input.txt"
        input_file.write_text("test")
        
        pipeline_data = [
            {"node": "readfile", "id": "duplicate", "path": str(input_file)},
            {"node": "readfile", "id": "duplicate", "path": str(input_file)}
        ]
        
        pipeline_file = tmp_dir / "pipeline.yml"
        with open(pipeline_file, 'w') as f:
            yaml.dump(pipeline_data, f)
        
        with pytest.raises(PowerMakeError, match="Duplicate node IDs found: duplicate"):
            Pipeline(pipeline_file, tmp_dir / "tmp")
    
    def test_run_simple_pipeline(self, tmp_dir, valid_pipeline_yaml):
        pipeline = Pipeline(valid_pipeline_yaml, tmp_dir / "tmp", verbose=False)
        pipeline.run()  # Should complete without error
        
        # Check that output file was created
        output_file = tmp_dir / "output.txt"
        assert output_file.exists()
        assert "test data" in output_file.read_text()