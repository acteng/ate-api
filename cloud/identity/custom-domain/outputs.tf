output "domain" {
  description = "Custom domain name"
  value       = auth0_custom_domain.main.domain
}

output "record" {
  description = "DNS record required to verify the custom domain"
  value = {
    type  = auth0_custom_domain.main.verification[0].methods[0].name
    name  = auth0_custom_domain.main.verification[0].methods[0].domain
    value = auth0_custom_domain.main.verification[0].methods[0].record
  }
}
