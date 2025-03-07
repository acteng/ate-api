# Terraform backend

This root module provisions a [Cloud Storage bucket](https://cloud.google.com/storage/docs/buckets) to be used as a
[Terraform backend](https://developer.hashicorp.com/terraform/language/backend) for other root modules.

As the state for this root module cannot be easily stored within itself, we store it in a shared Bitwarden note instead.

## Provisioning

1. Change directory:

   ```bash
   cd cloud/tf-backend
   ```

1. Authenticate with Google Cloud:

   ```bash
   gcloud auth application-default login
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
