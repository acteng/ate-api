data "google_project" "main" {
  project_id = var.project
}

resource "google_service_account" "cloud_run_ate_api" {
  account_id = "cloud-run-ate-api"
}

resource "google_cloud_run_v2_service" "ate_api" {
  name     = "ate-api"
  project  = var.project
  location = var.region
  ingress  = "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER"

  template {
    containers {
      image = "${var.docker_repository_url}/ate-api:${var.image_tag}"
      env {
        name = "DATABASE_URL"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.database_url.id
            version = "latest"
          }
        }
      }
      env {
        name  = "OIDC_SERVER_METADATA_URL"
        value = var.oidc_server_metadata_url
      }
      env {
        name  = "RESOURCE_SERVER_IDENTIFIER"
        value = var.resource_server_identifier
      }
      ports {
        container_port = 8080
      }
    }
    containers {
      image = "gcr.io/cloud-sql-connectors/cloud-sql-proxy:2.15.2"
      args = [
        "--address=0.0.0.0",
        "--port=5432",
        var.database_connection_name,
      ]
    }
    scaling {
      min_instance_count = var.keep_idle ? 1 : 0
      max_instance_count = 10
    }
    service_account = google_service_account.cloud_run_ate_api.email
  }

  depends_on = [
    # database URL
    google_secret_manager_secret_version.database_url,
    google_secret_manager_secret_iam_member.cloud_run_ate_api_database_url,
  ]
}

resource "google_cloud_run_v2_service_iam_binding" "ate_api_run_invoker" {
  name     = google_cloud_run_v2_service.ate_api.name
  project  = var.project
  location = var.region

  role    = "roles/run.invoker"
  members = ["allUsers"]
}

resource "google_project_iam_member" "cloud_run_artifact_registry_reader" {
  project = var.docker_repository_project
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:service-${data.google_project.main.number}@serverless-robot-prod.iam.gserviceaccount.com"
}

# database

resource "google_project_iam_member" "cloud_run_ate_api_database_cloud_sql_client" {
  project = var.database_project
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.cloud_run_ate_api.email}"
}

resource "google_secret_manager_secret" "database_url" {
  secret_id = "database-url"

  replication {
    auto {
    }
  }
}

resource "google_secret_manager_secret_version" "database_url" {
  secret = google_secret_manager_secret.database_url.id
  secret_data = join("", [
    "postgresql+asyncpg://",
    var.database_username,
    ":",
    var.database_password,
    "@127.0.0.1:5432/",
    var.database_name,
  ])
}

resource "google_secret_manager_secret_iam_member" "cloud_run_ate_api_database_url" {
  member    = "serviceAccount:${google_service_account.cloud_run_ate_api.email}"
  role      = "roles/secretmanager.secretAccessor"
  secret_id = google_secret_manager_secret.database_url.id
}
