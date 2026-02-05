#!/bin/bash

# Sets the client details in Bitwarden for downstream projects

set -eo pipefail

if [ $# -ne 1 ]
then
	echo "Usage: set-secrets.sh <environment>"
	exit 1
fi

ENVIRONMENT=$1

bw_edit_item() {
	local ITEM_NAME=$1
	local ITEM_USERNAME=$2
	local ITEM_PASSWORD=$3

	local ITEM=$(bw get item "${ITEM_NAME}")
	local ITEM_ID=$(echo "${ITEM}" | jq -r '.id')
	echo "${ITEM}" \
		| jq --arg username "${ITEM_USERNAME}" '.login.username=$username' \
		| jq --arg password "${ITEM_PASSWORD}" '.login.password=$password' \
		| bw encode \
		| bw edit item "${ITEM_ID}"
}

bw_edit_item "uycs-ate-api-client-${ENVIRONMENT}" \
	"$(terraform output -raw update_your_capital_schemes_client_id)" \
	"$(terraform output -raw update_your_capital_schemes_client_secret)"
