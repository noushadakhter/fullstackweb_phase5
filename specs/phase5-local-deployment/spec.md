# Phase V: Local Deployment Specification using Minikube

## 1. Introduction
This document specifies the requirements for a local development and testing environment using Minikube for the Todo AI Chatbot project in Phase V. The goal is to provide a comprehensive, reproducible, and easy-to-set-up environment that mirrors the production Kubernetes deployment as closely as possible, including Dapr, Kafka, and all microservices.

## 2. Minikube Setup Requirements

-   **Environment:** Developers SHALL use Minikube as the local Kubernetes cluster.
-   **Resource Allocation:** Minikube instance SHALL be configured with:
    -   Minimum 4 CPUs.
    -   Minimum 8GB RAM.
    -   Minimum 50GB disk space.
-   **Drivers:** Docker driver is preferred for Minikube for simplicity.
-   **Addons:** Minikube addons like `dashboard` and `ingress` SHALL be enabled.

## 3. Kubernetes Deployment Requirements

-   **Deployment Strategy:** All application microservices (Chat API, Recurring Task Worker, Reminder Services, Audit Service, Task Broadcaster), along with infrastructure components (Kafka, ZooKeeper, Schema Registry, PostgreSQL, Dapr Control Plane), SHALL be deployable within Minikube.
-   **Namespace Isolation:** Components SHOULD be deployed into specific namespaces (e.g., `todo-system` for infrastructure, `todo-apps` for application services) for organization and clarity.
-   **Local Registry:** Minikube's built-in Docker registry (or an external one) SHALL be used for local image builds and pushes.

## 4. Helm Chart Usage

-   **Packaging:** All deployable components (application microservices and infrastructure components like Kafka, PostgreSQL, Dapr Control Plane, Dapr components) SHALL be packaged as Helm charts.
-   **Configuration:** Helm `values.yaml` files SHALL be used to manage configuration differences between local (Minikube) and remote (production) environments, including:
    -   Image tags (local build vs. remote repository).
    -   Resource limits/requests (smaller for local).
    -   Service types (NodePort/LoadBalancer for local exposure vs. ClusterIP/LoadBalancer for production).
    -   External service endpoints (e.g., Kafka broker addresses).
-   **Dependencies:** Helm charts SHALL manage dependencies (e.g., application charts depending on Dapr, Kafka, PostgreSQL charts).

## 5. Dapr Installation

-   **Installation Method:** Dapr Control Plane SHALL be installed into Minikube using Helm.
-   **Version Control:** The Dapr version used locally SHALL match the version deployed in production.
-   **Dapr Components:** All Dapr components (`pubsub.kafka`, `state.postgresql`, `secretstores.kubernetes`) defined in the Dapr Integration Plan SHALL be deployable and functional within the Minikube environment.
-   **Sidecar Injection:** Automatic Dapr sidecar injection SHALL be enabled and functional for all application microservices.

## 6. Kafka Local Setup

-   **Deployment:** A dedicated Kafka cluster (including ZooKeeper and Schema Registry) SHALL be deployed directly into Minikube using its own Helm chart.
-   **Accessibility:** Kafka brokers SHALL be accessible from all Dapr-enabled application microservices within the Minikube cluster.
-   **Topic Creation:** A mechanism (e.g., Kubernetes Job, Helm post-install hook) SHALL be provided to automatically create all required Kafka topics (`todo.tasks.events`, `todo.reminders.events`, `todo.task_updates.broadcast`, DLQs) upon deployment.

## 7. Service Exposure Requirements

-   **Frontend Access:** The Frontend service (if applicable) SHALL be exposed locally via `minikube service frontend-service` or through an Ingress controller (configured with `minikube addons enable ingress`).
-   **Chat API Access:** The Chat API (FastAPI backend) SHALL be exposed locally to allow direct testing and interaction (e.g., via a NodePort or Ingress).
-   **Dapr Dashboard:** The Dapr Dashboard SHALL be accessible locally for monitoring Dapr components and applications.
-   **Kafka UI/Tooling:** If needed, a Kafka UI (e.g., Kowl, Kafka-UI) SHOULD be deployable within Minikube for monitoring Kafka topics and messages.

## 8. Development Workflow Integration

-   **Local Builds:** Developers SHALL be able to build Docker images of individual microservices locally and push them into the Minikube Docker daemon.
-   **Rapid Iteration:** Changes to application code SHOULD be quickly reflected in the Minikube environment (e.g., by rebuilding and redeploying specific microservice containers).
-   **Debugging:** Support for remote debugging of microservices running in Minikube SHOULD be available.

## 9. Next Steps

-   Create a comprehensive Helm chart for all application microservices.
-   Develop `values.yaml` overlays for Minikube-specific configurations.
-   Document the exact steps for setting up Minikube, deploying Dapr, Kafka, PostgreSQL, and all services.
-   Develop scripts or CI/CD pipelines to automate local deployment.