"""Node classes for PowerMake pipeline steps."""

import os
import shutil
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any


class PowerMakeError(Exception):
    """Base exception for PowerMake errors."""
    pass


class NodeValidationError(PowerMakeError):
    """Raised when node validation fails."""
    pass


class NodeExecutionError(PowerMakeError):
    """Raised when node execution fails."""
    pass


class Node(ABC):
    """Base class for pipeline nodes."""
    
    def __init__(self, config: Dict[str, Any], tmp_dir: Path):
        self.config = config
        self.tmp_dir = tmp_dir
        self.node_type = config.get('node')
        self.node_id = config.get('id')
        
        if not self.node_type:
            raise NodeValidationError("Node missing 'node' field")
        if not self.node_id:
            raise NodeValidationError("Node missing 'id' field")
    
    @abstractmethod
    def validate(self, node_outputs: Dict[str, Path]) -> None:
        """Validate the node configuration and dependencies."""
        pass
    
    @abstractmethod
    def execute(self, node_outputs: Dict[str, Path]) -> Path:
        """Execute the node and return the output file path."""
        pass


class ReadFileNode(Node):
    """Node that reads a file and copies it to the temp directory."""
    
    def validate(self, node_outputs: Dict[str, Path]) -> None:
        if 'path' not in self.config:
            raise NodeValidationError(f"ReadFile node '{self.node_id}' missing 'path' field")
        
        input_path = Path(self.config['path'])
        if not input_path.exists():
            raise NodeValidationError(f"ReadFile node '{self.node_id}': Input file '{input_path}' does not exist")
        if not input_path.is_file():
            raise NodeValidationError(f"ReadFile node '{self.node_id}': Path '{input_path}' is not a file")
    
    def execute(self, node_outputs: Dict[str, Path]) -> Path:
        input_path = Path(self.config['path'])
        output_path = self.tmp_dir / f"{self.node_id}_{input_path.name}"
        
        try:
            shutil.copy2(input_path, output_path)
            return output_path
        except Exception as e:
            raise NodeExecutionError(f"ReadFile node '{self.node_id}' failed: {e}")


class RunScriptNode(Node):
    """Node that runs a script and captures its output."""
    
    def validate(self, node_outputs: Dict[str, Path]) -> None:
        if 'path' not in self.config:
            raise NodeValidationError(f"RunScript node '{self.node_id}' missing 'path' field")
        
        script_path = self._expand_variables(self.config['path'], node_outputs)
        script_parts = script_path.split()
        if script_parts:
            actual_script = Path(script_parts[0])
            if not actual_script.exists():
                raise NodeValidationError(f"RunScript node '{self.node_id}': Script '{actual_script}' does not exist")
    
    def _expand_variables(self, command: str, node_outputs: Dict[str, Path]) -> str:
        """Expand ${node_id} variables in the command string."""
        expanded = command
        for node_id, output_path in node_outputs.items():
            expanded = expanded.replace(f"${{{node_id}}}", str(output_path))
        return expanded
    
    def execute(self, node_outputs: Dict[str, Path]) -> Path:
        command = self._expand_variables(self.config['path'], node_outputs)
        output_path = self.tmp_dir / f"{self.node_id}_output.txt"
        
        try:
            with open(output_path, 'w') as f:
                result = subprocess.run(
                    command, 
                    shell=True, 
                    stdout=f, 
                    stderr=subprocess.PIPE, 
                    text=True,
                    check=True
                )
            return output_path
        except subprocess.CalledProcessError as e:
            raise NodeExecutionError(f"RunScript node '{self.node_id}' failed with exit code {e.returncode}: {e.stderr}")
        except Exception as e:
            raise NodeExecutionError(f"RunScript node '{self.node_id}' failed: {e}")


class WriteFileNode(Node):
    """Node that writes output to a specified file."""
    
    def validate(self, node_outputs: Dict[str, Path]) -> None:
        if 'input' not in self.config:
            raise NodeValidationError(f"WriteFile node '{self.node_id}' missing 'input' field")
        if 'output' not in self.config:
            raise NodeValidationError(f"WriteFile node '{self.node_id}' missing 'output' field")
        
        input_id = self.config['input']
        if node_outputs and input_id not in node_outputs:
            raise NodeValidationError(f"WriteFile node '{self.node_id}': Input node '{input_id}' not found or not yet executed")
        
        output_path = Path(self.config['output'])
        output_dir = output_path.parent
        if not output_dir.exists():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise NodeValidationError(f"WriteFile node '{self.node_id}': Cannot create output directory '{output_dir}': {e}")
    
    def execute(self, node_outputs: Dict[str, Path]) -> Path:
        input_id = self.config['input']
        input_path = node_outputs[input_id]
        output_path = Path(self.config['output'])
        
        try:
            shutil.copy2(input_path, output_path)
            return output_path
        except Exception as e:
            raise NodeExecutionError(f"WriteFile node '{self.node_id}' failed: {e}")


def create_node(config: Dict[str, Any], tmp_dir: Path) -> Node:
    """Factory function to create appropriate node instances."""
    node_type = config.get('node', '').lower()
    
    if node_type == 'readfile':
        return ReadFileNode(config, tmp_dir)
    elif node_type == 'runscript':
        return RunScriptNode(config, tmp_dir)
    elif node_type == 'writefile':
        return WriteFileNode(config, tmp_dir)
    else:
        raise NodeValidationError(f"Unknown node type: {node_type}")