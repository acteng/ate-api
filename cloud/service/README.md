# Service

This root module provisions the resources required for the service.

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

1. Provision an IP address for the load balancer:

   ```bash
   terraform plan -target module.load_balancer.google_compute_global_address.ate_api -out plan.out
   terraform apply plan.out
   terraform output -raw ip_address
   ```

1. Update the DNS A record for the environment's domain to the IP address

1. Apply the changes:

   ```bash
   terraform apply
   ```

1. Invoke the server at:

   ```bash
   terraform output -raw url
   ```

## Configuring GitHub Actions

For the Dev environment only, configure the [CI workflow](../../.github/workflows/ci.yml) with credentials to deploy
images to the service:

1. Obtain the Cloud Run service account private key:

   ```bash
   terraform output -raw github_action_deploy_private_key
   ```
   
1. [Set the GitHub Actions environment secret](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-an-environment) `GCP_CREDENTIALS_DEPLOY` to the private key

## Redeploying

To manually redeploy the Cloud Run service using the latest image in the Docker repository:

```bash
gcloud run deploy ate-api \
    --project dft-ate-api-${ENVIRONMENT} \
    --region europe-west1 \
    --image europe-west1-docker.pkg.dev/dft-ate-api-common/docker/ate-api
```

## Destroying

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

1. Select the Terraform workspace for the environment:

   ```bash
   terraform workspace select ${ENVIRONMENT}
   ```

1. Disable deletion protection for the service by modifying `cloud/service/application/main.tf`:

   ```diff
    resource "google_cloud_run_v2_service" "ate_api" {
   +  deletion_protection = false
      ...
    }
   ```

1. Apply the change:

   ```bash
   terraform apply
   ```

1. Revert the modification:

   ```bash
   git checkout application/main.tf
   ```
   
1. Delete the resources:

   ```bash
   terraform destroy
   ```
