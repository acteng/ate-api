# Maintenance

Project dependencies should be kept up-to-date for the latest security fixes.

## Upgrading Python packages

To list Python packages that need upgrading:

```bash
pip list --outdated
```

To upgrade local packages to their latest patch versions:

```bash
make upgrade
```

To upgrade packages to their latest minor or major version:

1. Bump the package version in [pyproject.toml](../pyproject.toml) keeping the patch version zero, e.g. `~=1.2.0` to `~=1.3.0`

1. Install the upgraded packages:

   ```bash
   pip install -e .[dev]
   ```

## Upgrading Terraform

To upgrade Terraform the [latest minor version](https://developer.hashicorp.com/terraform/install#release-information):

1. For each Terraform root module in [cloud](../cloud), update the required version in `versions.tf` keeping the patch version zero:

   ```hcl
   terraform {
     required_version = "~> <version>"
     ...
   }
   ```

1. Update the Terraform version in the [CI workflow](../.github/workflows/ci.yml):

   ```yaml
   - name: Setup Terraform
     uses: hashicorp/setup-terraform@v4
     with:
       terraform_version: '~<version>'
   ```

1. Update the Terraform version in the [README](../README.md) prerequisites
