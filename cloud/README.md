## Provisioning infrastructure

### Provision the Terraform backend

1. Change directory:

   ```bash
   cd cloud/tf-backend
   ```

1. Initialise Terraform:

   ```bash
   terraform init
   ```

1. Fetch the previous Terraform state from Bitwarden, if any:

   ```bash
   bw get notes "API tf-backend State" > terraform.tfstate
   ```

1. Apply the changes:

   ```bash
   terraform apply
   ```

1. Store the new Terraform state in Bitwarden as "API tf-backend State"

### Provision the Docker repository

1. Change directory:

   ```bash
   cd cloud/docker-repository
   ```

1. Initialise Terraform:

   ```bash
   terraform init
   ```

1. Apply the changes:

   ```bash
   terraform apply
   ```

1. Obtain the Docker repository service account private key:

   ```bash
   terraform output -raw github_action_push_private_key
   ```
   
1. [Set the GitHub Actions repository secret](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository) `GCP_CREDENTIALS_PUSH` to the private key

### Provision the service

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

1. Obtain the Cloud Run service account private key:

   ```bash
   terraform output -raw github_action_deploy_private_key
   ```
   
1. [Set the GitHub Actions environment secret](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-an-environment) `GCP_CREDENTIALS_DEPLOY` to the private key

1. Invoke the server:

   ```bash
   curl $(terraform output -raw url)
   ```
