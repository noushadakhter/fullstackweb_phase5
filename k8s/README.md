# Kubernetes Manifests

This directory contains all the Kubernetes manifests required to deploy the Todo AI Chatbot application and its dependencies.

## Directory Structure

-   `00-namespace.yaml`: Defines the namespaces used by the application.
-   `infra/`: Contains manifests for infrastructure components like Kafka, Redis, and PostgreSQL. These would typically be managed by Helm charts in a real production scenario, but are provided here for clarity.
-   `services/`: Contains manifests for each application microservice (e.g., `api-gateway`, `tasks-service`).
-   `dapr/`: Contains Dapr component manifests specific to the Kubernetes environment (which may differ from local docker-compose).

## Deployment Order

1.  Apply the namespaces: `kubectl apply -f 00-namespace.yaml`
2.  Deploy infrastructure components from the `infra/` directory.
3.  Deploy Dapr components from the `dapr/` directory.
4.  Deploy application services from the `services/` directory.
