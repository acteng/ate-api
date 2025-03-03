# ATE API

Operational data API for Active Travel England.

[![CI](https://github.com/acteng/ate-api/actions/workflows/ci.yml/badge.svg)](https://github.com/acteng/ate-api/actions/workflows/ci.yml)

## Prerequisites

1. Install Python 3.13
1. Install Google Cloud CLI and authenticate using ADCs:
   ```bash
   gcloud auth application-default login
   ```
1. Install Terraform 1.11

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

## Running locally using Docker

To run the server as a container:

1. Build the Docker image:

   ```bash
   docker build -t ate-api .
   ```
   
1. Run the Docker image:

   ```bash
   docker run --rm -it -p 8000:8000 ate-api
   ```
   
1. Invoke the server:

   ```bash
   curl http://localhost:8000
   ```

The server can also be run on a different port by specifying the `PORT` environment variable:

```bash
docker run --rm -it -e PORT=8001 -p 8001:8001 ate-api
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

## Provisioning infrastructure

### Provision the Terraform backend

1. Change directory:

   ```bash
   cd cloud/tf-backend
   ```

1. Initialise Terraform:

   ```bash
   terraform init
   ```

1. Fetch the previous Terraform state from Bitwarden, if any:

   ```bash
   bw get notes "API tf-backend State" > terraform.tfstate
   ```

1. Apply the changes:

   ```bash
   terraform apply
   ```

1. Store the new Terraform state in Bitwarden as "API tf-backend State"

### Provision the Docker repository

1. Change directory:

   ```bash
   cd cloud/docker-repository
   ```

1. Initialise Terraform:

   ```bash
   terraform init
   ```

1. Apply the changes:

   ```bash
   terraform apply
   ```

## See also

* [Architecture](docs/architecture)
