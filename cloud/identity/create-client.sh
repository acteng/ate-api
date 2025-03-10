#!/bin/bash

# Creates an OAuth client for the Auth0 Terraform provider
#
# See: https://registry.terraform.io/providers/auth0/auth0/latest/docs/guides/quickstart#create-a-machine-to-machine-application

set -eo pipefail

CLIENT_NAME=Terraform

# create app
CLIENT_ID=$(auth0 apps create \
	--name "${CLIENT_NAME}" \
	--type m2m \
	--json \
	2>/dev/null \
	| jq -r '.client_id')

# get management API details
MANAGEMENT_API=$(auth0 apis list --json 2>/dev/null | jq '.[] | select(.name == "Auth0 Management API")')
MANAGEMENT_API_IDENTIFIER=$(echo "${MANAGEMENT_API}" | jq -r '.identifier')
MANAGEMENT_API_SCOPES=$(echo "${MANAGEMENT_API}" | jq -r '.scopes[].value' | jq -ncR '[inputs]')

# authorise app to use the management API
auth0 api post "client-grants" \
	--data="{\"client_id\": \"${CLIENT_ID}\", \"audience\": \"${MANAGEMENT_API_IDENTIFIER}\", \"scope\": ${MANAGEMENT_API_SCOPES}}" \
	1>/dev/null

echo "Created Auth0 app \"${CLIENT_NAME}\"."
