"""CLI interface for PowerMake."""

import typer
from pathlib import Path
from typing import Optional

from .pipeline import Pipeline

app = typer.Typer(help="PowerMake - Enhanced makefile-style workflow manager")


@app.command()
def run(
    pipeline_file: Path = typer.Argument(..., help="YAML pipeline specification file"),
    tmp_dir: Optional[Path] = typer.Option(
        None, 
        "--tmp-dir", 
        "-t", 
        help="Temporary directory for intermediate files (default: .tmp/ in pipeline file directory)"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Run a PowerMake pipeline from a YAML specification file."""
    if not pipeline_file.exists():
        typer.echo(f"Error: Pipeline file '{pipeline_file}' not found", err=True)
        raise typer.Exit(1)
    
    if tmp_dir is None:
        tmp_dir = pipeline_file.parent / ".tmp"
    
    try:
        pipeline = Pipeline(pipeline_file, tmp_dir, verbose=verbose)
        pipeline.run()
        typer.echo("Pipeline completed successfully!")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()