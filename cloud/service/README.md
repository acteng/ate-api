# Service

This root module provisions the resources required for a service environment.

## Provisioning

For each environment required (dev, test, prod):

1. Change directory:

   ```bash
   cd cloud/service
   ```

1. Initialise Terraform:

   ```bash
   terraform init
   ```

1. Create a Terraform workspace for the environment:

   ```bash
   terraform workspace new $ENVIRONMENT
   ```

1. Apply the changes:

   ```bash
   terraform apply
   ```

1. Invoke the server:

   ```bash
   curl $(terraform output -raw url)
   ```

## Configuring GitHub Actions

To configure the [CI workflow](../../.github/workflows/ci.yml) with credentials to push deploy images to the service:

1. Obtain the Cloud Run service account private key:

   ```bash
   terraform output -raw github_action_deploy_private_key
   ```
   
1. [Set the GitHub Actions environment secret](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-an-environment) `GCP_CREDENTIALS_DEPLOY` to the private key
