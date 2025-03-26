# Cloud infrastructure

This service is hosted on [Google Cloud Platform](https://console.cloud.google.com/).

## Prerequisites

1. Install [Google Cloud CLI](https://cloud.google.com/sdk/docs/install)
1. Install [Auth0 CLI](https://auth0.github.io/auth0-cli/)
1. Install [jq](https://jqlang.org/download/)
1. Install [Bitwarden CLI](https://bitwarden.com/help/cli/#download-and-install)

## Provisioning

To provision the cloud infrastructure:

1. Provision the [Terraform backend](tf-backend/README.md)
1. Provision the [Docker repository](docker-repository/README.md)
1. Provision the [identity provider](identity/README.md)
1. Provision the [service](service/README.md) for each environment
