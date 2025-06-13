# PowerMake

An enhanced version of a makefile-style workflow manager that executes pipelines defined in YAML.

**Author** 

  - Design: Carlos M. Martinez
  - Programming: Claude AI

## Features

  - **YAML-based pipeline specification**: Define workflows using simple YAML syntax
  - **Four node types**: `readfile`, `runscript`, `writefile`, and `httpgetfile`
  - **Progress tracking**: Real-time progress display with timing information
  - **Rich error messages**: Detailed validation and execution error reporting
  - **Sanity checking**: Validates pipeline syntax and file existence before execution
  - **Temporary file management**: Automatic handling of intermediate files

## Installation

### Using Poetry (Recommended)

1. Install dependencies:

```bash
poetry install
```

2. Run PowerMake:

```bash
poetry run python -m powermake.cli pipeline.yml
```

### Using pip

1. Install dependencies:
```bash
pip install typer pyyaml rich requests pytest
```

2. Install PowerMake (development mode):
```bash
pip install -e .
```

## Usage

### Basic Usage

```bash
python -m powermake.cli pipeline.yml
```
