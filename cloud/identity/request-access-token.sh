#!/bin/bash

# Requests an access token from the identity provider

set -eo pipefail

SERVER_METADATA_URL=$(terraform output -raw oidc_server_metadata_url)
TOKEN_ENDPOINT=$(curl -s "${SERVER_METADATA_URL}" | jq -r .token_endpoint)
RESOURCE_SERVER_IDENTIFIER=$(terraform output -raw resource_server_identifier)
CLIENT_ID=$(terraform output -raw example_client_id)
CLIENT_SECRET=$(terraform output -raw example_client_secret)

curl -s "${TOKEN_ENDPOINT}" \
	-H 'Content-Type: application/x-www-form-urlencoded' \
	-d 'grant_type=client_credentials' \
	-d "scope=${RESOURCE_SERVER_IDENTIFIER}/.default" \
	-d "client_id=${CLIENT_ID}" \
	-d "client_secret=${CLIENT_SECRET}" | jq -r .access_token
