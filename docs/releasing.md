# Releasing

## Create a release

1. Ensure all GitHub issues are closed for the milestone
1. Close the GitHub milestone for the release
1. Update the project version in [pyproject.toml](../pyproject.toml) for the release:
   ```toml
   [project]
   name = "ate-api"
   version = "<version>"
   ```
1. Tag the repository for the release:
   ```bash
   git tag <version>
   ```
1. Push the tag:
   ```bash
   git push --tags
   ```
1. Wait for the [CI](https://github.com/acteng/ate-api/actions/workflows/ci.yml) GitHub Action to build and deploy the release to Dev
1. Confirm that Dev is working as expected
1. Publish a new GitHub release:
   * Tag: `<version>`
   * Title: `<version>`
   * Description: `Completed stories: <link to milestone closed issues>`

## Deploy to Test

1. Upgrade the Test image tag in the Terraform file `cloud/service/main.tf` to the release:
   ```hcl
   locals {
     config = {
       ...
       test = {
         image_tag = "<version>"
         ...
       }
       ...
     }
   }
   ```
1. Commit the change with the message "Deploy \<version> to Test"
1. Apply Terraform infrastructure changes to Test:
   ```bash
   cd cloud/service
   terraform workspace select test
   terraform apply
   ```
1. Confirm that Test is working as expected

## Deploy to Prod

1. Upgrade the Prod image tag in the Terraform file `cloud/service/main.tf` to the release:
   ```hcl
   locals {
     config = {
       ...
       prod = {
         image_tag = "<version>"
         ...
       }
     }
   }
   ```
1. Commit the change with the message "Deploy \<version> to Prod"
1. Apply Terraform infrastructure changes to Prod:
   ```bash
   cd cloud/service
   terraform workspace select prod
   terraform apply
   ```
1. Confirm that Prod is working as expected
