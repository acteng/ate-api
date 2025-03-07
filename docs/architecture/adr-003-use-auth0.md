# ADR-003: Use Auth0

Date: 2025-03-07

## Status

Accepted

## Context

We need to authenticate users of our API.

OAuth 2.0 is [recommended by GDS](https://www.gov.uk/guidance/gds-api-technical-and-data-standards#control-access-to-your-api)
to manage access to APIs. The [client credentials grant](https://datatracker.ietf.org/doc/html/rfc6749#section-1.3.4)
should be used for machine-to-machine authentication.

We don't want to build and maintain our own OAuth 2.0 implementation. Our cloud platform is GCP which offers various
products around authentication.

[Identity Platform](https://cloud.google.com/security/products/identity-platform) provides Customer Identity Access
Management (CIAM). It offers a delegated model of authentication with an external OpenID Connect provider, but has no
documented support for machine-to-machine authentication using the client credentials grant.

[API Gateway](https://cloud.google.com/api-gateway/docs) provides API management. It uses service accounts for
authentication but offers no authorisation server responsible for creating tokens.

[Cloud Endpoints](https://cloud.google.com/endpoints/docs/openapi) also provides API management and has similar
drawbacks to API Gateway.

[Apigee](https://cloud.google.com/apigee/docs) provides comprehensive API management. Authentication is only a small
part of its offering and the product incurs a significant complexity overhead. This solution is the preferred strategic
choice of DfTc cloud engineering.

Other clouds provide alternative products, such as [Azure AD B2C](https://learn.microsoft.com/en-us/azure/active-directory-b2c/overview)
and [AWS Cognito](https://aws.amazon.com/cognito/), but we are restricted to GCP by DfTc.

Open-source solutions such as [Keycloak](https://www.keycloak.org/) exist, but require us to host and maintain them.
Keycloak also offers a [Terraform provider](https://registry.terraform.io/providers/keycloak/keycloak/latest/docs).

SaaS solutions such as [Auth0](https://auth0.com/) provide a managed solution and are used by many other Government
departments including GDS. Auth0 also offers a [Terraform provider](https://registry.terraform.io/providers/auth0/auth0/latest/docs).

## Decision

We will use Auth0 to authenticate users of our API.

## Consequences

We don't have to build, host or maintain our own authorisation server and can use Auth0 straight away.

Auth0 implements OAuth 2.0 and allows us to switch to an alternative provider in future if required.

We can manage Auth0 infrastructure using Terraform alongside our GCP resources.
