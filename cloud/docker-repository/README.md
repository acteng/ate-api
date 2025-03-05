# Provision the Docker repository

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
