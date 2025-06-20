resource "google_compute_global_address" "ate_api" {
  name = "ate-api"
}

resource "google_compute_managed_ssl_certificate" "ate_api" {
  name = "ate-api"

  managed {
    domains = [var.domain]
  }
}

resource "google_compute_region_network_endpoint_group" "ate_api" {
  name                  = "ate-api"
  region                = var.region
  network_endpoint_type = "SERVERLESS"

  cloud_run {
    service = var.cloud_run_service_name
  }
}

resource "google_compute_backend_service" "ate_api" {
  name                  = "ate-api"
  load_balancing_scheme = "EXTERNAL_MANAGED"

  backend {
    group = google_compute_region_network_endpoint_group.ate_api.id
  }

  log_config {
    enable = true
  }
}

resource "google_compute_url_map" "ate_api" {
  name            = "ate-api"
  default_service = google_compute_backend_service.ate_api.id
}

resource "google_compute_target_https_proxy" "ate_api_https" {
  name             = "ate-api-https"
  url_map          = google_compute_url_map.ate_api.id
  ssl_certificates = [google_compute_managed_ssl_certificate.ate_api.id]
}

resource "google_compute_global_forwarding_rule" "ate_api_https" {
  name                  = "ate-api-https"
  ip_address            = google_compute_global_address.ate_api.id
  target                = google_compute_target_https_proxy.ate_api_https.id
  port_range            = "443"
  load_balancing_scheme = "EXTERNAL_MANAGED"
}
