# L2Sec

L2Sec is a local-first PTaaS/DAST platform for DevSecOps teams.

## Core Principle

The SaaS control plane orchestrates scans, but scanning runs locally inside the customer's environment.

## Security Principles

- Zero code egress
- Zero secret egress
- Local scan execution
- Sanitized findings by default
- Metadata-only mode for regulated environments
- Runner-based architecture

## MVP Scope

- FastAPI control plane
- PostgreSQL
- Local runner
- OWASP ZAP baseline scan
- Sanitized findings
- CI/CD quality gate

## Day 1 Run

```bash
docker compose up --build