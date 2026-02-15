# Phase 5: Full Advanced Cloud Deployment Specification

## 1. Overview

This specification outlines the comprehensive advanced cloud deployment for the AI Todo Chatbot project, targeting Oracle Kubernetes Engine (OKE). It integrates advanced features, event-driven architecture with Dapr and Kafka, robust CI/CD pipelines, and comprehensive monitoring and logging solutions. This document serves as an umbrella specification, referencing individual phase specifications for detailed requirements.

## 2. Goals and Objectives

*   Achieve a production-grade, scalable, and resilient deployment on OKE.
*   Fully leverage Dapr for microservices abstraction and infrastructure portability.
*   Implement event-driven communication via Kafka for decoupled services.
*   Establish automated CI/CD workflows using GitHub Actions.
*   Provide comprehensive monitoring and logging for operational visibility.
*   Ensure the project is well-documented and easily deployable by other teams.

## 3. Architecture Highlights

The deployed architecture on OKE will include:

*   **Microservices:** Frontend, API Gateway, Tasks Service, Notification Service, Audit Service, WebSocket Service, Recurring Task Service.
*   **Dapr Sidecars:** Injected into all application pods for Pub/Sub, State Management, Secrets Management, and Jobs API.
*   **Dapr Components:** Configured for Kafka (Pub/Sub), Redis (State Store), Kubernetes Secret Store, and Jobs API Scheduler.
*   **Kafka:** Self-hosted on Kubernetes using Strimzi Operator (or managed service like Redpanda Cloud).
*   **Redis:** Deployed as a state store in Kubernetes.
*   **PostgreSQL:** Deployed as the primary database in Kubernetes.
*   **Ingress Controller:** To expose the Frontend and API Gateway.
*   **Monitoring:** Prometheus for metrics collection.
*   **Logging:** Loki and Promtail for centralized log aggregation.
*   **Visualization:** Grafana for dashboards and log exploration.

## 4. Key Components and Configuration

### 4.1 Services

*   **Existing Services:**
    *   `services/frontend` (Next.js)
    *   `services/api-gateway` (Python FastAPI)
    *   `services/tasks-service` (Python FastAPI)
*   **New Services (Base Structure Created):**
    *   `services/notification-service` (Python FastAPI)
    *   `services/audit-service` (Python FastAPI)
    *   `services/websocket-service` (Python FastAPI)
    *   `services/recurring-task-service` (Python FastAPI)

### 4.2 Dapr Integration

*   **Dapr Components (YAMLs in `dapr/components/`):**
    *   `pubsub-kafka.yaml` (Kafka Pub/Sub)
    *   `statestore-redis.yaml` (Redis State Store)
    *   `secretstore-kubernetes.yaml` (Kubernetes Secrets Store for OKE)
    *   `jobs-api.yaml` (Dapr Jobs API Scheduler)
    *   `secretstore-local.yaml` (Local File Secret Store - for Minikube/local dev)
*   **Event Schemas:** Defined in `events/schemas.py` for `task-events`, `reminders`, `task-updates`.
*   **Event Publishing:** `tasks-service` publishes events (`task-events`, `reminders`, `task-updates`) via Dapr Pub/Sub.
*   **Event Subscriptions:** New services subscribe to relevant topics via Dapr Pub/Sub.

### 4.3 Kubernetes Manifests & Helm Charts

*   **Application Helm Charts (`helm/`):**
    *   Updated `helm/backend` and `helm/frontend` for Dapr sidecar injection.
    *   New charts created for `helm/notification-service`, `helm/audit-service`, `helm/websocket-service`, `helm/recurring-task-service` with Dapr integration.
*   **Infrastructure Manifests (`k8s/infrastructure/`):**
    *   Dapr Control Plane installation guide (`dapr-install-guide.md`).
    *   Strimzi Kafka deployment manifests (`strimzi-kafka/`).
    *   Redis deployment manifests (`redis/`).
    *   PostgreSQL deployment manifests (`postgresql/`).
*   **Ingress (`k8s/application/ingress.yaml`):** Configured to expose frontend and API Gateway.

### 4.4 CI/CD Pipeline

*   **GitHub Actions (`.github/workflows/`):**
    *   `ci.yaml`: Builds and pushes Docker images to GitHub Container Registry (GHCR).
    *   `cd.yaml`: Deploys to OKE, including Dapr control plane, infrastructure components, Dapr components, Helm charts, and Ingress.

### 4.5 Monitoring & Logging

*   **Prometheus:** Setup guide for Prometheus Operator (`k8s/monitoring/prometheus/install-guide.md`).
*   **Grafana:** Access guide (`k8s/monitoring/grafana/access-guide.md`).
*   **Loki & Promtail:** Installation guide for centralized logging (`k8s/monitoring/logging/install-guide.md`).

## 5. Next Steps for Implementation

*   Implement detailed business logic for advanced and intermediate features within the services.
*   Refine Dapr integration for State Management, Jobs API, and Service Invocation as features are built.
*   Add more robust monitoring configurations (e.g., ServiceMonitors for applications).
*   Complete detailed documentation and setup guides.

## 6. References

*   [Original Phase V Document](/path/to/original/phase5/document.md) (Placeholder - link to the actual document if available in repo)
*   [Project `README.md`](/README.md)
*   [AGENTS.md](/AGENTS.md)
