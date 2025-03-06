# Cloud infrastructure

This service is hosted on [Google Cloud Platform](https://console.cloud.google.com/).

## Prerequisites

1. Install [Terraform](https://developer.hashicorp.com/terraform/install) 1.11

1. Install [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) and
   [authenticate using ADCs](https://cloud.google.com/sdk/docs/authorizing#adc):

   ```bash
   gcloud auth application-default login
   ```

## Provisioning

To provision the cloud infrastructure:

1. Provision the [Terraform backend](tf-backend/README.md)
1. Provision the [Docker repository](docker-repository/README.md)
1. Provision the [service](service/README.md) for each environment
