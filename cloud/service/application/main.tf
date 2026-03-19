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

  scaling {
    min_instance_count = var.keep_idle ? 1 : 0
    max_instance_count = 10
  }

  template {
    service_account = google_service_account.cloud_run_ate_api.email

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
      dynamic "env" {
        for_each = var.docs_auth ? [1] : []
        content {
          name = "DOCS_USERNAME"
          value_source {
            secret_key_ref {
              secret  = data.google_secret_manager_secret.docs_username[0].secret_id
              version = "latest"
            }
          }
        }
      }
      dynamic "env" {
        for_each = var.docs_auth ? [1] : []
        content {
          name = "DOCS_PASSWORD"
          value_source {
            secret_key_ref {
              secret  = data.google_secret_manager_secret.docs_password[0].secret_id
              version = "latest"
            }
          }
        }
      }
      ports {
        container_port = 8080
      }
    }

    containers {
      image = "gcr.io/cloud-sql-connectors/cloud-sql-proxy:2.21.0"
      args = [
        "--address=0.0.0.0",
        "--port=5432",
        var.database_connection_name,
      ]
    }
  }

  depends_on = [
    # database URL
    google_secret_manager_secret_version.database_url,
    google_secret_manager_secret_iam_member.cloud_run_ate_api_database_url,
    # docs username
    google_secret_manager_secret_iam_member.cloud_run_ate_api_docs_username,
    # docs password
    google_secret_manager_secret_iam_member.cloud_run_ate_api_docs_password,
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

# docs username

data "google_secret_manager_secret" "docs_username" {
  count = var.docs_auth ? 1 : 0

  secret_id = "docs-username"
}

resource "google_secret_manager_secret_iam_member" "cloud_run_ate_api_docs_username" {
  count = var.docs_auth ? 1 : 0

  member    = "serviceAccount:${google_service_account.cloud_run_ate_api.email}"
  role      = "roles/secretmanager.secretAccessor"
  secret_id = data.google_secret_manager_secret.docs_username[0].id
}

# docs password

data "google_secret_manager_secret" "docs_password" {
  count = var.docs_auth ? 1 : 0

  secret_id = "docs-password"
}

resource "google_secret_manager_secret_iam_member" "cloud_run_ate_api_docs_password" {
  count = var.docs_auth ? 1 : 0

  member    = "serviceAccount:${google_service_account.cloud_run_ate_api.email}"
  role      = "roles/secretmanager.secretAccessor"
  secret_id = data.google_secret_manager_secret.docs_password[0].id
}

# monitoring

resource "google_monitoring_uptime_check_config" "application" {
  count = var.monitoring ? 1 : 0

  display_name = "Application uptime check"
  timeout      = "60s"
  period       = "300s"

  http_check {
    use_ssl = true
    path    = "/docs"
  }

  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project
      host       = var.domain
    }
  }
}

resource "google_monitoring_notification_channel" "email" {
  count = var.monitoring ? 1 : 0

  display_name = "ATE API support email"
  type         = "email"
  labels = {
    email_address = "api@activetravelengland.gov.uk"
  }
}

resource "google_monitoring_alert_policy" "application_uptime" {
  count = var.monitoring ? 1 : 0

  display_name = "Application uptime alert"
  combiner     = "OR"

  conditions {
    display_name = "Uptime check failed"

    condition_threshold {
      filter = join("", [
        "metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\" ",
        "AND metric.label.check_id=\"${google_monitoring_uptime_check_config.application[0].uptime_check_id}\" ",
        "AND resource.type=\"uptime_url\""
      ])
      duration        = "300s"
      comparison      = "COMPARISON_LT"
      threshold_value = "1"

      trigger {
        count = 1
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email[0].id]
  severity              = "CRITICAL"

  lifecycle {
    replace_triggered_by = [google_monitoring_uptime_check_config.application[0].uptime_check_id]
  }
}

resource "google_monitoring_alert_policy" "application_error" {
  count = var.monitoring ? 1 : 0

  display_name = "Application error alert"
  combiner     = "OR"

  conditions {
    display_name = "Cloud Run error"

    condition_matched_log {
      filter = join("", [
        "resource.type=\"cloud_run_revision\" ",
        "AND severity>=ERROR"
      ])
    }
  }

  notification_channels = [google_monitoring_notification_channel.email[0].id]

  alert_strategy {
    notification_rate_limit {
      period = "300s"
    }
  }

  severity = "ERROR"
}
