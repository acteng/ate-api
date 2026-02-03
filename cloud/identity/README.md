# Identity provider

This root module provisions OAuth clients for the API in [Auth0](https://auth0.com/).

## Environments

There are multiple environments that replicate the resources which are represented as Terraform workspaces:

* `dev`
* `test`
* `prod`

Set the target environment, for example:

```bash
export ENVIRONMENT=dev
```

Then repeat the steps below for each environment as required.

## Provisioning

### Terraform provider

To create an OAuth client for the Auth0 Terraform provider:

1. Change directory:

   ```bash
   cd cloud/identity
   ```

1. Authenticate with Auth0:

   ```bash
   auth0 login --domain ate-api-${ENVIRONMENT}.uk.auth0.com --scopes create:client_grants
   ```

1. Create an OAuth client for Terraform:

   ```bash
   ./create-client.sh
   ```

1. Log out from Auth0:

   ```bash
   auth0 logout
   ```

### Resources

1. Change directory:

   ```bash
   cd cloud/identity
   ```

1. Authenticate with Auth0:

   ```bash
   auth0 login --domain ate-api-${ENVIRONMENT}.uk.auth0.com
   ```

1. Initialise Terraform:

   ```bash
   terraform init
   ```

1. Create a Terraform workspace for the environment:

   ```bash
   terraform workspace new ${ENVIRONMENT}
   ```
   
1. Configure the Auth0 Terraform provider for the environment:

   ```bash
   source select-client.sh ate-api-${ENVIRONMENT}.uk.auth0.com
   ```
   
1. Get the Terraform variables for the environment:

   ```bash
   ./get-vars.sh ${ENVIRONMENT}
   ```

1. Apply the changes:

   ```bash
   terraform apply
   ```

1. (Dev environment only) Set the client details in Bitwarden for downstream projects:

   ```bash
   ./set-secrets.sh ${ENVIRONMENT}
   ```

1. Add a DNS record to the custom domain with details from:

   ```bash
   terraform output record
   ```

1. [Verify the custom domain](https://auth0.com/docs/customize/custom-domains/auth0-managed-certificates#verify-ownership)

1. Unset the Auth0 Terraform provider credentials:

   ```bash
   unselect_client
   ```

1. Log out from Auth0:

   ```bash
   auth0 logout
   ```

## Requesting an access token

To request an access token from the identity provider:

1. Change directory:

   ```bash
   cd cloud/identity
   ```

1. Initialise Terraform:

   ```bash
   terraform init
   ```

1. Select the Terraform workspace for the environment:

   ```bash
   terraform workspace select ${ENVIRONMENT}
   ```
   
1. Request an access token from the identity provider:

   ```bash
   ./request-access-token.sh ${ENVIRONMENT}
   ```

## Destroying

### Resources

1. Change directory:

   ```bash
   cd cloud/identity
   ```

1. Authenticate with Auth0:

   ```bash
   auth0 login --domain ate-api-${ENVIRONMENT}.uk.auth0.com
   ```

1. Initialise Terraform:

   ```bash
   terraform init
   ```

1. Select the Terraform workspace for the environment:

   ```bash
   terraform workspace select ${ENVIRONMENT}
   ```
   
1. Configure the Auth0 Terraform provider for the environment:

   ```bash
   source select-client.sh ate-api-${ENVIRONMENT}.uk.auth0.com
   ```
   
1. Remove the DNS record from the custom domain

1. Delete the resources:

   ```bash
   terraform destroy
   ```

1. Unset the Auth0 Terraform provider credentials:

   ```bash
   unselect_client
   ```

1. Log out from Auth0:

   ```bash
   auth0 logout
   ```

### Terraform provider

To delete the OAuth client for the Auth0 Terraform provider:

1. Change directory:

   ```bash
   cd cloud/identity
   ```

1. Authenticate with Auth0:

   ```bash
   auth0 login --domain ate-api-${ENVIRONMENT}.uk.auth0.com
   ```

1. Delete the OAuth client for Terraform:

   ```bash
   ./delete-client.sh
   ```

1. Log out from Auth0:

   ```bash
   auth0 logout
   ```
