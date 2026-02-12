<!-- Sync Impact Report:
Version change: 1.0.0 -> 2.0.0
List of modified principles: All principles redefined based on the new spec for a production-grade distributed system.
Added sections: Expanded principles for Event-Driven Architecture, Dapr, Cloud Portability, Data Reliability, Observability, Security, and Code Quality.
Removed sections: All principles from v1.0.0 related to the local hackathon phase have been superseded.
Templates requiring updates:
- .specify/templates/plan-template.md ⚠ pending
- .specify/templates/spec-template.md ⚠ pending
- .specify/templates/tasks-template.md ⚠ pending
- README.md ⚠ pending
Follow-up TODOs: None.
-->

# Project Constitution: AI Todo Chatbot

## Core Philosophy: Spec-Driven Development

This project follows strict Spec-Driven Development (SDD) using the Spec-Kit Plus framework. The development flow is non-negotiable:

**Constitution → Specify → Plan → Tasks → Implement**

- No code may exist without a corresponding Task.
- No Task may exist without a parent Plan.
- No Plan may exist without a governing Specification.
- No Specification may violate this Constitution.

## System Purpose

The primary goal is to evolve the Todo Chatbot from a monolithic application into a scalable, event-driven, cloud-deployable distributed system. The system must be capable of independent service scaling and provide real-time, multi-client synchronization.

## Technology Constraints

The following technologies are mandatory. No alternatives are permitted unless this constitution is formally amended.

- **Backend Framework**: FastAPI (async-only operations).
- **ORM**: SQLModel.
- **Database**: PostgreSQL (must be compatible with Neon serverless architecture).
- **Chat System**: MCP Server + Agents SDK.
- **Runtime**: Python 3.11 or newer.
- **Containerization**: Docker.
- **Orchestration**: Kubernetes (compatible with Minikube for local development and AKS/GKE/OKE for cloud deployment).

## Architecture Principles

### 1. Event-Driven System
- **Decoupling**: Services must never depend directly on each other’s database or internal state.
- **Communication**: Cross-service communication must occur exclusively via asynchronous events or abstracted service invocation.
- **Backbone**: Kafka is the sole event backbone for inter-service communication.
- **Anonymity**: Producers of events must have no knowledge of their consumers. Consumers must be independently deployable and scalable.

### 2. Microservice Boundaries
- **Isolation**: Each business domain must be encapsulated within a distinct, isolated microservice.
- **Services**: The system will be composed of at least the following services: Chat API, Tasks, Notifications, Recurring Tasks, Audit/History, and Realtime Sync.
- **No Shared Logic**: Business logic must not be shared or duplicated across service boundaries.

### 3. Dapr Abstraction (Mandatory)
- **Sidecar Pattern**: All interactions with external infrastructure must be abstracted through a Dapr sidecar.
- **Allowed Dapr APIs**: Pub/Sub, State Management, Secret Stores, Service Invocation, and Dapr Jobs API for scheduled tasks.
- **Forbidden Patterns**: Direct SDK/client usage for Kafka, Redis, or other backing services in business logic is strictly prohibited. Hardcoded connection strings or direct service-to-service HTTP calls that bypass Dapr are forbidden.

## Cloud & Deployment Principles

- **Portability**: The system must be portable across cloud providers (Azure, Google Cloud, Oracle Cloud) and local environments (Minikube) without any code changes. Infrastructure-specific configurations must be externalized.
- **Kubernetes Readiness**: Every service must be a separate Kubernetes deployment, include mandatory liveness and readiness probes, and be configured to support Horizontal Pod Autoscaling (HPA).

## Data & Reliability Rules

- **Idempotency**: All event consumers must be idempotent.
- **Resilience**: Consumers must be designed to support retries and handle message replay without causing data corruption.
- **Durability**: No data loss is permitted during service restarts or transient failures. State changes must be backed by a persistent, versionable event log.
- **Schema Evolution**: Event schemas must be versionable to support backward and forward compatibility.

## Observability Rules

- **Standard Instrumentation**: Every service must implement structured logging (e.g., JSON), a standardized health endpoint (`/health`), and mechanisms for failure traceability.
- **Correlation**: A correlation ID must be propagated across all service calls and events to enable distributed tracing.

## Security Rules

- **Secrets Management**: Secrets, API keys, and credentials must only be stored and accessed via the configured Dapr or Kubernetes secret store.
- **No Hardcoded Credentials**: Source code must not contain any credentials.
- **Authenticated Endpoints**: All externally exposed communication endpoints must be secured and require authentication.

## Code Quality Rules

- **Asynchronous by Default**: All I/O operations must be non-blocking and use async/await patterns.
- **Strict Typing**: Python type hints are mandatory for all function signatures and variable declarations.
- **Layered Architecture**: Code must be organized into a layered architecture (e.g., API layer, Service/Application layer, Domain layer, Infrastructure layer).
- **Traceability**: Every file and significant code block must be traceable to a Task ID via comments or metadata.

## Governance

This constitution is the supreme source of truth for all engineering decisions. It overrides any conflicting requirements in specifications, plans, or tasks.

**Amendment Procedure**: Amendments require a formal proposal, review, and documented approval. All changes must be versioned.

**Versioning Policy**: This constitution follows Semantic Versioning (MAJOR.MINOR.PATCH).
*   **MAJOR**: Backward-incompatible governance/principle removals or redefinitions.
*   **MINOR**: New principle/section added or materially expanded guidance.
*   **PATCH**: Clarifications, wording, typo fixes, non-semantic refinements.

**Compliance Review**: Compliance will be periodically reviewed. Deviations must be justified and documented via an Architecture Decision Record (ADR).

**Version**: 2.0.0 | **Ratified**: 2026-02-09 | **Last Amended**: 2026-02-12
