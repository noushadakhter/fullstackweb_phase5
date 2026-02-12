---
id: 2
title: Establish v2.0.0 Constitution for Distributed System
stage: constitution
date: 2026-02-12
surface: agent
model: gemini
feature: none
branch: main
user: unknown
command: /sp.constitution Create the project constitution for a production-grade AI Todo Chatbot system built using Spec-Driven Development (Spec-Kit Plus)...
labels: [constitution, architecture, setup]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
 - .specify/templates/plan-template.md
 - .specify/templates/spec-template.md
 - .specify/templates/tasks-template.md
 - README.md
tests:
 - "none"
---

## Prompt

/sp.constitution Create the project constitution for a production-grade AI Todo Chatbot system built using Spec-Driven Development (Spec-Kit Plus).

The constitution defines NON-NEGOTIABLE engineering principles.
It must not contain feature requirements — only rules, constraints, and architectural laws that all future plans and implementations must obey.

Core Philosophy

This project follows strict Spec-Driven Development:
Constitution → Specify → Plan → Tasks → Implement

No code may exist without a task
No task may exist without a plan
No plan may exist without a specification

System Purpose

Transform a Todo Chatbot into a scalable, event-driven, cloud-deployable distributed system capable of independent service scaling and real-time multi-client synchronization.

Technology Constraints (Mandatory)

Backend: FastAPI (async only)
ORM: SQLModel
Database: PostgreSQL (Neon compatible)
Chat System: MCP Server + Agents SDK
Runtime: Python 3.11+
Containerization: Docker
Orchestration: Kubernetes (Minikube locally, AKS/GKE/OKE in cloud)

No alternative frameworks allowed unless constitution is updated.

Architecture Principles
Event-Driven System

Services must never depend directly on each other’s database

Cross-service communication must occur via events or service invocation only

Kafka is the event backbone

Producers must not know consumers

Consumers must be independently deployable

Microservice Boundaries

Each domain must be isolated:

Chat API Service

Task Service

Notification Service

Recurring Task Service

Audit/History Service

Realtime Sync Service

No shared business logic across services.

Dapr Rules (Mandatory Abstraction Layer)

All infrastructure access must go through Dapr sidecar:

Allowed:

Pub/Sub via Dapr

State via Dapr

Secrets via Dapr

Service invocation via Dapr

Scheduled jobs via Dapr Jobs API

Forbidden:

Direct Kafka clients in business logic

Hardcoded connection strings

Direct service-to-service HTTP calls bypassing Dapr

Cloud & Deployment Principles

The system must be portable across cloud providers:

Must run on Minikube without modification

Must run on AKS/GKE/OKE without code change

Infrastructure differences handled only via configuration

Kubernetes Requirements:

Each service separate deployment

Liveness & readiness probes required

Horizontal scaling supported

Data & Reliability Rules

All events must be idempotent

Consumers must support retries

No data loss allowed on restarts

State changes must be event-backed

Event schema must be versionable

Observability Rules

Every service must include:

Structured logging

Health endpoint

Failure traceability

Correlation IDs across events

Security Rules

Secrets stored only in Dapr/Kubernetes secret store

No credentials in source code

All external communication authenticated

Code Quality Rules

Async I/O only (no blocking DB calls)

Type hints mandatory

Layered architecture (API → Service → Domain → Infrastructure)

Each file traceable to a Task ID

Decision Hierarchy

Constitution overrides all other spec files

## Response snapshot

I have successfully updated the project's constitution to version 2.0.0, redefining the architecture to be a distributed, event-driven system. I also updated the README, and the plan, spec, and tasks templates to align with these new principles.

## Outcome

- ✅ Impact: Major architectural overhaul. Redefined the project's core principles to establish a distributed, event-driven microservices architecture. Updated all relevant project templates to align with the new constitution.
- 🧪 Tests: No tests were run.
- 📁 Files: Updated the constitution, README, and the plan, spec, and tasks templates.
- 🔁 Next prompts: The user can now proceed with `/sp.specify` to define features based on the new constitution.
- 🧠 Reflection: The process of updating the constitution and propagating changes to templates was successful. The manual PHR creation fallback worked as expected when the creation script was not found.

## Evaluation notes (flywheel)

- Failure modes observed: The `create-phr.sh` script was not found, requiring a manual fallback.
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): null
