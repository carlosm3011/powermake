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

### Command Line Options

- `--tmp-dir, -t`: Specify temporary directory (default: `.tmp/` in pipeline file directory)
- `--verbose, -v`: Enable verbose output
- `--help`: Show help message

### Example

Using Poetry:
```bash
poetry run python -m powermake.cli example_pipeline.yml --verbose --tmp-dir /tmp/powermake
```

Using pip installation:
```bash
python -m powermake.cli example_pipeline.yml --verbose --tmp-dir /tmp/powermake
```

## Pipeline Specification

A PowerMake pipeline is defined as a YAML list of nodes. Each node has:
- `node`: The node type (`readfile`, `runscript`, `writefile`, or `httpgetfile`)
- `id`: A unique identifier for the node
- Additional fields specific to the node type

### Node Types

#### ReadFile Node
Reads a file and copies it to the temporary directory.

```yaml
- node: readfile
  path: /path/to/input.csv
  id: input_data
```

#### RunScript Node
Executes a script/command and captures its output.

```yaml
- node: runscript
  path: ./process.sh ${input_data}  # ${node_id} variables are expanded
  id: processed_data
```

#### WriteFile Node
Writes the output of a previous node to a specified location.

```yaml
- node: writefile
  input: processed_data  # References another node's ID
  output: /path/to/result.txt
  id: final_output
```

#### HttpGetFile Node
Downloads a file from an HTTP(S) URL to the temporary directory.

```yaml
- node: httpgetfile
  url: https://example.com/data.csv
  id: downloaded_data
```

### Complete Example

```yaml
- node: readfile 
  path: example_data.csv
  id: examplecsv

- node: httpgetfile
  url: https://example.com/remote_data.json
  id: remote_data

- node: runscript
  path: ./process_data.sh ${examplecsv} ${remote_data}
  id: processed_data

- node: writefile
  input: processed_data
  output: output/result.txt
  id: final_output
```

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Project Structure

```
❯ tree --gitignore
.
├── DESIGN.md
├── LICENSE
├── output
│   └── result.txt
├── poetry.lock
├── powermake
│   ├── __init__.py
│   ├── cli.py
│   ├── nodes.py
│   └── pipeline.py
├── pyproject.toml
├── README.md
├── test_basic.py
├── test_nodes_only.py
├── test_pipeline
│   ├── example_data.csv
│   ├── example_pipeline.yml
│   └── process_data.sh
└── tests
    ├── __init__.py
    ├── test_nodes.py
    └── test_pipeline.py
```

## Features Included in v1

  - YAML pipeline specification parser 
  - CLI interface with Typer  
  - Four core node types (readfile, runscript, writefile, httpgetfile)  
  - Progress tracking with timing  
  - Comprehensive validation and error checking  
  - Rich error messages  
  - Unit test coverage  
  - Temporary file management  

## Future Enhancements (Not in v1)

- Dependency calculation among nodes
- Parallel execution
- Additional node types
- Pipeline caching and resumption
