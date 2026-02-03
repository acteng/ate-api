#!/bin/bash

# Gets the Terraform variables for an environment from Bitwarden

set -eo pipefail

if [ $# -ne 1 ]
then
	echo "Usage: get-vars.sh <environment>"
	exit 1
fi

ENVIRONMENT=$1

cat <<EOS >terraform.tfvars
# Environment ${ENVIRONMENT}

example_public_key                     = <<EOF
$(bw get notes "ate-api-example-client-public-key-${ENVIRONMENT}")
EOF
update_your_capital_schemes_public_key = <<EOF
$(bw get notes "uycs-ate-api-public-key-${ENVIRONMENT}")
EOF
EOS
