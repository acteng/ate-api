#!/bin/bash

# Deletes the OAuth client for the Auth0 Terraform provider

set -eo pipefail

CLIENT_NAME=Terraform

# delete app
CLIENT_ID=$(auth0 apps list --json 2>/dev/null | jq -r ".[] | select(.name == \"${CLIENT_NAME}\") | .client_id")
auth0 apps delete "${CLIENT_ID}" --force 2>/dev/null

echo "Deleted Auth0 app \"${CLIENT_NAME}\"."
