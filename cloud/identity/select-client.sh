# Configures the Auth0 Terraform provider to use the specified OAuth client
#
# See: https://registry.terraform.io/providers/auth0/auth0/latest/docs/guides/quickstart#configure-the-provider

CLIENT_NAME=Terraform

unselect_client () {
	# unset client credentials
	unset AUTH0_DOMAIN
	unset AUTH0_CLIENT_ID
	unset AUTH0_CLIENT_SECRET

	echo "Auth0 credentials unset."

	unset -f unset_client
}

if [ $# -ne 1 ]
then
	echo "Usage: source select-client.sh [<tenant-domain>]"
else
	# set client credentials
	export AUTH0_DOMAIN=$1
	APP=$(auth0 apps list --tenant "${AUTH0_DOMAIN}" --json --reveal-secrets 2>/dev/null \
		| jq ".[] | select(.name == \"${CLIENT_NAME}\") | {client_id: .client_id, client_secret: .client_secret}")
	export AUTH0_CLIENT_ID=$(echo "${APP}" | jq -r '.client_id')
	export AUTH0_CLIENT_SECRET=$(echo "${APP}" | jq -r '.client_secret')

	echo "Auth0 credentials set for tenant \"${AUTH0_DOMAIN}\"."
fi
