# ATE API

Operational data API for Active Travel England.

## Prerequisites

1. Install Python 3.13

## Running locally

1. Create a virtual environment:

   ```bash
   python3.13 -m venv --prompt . --upgrade-deps .venv
   ```

1. Activate the virtual environment:

   ```bash
   source .venv/bin/activate
   ```

1. Install the dependencies:

   ```bash
   pip install -e .[dev]
   ```

1. Run the server:

   ```bash
   make run
   ```

1. Invoke the server:

   ```bash
   curl http://localhost:8000
   ```

## Running formatters and linters

1. Run the formatters:

   ```bash
   make format
   ```

1. Run the linters:

   ```bash
   make lint
   ```
   
## Running tests

Run the tests:
   
   ```bash
   make test
   ```

## See also

* [Architecture](docs/architecture)
