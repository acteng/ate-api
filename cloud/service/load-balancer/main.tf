locals {
  year_in_seconds = 365 * 24 * 60 * 60
}

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
  name                    = "ate-api"
  load_balancing_scheme   = "EXTERNAL_MANAGED"
  security_policy         = var.security_policy_id
  custom_response_headers = ["Strict-Transport-Security: max-age=${local.year_in_seconds}"]

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

resource "google_compute_ssl_policy" "ate_api" {
  name            = "ate-api"
  profile         = "RESTRICTED"
  min_tls_version = "TLS_1_2"
}

resource "google_compute_target_https_proxy" "ate_api_https" {
  name             = "ate-api-https"
  url_map          = google_compute_url_map.ate_api.id
  ssl_certificates = [google_compute_managed_ssl_certificate.ate_api.id]
  ssl_policy       = google_compute_ssl_policy.ate_api.id
}

resource "google_compute_global_forwarding_rule" "ate_api_https" {
  name                  = "ate-api-https"
  ip_address            = google_compute_global_address.ate_api.id
  target                = google_compute_target_https_proxy.ate_api_https.id
  port_range            = "443"
  load_balancing_scheme = "EXTERNAL_MANAGED"
}

# HTTP-to-HTTPS redirect

resource "google_compute_url_map" "ate_api_https_redirect" {
  name = "ate-api-https-redirect"

  default_url_redirect {
    https_redirect         = true
    redirect_response_code = "MOVED_PERMANENTLY_DEFAULT"
    strip_query            = false
  }
}

resource "google_compute_target_http_proxy" "ate_api_http" {
  name    = "ate-api-http"
  url_map = google_compute_url_map.ate_api_https_redirect.id
}

resource "google_compute_global_forwarding_rule" "ate_api_http" {
  name                  = "ate-api-http"
  ip_address            = google_compute_global_address.ate_api.id
  target                = google_compute_target_http_proxy.ate_api_http.id
  port_range            = "80"
  load_balancing_scheme = "EXTERNAL_MANAGED"
}
