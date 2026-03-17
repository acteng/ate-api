#!/bin/bash

# Sets the environment secrets in Google Secret Manager

set -eo pipefail

if [ $# -ne 1 ]
then
	echo "Usage: set-secrets.sh <environment>"
	exit 1
fi

ENVIRONMENT=$1
PROJECT="dft-ate-api-${ENVIRONMENT}"

DOCS_ITEM=$(bw get item "ate-api-docs-${ENVIRONMENT}" || true)
if [ -n "${DOCS_ITEM}" ]; then
	echo "${DOCS_ITEM}" | jq -j '.login.username' \
		| gcloud secrets create "docs-username" --project "${PROJECT}" --data-file=-

	echo "${DOCS_ITEM}" | jq -j '.login.password' \
		| gcloud secrets create "docs-password" --project "${PROJECT}" --data-file=-
fi
