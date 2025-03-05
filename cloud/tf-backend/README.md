# Provision the Terraform backend

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
