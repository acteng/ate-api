# ADR-001: Record architecture decisions

Date: 2025-03-03

## Status

Accepted

## Context

As the project progresses, we will make decisions that will have implications for our architecture. It is important that
we understand the reasons for these decisions in the future, so that we can understand whether they are still relevant.

Human memory is unreliable, and our team will change, so we need to document these decisions.

## Decision

We will use Architecture Decision Records, as described in Michael Nygard's
[Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) and
[suggested by GDS](https://gds-way.digital.cabinet-office.gov.uk/standards/architecture-decisions.html).

We will keep ADRs in the [docs/architecture](.) directory of this repository.

Decisions will be written using Markdown and named `adr-{number}-{title}.md`. For example,
`ADR-001-record-architecture-decisions.md`.

## Consequences

Team members will be able to view the entire decision history of our project.
