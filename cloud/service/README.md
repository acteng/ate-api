# Service

This root module provisions the resources required for the service.

## Environments

There are multiple environments that replicate the resources which are represented as Terraform workspaces:

* `dev`
* `test`
* `prod`

Repeat the steps below for each environment as required. The target environment is denoted as `${ENVIRONMENT}`.

## Provisioning

1. Change directory:

   ```bash
   cd cloud/service
   ```

1. Authenticate with Google Cloud:

   ```bash
   gcloud auth application-default login
   ```

1. Initialise Terraform:

   ```bash
   terraform init
   ```

1. Create a Terraform workspace for the environment:

   ```bash
   terraform workspace new ${ENVIRONMENT}
   ```

1. Enable the Google Secret Manager service:

   ```bash
   terraform plan -target google_project_service.secret_manager -out plan.out
   terraform apply plan.out
   ```

1. Create the secrets:

   ```bash
   bw get notes "API Secrets ($ENVIRONMENT)" | sh
   ```
   
1. Apply the changes:

   ```bash
   terraform apply
   ```

1. Invoke the server at:

   ```bash
   terraform output -raw url
   ```

## Configuring GitHub Actions

To configure the [CI workflow](../../.github/workflows/ci.yml) with credentials to deploy images to the service:

1. Obtain the Cloud Run service account private key:

   ```bash
   terraform output -raw github_action_deploy_private_key
   ```
   
1. [Set the GitHub Actions environment secret](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-an-environment) `GCP_CREDENTIALS_DEPLOY` to the private key
