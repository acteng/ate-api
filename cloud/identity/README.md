# Identity provider

This root module provisions OAuth clients for the API in [Auth0](https://auth0.com/).

## Provisioning

For each environment required (dev, test, prod):

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

## Destroying

For each environment required (dev, test, prod):

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
