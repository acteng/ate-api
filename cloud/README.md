# Cloud infrastructure

This service is hosted on [Google Cloud Platform](https://console.cloud.google.com/) and
[Microsoft Azure](https://azure.microsoft.com/).

## Prerequisites

1. Install [Google Cloud CLI](https://cloud.google.com/sdk/docs/install)
1. Install [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) and
   [log in](https://registry.terraform.io/providers/hashicorp/azuread/latest/docs/guides/azure_cli#logging-into-the-azure-cli)
1. Install [jq](https://jqlang.org/download/)
1. Install [Bitwarden CLI](https://bitwarden.com/help/cli/#download-and-install)

## Provisioning

To provision the cloud infrastructure:

1. Provision the [Terraform backend](tf-backend/README.md)
1. Provision the [Docker repository](docker-repository/README.md)
1. Provision the [identity provider](identity/README.md) for each environment
1. Provision the [service](service/README.md) for each environment
