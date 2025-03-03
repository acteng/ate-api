# ADR-002: Use FastAPI

Date: 2025-03-03

## Status

Accepted

## Context

We need to choose a framework to implement the ATE API.

The OpenAPI specification is [recommended by GDS](https://www.gov.uk/guidance/gds-api-technical-and-data-standards#develop-a-specification-before-you-start-to-code)
as a standardised way to document web APIs.

The two main approaches for OpenAPI development are spec-first or code-first. Spec-first centres development on the
OpenAPI specification, generating code at build-time. Code-first centres development on the implementation, generating
the OpenAPI specification at runtime.

Our existing digital services are written in Python and use the [Flask web framework](https://flask.palletsprojects.com/en/stable/).
Flask supports [testing using pytest](https://flask.palletsprojects.com/en/stable/testing/).

## Decision

We will use [FastAPI](https://fastapi.tiangolo.com/) to implement this project in a code-first approach.

## Consequences

FastAPI complements our existing Python stack and shares similarities with Flask.

It provides a framework specifically for developing APIs and supports a code-first approach by
[generating the OpenAPI specification](https://fastapi.tiangolo.com/tutorial/first-steps/#check-the-openapijson) at
runtime. Other frameworks, such as Flask, rely on extensions like [Flask-RESTful](https://flask-restful.readthedocs.io/en/latest/)
to support API development. Similarly, with [Django](https://www.djangoproject.com/) and [Django REST](https://www.django-rest-framework.org/).

FastAPI also supports [testing using pytest](https://fastapi.tiangolo.com/tutorial/testing/).

As a Python framework, we will be able to reuse existing cloud infrastructure patterns from our digital services.
