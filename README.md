# ATE API

Operational data API for Active Travel England.

[![CI](https://github.com/acteng/ate-api/actions/workflows/ci.yml/badge.svg)](https://github.com/acteng/ate-api/actions/workflows/ci.yml)

## Prerequisites

1. Install Python 3.13
1. Install [Terraform](https://developer.hashicorp.com/terraform/install) 1.11

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

1. Invoke the server at http://localhost:8000

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
   
1. Invoke the server at http://localhost:8000

The server can also be run on a different port by specifying the `PORT` environment variable:

```bash
docker run --rm -it -e PORT=8001 -p 8001:8001 ate-api
```

## Invoking

To invoke the server running locally at http://localhost:8000:

1. Obtain the OAuth client credentials:

   ```bash
   cd cloud/identity
   terraform workspace select dev
   CLIENT_ID=$(terraform output -raw example_client_id)
   CLIENT_SECRET=$(terraform output -raw example_client_secret)
   ```

1. Obtain an access token from the identity provider:

   ```bash
   ACCESS_TOKEN=$(curl -s https://ate-api-dev.uk.auth0.com/oauth/token \
      -H 'Content-Type: application/x-www-form-urlencoded' \
      -d 'grant_type=client_credentials' \
      -d 'audience=https://dev.api.activetravelengland.gov.uk' \
      -d "client_id=${CLIENT_ID}" \
      -d "client_secret=${CLIENT_SECRET}" | jq -r .access_token)
   ```

1. Invoke the server with the access token:

   ```bash
   curl -H "Authorization: Bearer ${ACCESS_TOKEN}" http://localhost:8000
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
* [Cloud infrastructure](cloud/README.md)
