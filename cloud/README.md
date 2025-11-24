# Cloud infrastructure

This service is hosted on [Google Cloud Platform](https://console.cloud.google.com/) and
[AWS](https://console.aws.amazon.com/).

## Prerequisites

1. Install [Google Cloud CLI](https://cloud.google.com/sdk/docs/install)
1. Install [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) and
   [log in](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sign-in.html)
1. Install [jq](https://jqlang.org/download/)
1. Install [Bitwarden CLI](https://bitwarden.com/help/cli/#download-and-install)

## Provisioning

To provision the cloud infrastructure:

1. Provision the [Terraform backend](tf-backend/README.md)
1. Provision the [Docker repository](docker-repository/README.md)
1. Provision the [identity provider](identity/README.md) for each environment
1. Provision the [service](service/README.md) for each environment
