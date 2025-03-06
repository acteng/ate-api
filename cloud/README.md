# Cloud infrastructure

This service is hosted on [Google Cloud Platform](https://console.cloud.google.com/).

## Prerequisites

1. Install Google Cloud CLI and authenticate using ADCs:

   ```bash
   gcloud auth application-default login
   ```

1. Install Terraform 1.11

## Provisioning

To provision the cloud infrastructure:

1. Provision the [Terraform backend](tf-backend/README.md)
1. Provision the [Docker repository](docker-repository/README.md)
1. Provision the [service](service/README.md) for each environment
