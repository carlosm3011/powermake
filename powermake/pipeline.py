"""Pipeline execution engine for PowerMake."""

import time
import yaml
from pathlib import Path
from typing import List, Dict, Any
from rich.console import Console
from rich.progress import Progress, TaskID, track
from rich.table import Table

from .nodes import create_node, Node, PowerMakeError, NodeValidationError


class Pipeline:
    """Pipeline execution engine."""
    
    def __init__(self, pipeline_file: Path, tmp_dir: Path, verbose: bool = False):
        self.pipeline_file = pipeline_file
        self.tmp_dir = tmp_dir
        self.verbose = verbose
        self.console = Console()
        self.nodes: List[Node] = []
        self.node_outputs: Dict[str, Path] = {}
        
        self._load_pipeline()
        self._prepare_tmp_dir()
    
    def _load_pipeline(self) -> None:
        """Load and parse the pipeline YAML file."""
        try:
            with open(self.pipeline_file, 'r') as f:
                pipeline_data = yaml.safe_load(f)
        except Exception as e:
            raise PowerMakeError(f"Failed to load pipeline file '{self.pipeline_file}': {e}")
        
        if not isinstance(pipeline_data, list):
            raise PowerMakeError("Pipeline file must contain a list of nodes")
        
        if not pipeline_data:
            raise PowerMakeError("Pipeline file is empty")
        
        # Create node instances
        for i, node_config in enumerate(pipeline_data):
            if not isinstance(node_config, dict):
                raise PowerMakeError(f"Node {i+1} must be a dictionary")
            
            try:
                node = create_node(node_config, self.tmp_dir)
                self.nodes.append(node)
            except Exception as e:
                raise PowerMakeError(f"Failed to create node {i+1}: {e}")
        
        # Check for duplicate node IDs
        node_ids = [node.node_id for node in self.nodes]
        duplicates = set([id for id in node_ids if node_ids.count(id) > 1])
        if duplicates:
            raise PowerMakeError(f"Duplicate node IDs found: {', '.join(duplicates)}")
    
    def _prepare_tmp_dir(self) -> None:
        """Create and prepare the temporary directory."""
        try:
            self.tmp_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise PowerMakeError(f"Failed to create temporary directory '{self.tmp_dir}': {e}")
    
    def _validate_pipeline(self) -> None:
        """Validate all nodes in the pipeline."""
        self.console.print("[bold blue]Validating pipeline...[/bold blue]")
        
        for i, node in enumerate(self.nodes):
            try:
                node.validate(self.node_outputs)
                if self.verbose:
                    self.console.print(f"✓ Node {i+1} ({node.node_id}): {node.node_type} - Valid")
            except NodeValidationError as e:
                raise PowerMakeError(f"Validation failed for node {i+1} ({node.node_id}): {e}")
        
        self.console.print("[green]✓ Pipeline validation successful[/green]")
    
    def _show_pipeline_summary(self) -> None:
        """Display a summary of the pipeline."""
        table = Table(title="Pipeline Summary")
        table.add_column("Step", justify="right", style="cyan")
        table.add_column("Node ID", style="magenta")
        table.add_column("Type", style="green")
        table.add_column("Description", style="white")
        
        for i, node in enumerate(self.nodes):
            description = ""
            if node.node_type == "readfile":
                description = f"Read: {node.config.get('path', 'N/A')}"
            elif node.node_type == "runscript":
                description = f"Run: {node.config.get('path', 'N/A')}"
            elif node.node_type == "writefile":
                description = f"Write to: {node.config.get('output', 'N/A')}"
            elif node.node_type == "httpgetfile":
                description = f"Download: {node.config.get('url', 'N/A')}"
            
            table.add_row(str(i+1), node.node_id, node.node_type, description)
        
        self.console.print(table)
    
    def run(self) -> None:
        """Execute the pipeline."""
        start_time = time.time()
        
        self.console.print(f"[bold green]Starting PowerMake pipeline: {self.pipeline_file.name}[/bold green]")
        self.console.print(f"Temporary directory: {self.tmp_dir}")
        self.console.print(f"Total nodes: {len(self.nodes)}")
        
        if self.verbose:
            self._show_pipeline_summary()
        
        # Validate pipeline
        self._validate_pipeline()
        
        # Execute nodes
        self.console.print("\n[bold blue]Executing pipeline...[/bold blue]")
        
        with Progress() as progress:
            task = progress.add_task("[green]Processing nodes...", total=len(self.nodes))
            
            for i, node in enumerate(self.nodes):
                current_time = time.time()
                elapsed = current_time - start_time
                
                self.console.print(f"\n[cyan]Step {i+1}/{len(self.nodes)}[/cyan] - "
                                 f"[bold]{node.node_id}[/bold] ({node.node_type}) - "
                                 f"Elapsed: {elapsed:.1f}s")
                
                try:
                    # Re-validate the node with current outputs
                    node.validate(self.node_outputs)
                    
                    # Execute the node
                    output_path = node.execute(self.node_outputs)
                    self.node_outputs[node.node_id] = output_path
                    
                    if self.verbose:
                        self.console.print(f"  ✓ Output: {output_path}")
                    
                    progress.update(task, advance=1)
                    
                except Exception as e:
                    raise PowerMakeError(f"Execution failed for node {i+1} ({node.node_id}): {e}")
        
        # Pipeline completed
        total_time = time.time() - start_time
        self.console.print(f"\n[bold green]✓ Pipeline completed successfully![/bold green]")
        self.console.print(f"Total execution time: {total_time:.2f}s")
        
        if self.verbose:
            self.console.print("\n[bold]Final outputs:[/bold]")
            for node_id, output_path in self.node_outputs.items():
                self.console.print(f"  {node_id}: {output_path}")