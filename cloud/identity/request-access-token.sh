#!/bin/bash

# Requests an access token from the identity provider

set -eo pipefail

if [ $# -ne 1 ]
then
	echo "Usage: request-access-token.sh <environment>"
	exit 1
fi

ENVIRONMENT=$1

SERVER_METADATA_URL=$(terraform output -raw oidc_server_metadata_url)
ISSUER=$(terraform output -raw issuer)
TOKEN_ENDPOINT=$(curl -s "${SERVER_METADATA_URL}" | jq -r .token_endpoint)
RESOURCE_SERVER_IDENTIFIER=$(terraform output -raw resource_server_identifier)
CLIENT_ID=$(terraform output -raw example_client_id)

JWT_HEADER=$(echo -n '{"alg": "RS256"}' \
	| basenc --base64url --wrap=0 \
	| tr -d '=')

ISSUED_AT=$(date +%s)
JWT_PAYLOAD=$((basenc --base64url --wrap=0 | tr -d '=') <<EOF
{
	"iss": "${CLIENT_ID}",
	"sub": "${CLIENT_ID}",
	"aud": "${ISSUER}",
	"iat": ${ISSUED_AT},
	"exp": $((${ISSUED_AT} + 60)),
	"jti": "$(uuidgen)"
}
EOF
)

PRIVATE_KEY=$(bw get notes "ate-api-example-private-key-${ENVIRONMENT}")
JWT_SIGNATURE=$(echo -n "${JWT_HEADER}.${JWT_PAYLOAD}" \
	| openssl dgst -sha256 -sign <(echo -n "${PRIVATE_KEY}") \
	| basenc --base64url --wrap=0 \
	| tr -d '=')

CLIENT_ASSERTION="${JWT_HEADER}.${JWT_PAYLOAD}.${JWT_SIGNATURE}"

curl -s "${TOKEN_ENDPOINT}" \
	-H 'Content-Type: application/x-www-form-urlencoded' \
	-d 'grant_type=client_credentials' \
	-d "audience=${RESOURCE_SERVER_IDENTIFIER}" \
	-d 'client_assertion_type=urn:ietf:params:oauth:client-assertion-type:jwt-bearer' \
	-d "client_assertion=${CLIENT_ASSERTION}" | jq -r .access_token
