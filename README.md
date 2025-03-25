# ATE API

Operational data API for Active Travel England.

[![CI](https://github.com/acteng/ate-api/actions/workflows/ci.yml/badge.svg)](https://github.com/acteng/ate-api/actions/workflows/ci.yml)

## Prerequisites

1. Install Python 3.13
1. Install [Terraform](https://developer.hashicorp.com/terraform/install) 1.11

## Running locally using Compose

To run the server as a container using a database:

1. Run the services:

   ```bash
   docker compose up
   ```

1. Invoke the server at http://localhost:8000

## Running locally using Docker

To run the server as a container:

1. Build the Docker image:

   ```bash
   docker build -t ate-api .
   ```
   
1. Run the database image:

   ```bash
   docker run --rm -it -e POSTGRES_USER=ate -e POSTGRES_PASSWORD=password -p 5432:5432 postgres:16       
   ```

1. Run the Docker image:

   ```bash
   docker run --rm -it --network=host -e CREATE_DATABASE_SCHEMA=true ate-api
   ```
   
1. Invoke the server at http://localhost:8000

The server can also be run on a different port by specifying the `PORT` environment variable:

```bash
docker run --rm -it --network=host -e CREATE_DATABASE_SCHEMA=true -e PORT=8001 ate-api
```

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

1. Run the database image:

   ```bash
   docker run --rm -it -e POSTGRES_USER=ate -e POSTGRES_PASSWORD=password -p 5432:5432 postgres:16       
   ```
   
   Or using Compose:

   ```bash
   docker compose up database
   ```
   
1. Run the server:

   ```bash
   CREATE_DATABASE_SCHEMA=true make run
   ```

1. Invoke the server at http://localhost:8000

## Invoking

To invoke the server running in an environment:

1. Obtain the identity provider details:

   ```bash
   cd cloud/identity
   terraform workspace select ${ENVIRONMENT}
   TOKEN_ENDPOINT=$(curl -s $(terraform output -raw oidc_server_metadata_url) | jq -r .token_endpoint)
   RESOURCE_SERVER_IDENTIFIER=$(terraform output -raw resource_server_identifier)
   CLIENT_ID=$(terraform output -raw example_client_id)
   CLIENT_SECRET=$(terraform output -raw example_client_secret)
   ```

1. Obtain an access token from the identity provider:

   ```bash
   ACCESS_TOKEN=$(curl -s ${TOKEN_ENDPOINT} \
      -H 'Content-Type: application/x-www-form-urlencoded' \
      -d 'grant_type=client_credentials' \
      -d "audience=${RESOURCE_SERVER_IDENTIFIER}" \
      -d "client_id=${CLIENT_ID}" \
      -d "client_secret=${CLIENT_SECRET}" | jq -r .access_token)
   ```

1. Obtain the server details:

   ```bash
   cd cloud/service
   terraform workspace select ${ENVIRONMENT}
   SERVER_URL=$(terraform output -raw url)
   ```

1. Invoke the server with the access token:

   ```bash
   curl -H "Authorization: Bearer ${ACCESS_TOKEN}" ${SERVER_URL}/authorities/GMA
   ```

## Configuring

The server can be configured with the following environment variables:

| Name                       | Value                                                                                   |
|----------------------------|-----------------------------------------------------------------------------------------|
| DATABASE_URL               | [Database URL](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls)       |
| CREATE_DATABASE_SCHEMA     | `true` to create the database schema                                                    |
| OIDC_SERVER_METADATA_URL   | Authorisation server configuration endpoint                                             |
| RESOURCE_SERVER_IDENTIFIER | Resource server identifier (this must match the audience claim in the JWT access token) |

Environment variables can also be provided in a `.env` file.

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
