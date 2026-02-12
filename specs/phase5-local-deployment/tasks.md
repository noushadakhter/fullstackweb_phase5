# Phase V: Minikube Local Deployment Atomic Tasks

This document breaks down the Minikube local deployment process into atomic, testable tasks, referencing the Local Deployment Specification (`specs/phase5-local-deployment/spec.md`) and the Technical Deployment Plan (`specs/phase5-local-deployment/plan.md`).

## 1. Minikube Cluster Setup

### Task ID: MINIKUBE-SETUP-001
-   **Description:** Install Minikube and configure initial cluster settings (CPU, Memory, Disk Size, Driver).
-   **Preconditions:**
    -   Host machine with Docker installed and running.
    -   Sufficient system resources (4+ CPUs, 8GB+ RAM, 50GB+ disk space).
-   **Expected Output:**
    -   Minikube cluster running with specified resources.
    -   `kubectl` context set to Minikube.
-   **Files to Modify:** N/A (CLI commands)
-   **References:**
    -   `speckit.specify` (Section 2: Minikube Setup Requirements)
    -   `speckit.plan` (Section 2: Minikube Cluster Initialization)

### Task ID: MINIKUBE-SETUP-002
-   **Description:** Enable required Minikube addons (`ingress`, `dashboard`).
-   **Preconditions:**
    -   MINIKUBE-SETUP-001 completed.
-   **Expected Output:**
    -   `ingress` and `dashboard` addons enabled.
    -   Kubernetes dashboard accessible via `minikube dashboard`.
-   **Files to Modify:** N/A (CLI commands)
-   **References:**
    -   `speckit.specify` (Section 2: Minikube Setup Requirements)
    -   `speckit.plan` (Section 2: Minikube Cluster Initialization)

## 2. Infrastructure Deployment (Helm)

### Task ID: INFRA-DEPLOY-001
-   **Description:** Deploy PostgreSQL using its Helm chart with Minikube-specific `values.yaml`.
-   **Preconditions:**
    -   MINIKUBE-SETUP-001 completed.
    -   `helm/postgresql/values-minikube.yaml` created.
-   **Expected Output:**
    -   PostgreSQL pod running in `todo-system` namespace.
    -   PostgreSQL service accessible internally.
-   **Files to Modify:**
    -   `helm/postgresql/values-minikube.yaml`
-   **References:**
    -   `speckit.specify` (Section 3: Kubernetes Deployment Requirements)
    -   `speckit.plan` (Section 3.1: PostgreSQL)

### Task ID: INFRA-DEPLOY-002
-   **Description:** Deploy Kafka (with ZooKeeper and Schema Registry) using its Helm chart with Minikube-specific `values.yaml`.
-   **Preconditions:**
    -   MINIKUBE-SETUP-001 completed.
    -   `helm/kafka/values-minikube.yaml` created.
-   **Expected Output:**
    -   Kafka, ZooKeeper, and Schema Registry pods running in `todo-system` namespace.
    -   Kafka brokers accessible internally.
-   **Files to Modify:**
    -   `helm/kafka/values-minikube.yaml`
-   **References:**
    -   `speckit.specify` (Section 3: Kubernetes Deployment Requirements, Section 6: Kafka Local Setup)
    -   `speckit.plan` (Section 3.2: Kafka)

### Task ID: INFRA-DEPLOY-003
-   **Description:** Install Dapr Control Plane using Helm.
-   **Preconditions:**
    -   MINIKUBE-SETUP-001 completed.
    -   `helm/dapr/values-minikube.yaml` created.
-   **Expected Output:**
    -   Dapr control plane pods running in `dapr-system` namespace.
-   **Files to Modify:**
    -   `helm/dapr/values-minikube.yaml`
-   **References:**
    -   `speckit.specify` (Section 5: Dapr Installation)
    -   `speckit.plan` (Section 3.3: Dapr Control Plane)

### Task ID: INFRA-DEPLOY-004
-   **Description:** Apply Dapr component YAMLs for `pubsub-kafka-todo`, `state-postgresql-todo`, and `secretstore-kubernetes-todo`.
-   **Preconditions:**
    -   INFRA-DEPLOY-003 completed.
    -   DAPR-COMP-001, DAPR-COMP-002, DAPR-COMP-003 (from Dapr integration tasks) completed.
-   **Expected Output:**
    -   Dapr components successfully registered and visible via `dapr components -k`.
-   **Files to Modify:**
    -   `kubernetes/components/pubsub-kafka-todo.yaml`
    -   `kubernetes/components/state-postgresql-todo.yaml`
    -   `kubernetes/components/secretstore-kubernetes-todo.yaml`
-   **References:**
    -   `speckit.plan` (Section 3.4: Dapr Components)

## 3. Application Microservices Deployment (Helm)

### Task ID: APP-DEPLOY-001
-   **Description:** Create Docker images for all application microservices (backend, all consumers/workers, frontend) and load them into Minikube's Docker daemon.
-   **Preconditions:**
    -   All application code is ready to be containerized.
    -   Local `Dockerfile`s are defined for each service.
-   **Expected Output:**
    -   Docker images built and available within Minikube.
-   **Files to Modify:**
    -   `backend/Dockerfile`
    -   `frontend/Dockerfile`
    -   `backend/app/consumers/*/Dockerfile` (if separate)
-   **References:**
    -   `speckit.plan` (Section 7: Configuration for Local Development Workflow)

### Task ID: APP-DEPLOY-002
-   **Description:** Deploy the Backend (Chat API) using its Helm chart with Minikube-specific `values.yaml` and Dapr annotations.
-   **Preconditions:**
    -   INFRA-DEPLOY-004 completed.
    -   APP-DEPLOY-001 completed.
    -   `helm/backend/values-minikube.yaml` created.
-   **Expected Output:**
    -   Backend pod with Dapr sidecar running.
    -   Backend service accessible internally.
-   **Files to Modify:**
    -   `helm/backend/values-minikube.yaml`
    -   `helm/backend/templates/deployment.yaml` (for Dapr annotations)
-   **References:**
    -   `speckit.plan` (Section 4: Application Microservices Deployment, Section 5: Helm Value Configuration, Section 6: Dapr Sidecar Injection)

### Task ID: APP-DEPLOY-003
-   **Description:** Deploy all Consumer/Worker services using their respective Helm charts with Minikube-specific `values.yaml` and Dapr annotations.
-   **Preconditions:**
    -   INFRA-DEPLOY-004 completed.
    -   APP-DEPLOY-001 completed.
    -   `helm/consumer-x/values-minikube.yaml` created for each.
-   **Expected Output:**
    -   All consumer/worker pods with Dapr sidecars running.
    -   Services operating as expected (consuming messages).
-   **Files to Modify:**
    -   `helm/*/values-minikube.yaml` for each consumer/worker
    -   `helm/*/templates/deployment.yaml` for Dapr annotations
-   **References:**
    -   `speckit.plan` (Section 4, Section 5, Section 6)

### Task ID: APP-DEPLOY-004
-   **Description:** Deploy the Frontend using its Helm chart with Minikube-specific `values.yaml` and configure Ingress/NodePort for external access.
-   **Preconditions:**
    -   APP-DEPLOY-001 completed.
    -   `helm/frontend/values-minikube.yaml` created.
-   **Expected Output:**
    -   Frontend pod running.
    -   Frontend accessible via `minikube service frontend-service` or Ingress URL.
-   **Files to Modify:**
    -   `helm/frontend/values-minikube.yaml`
    -   `helm/frontend/templates/ingress.yaml` (if using Ingress)
-   **References:**
    -   `speckit.specify` (Section 7: Service Exposure Requirements)
    -   `speckit.plan` (Section 4.3: Ingress or NodePort Exposure)

## 4. Verification Checklist

### Task ID: VERIFY-001
-   **Description:** Verify all Kubernetes pods are running and healthy.
-   **Preconditions:**
    -   All deployment tasks completed.
-   **Expected Output:**
    -   `kubectl get pods -A` shows all pods in `Running` or `Completed` state.
    -   No CrashLoopBackOffs or other errors.
-   **Files to Modify:** N/A (CLI commands)
-   **References:** N/A

### Task ID: VERIFY-002
-   **Description:** Verify Dapr components are correctly installed and configured.
-   **Preconditions:**
    -   VERIFY-001 completed.
-   **Expected Output:**
    -   `dapr status -k` shows Dapr control plane healthy.
    -   `dapr components -k` shows all Dapr components present.
    -   `dapr dashboard -k` displays Dapr dashboard.
-   **Files to Modify:** N/A (CLI commands)
-   **References:**
    -   `speckit.plan` (Section 8: Service Access and Testing)

### Task ID: VERIFY-003
-   **Description:** Verify Kafka topic creation and message flow (publishers/subscribers).
-   **Preconditions:**
    -   VERIFY-001, VERIFY-002 completed.
-   **Expected Output:**
    -   Kafka topics exist.
    -   Test events published from Backend API are consumed by worker services.
-   **Files to Modify:** N/A (CLI commands, `kafka-console-consumer.sh`, `kafka-console-producer.sh` for manual tests)
-   **References:** N/A

### Task ID: VERIFY-004
-   **Description:** Verify external access to Frontend and Chat API.
-   **Preconditions:**
    -   VERIFY-001 completed.
-   **Expected Output:**
    -   Frontend loads in browser.
    -   API endpoints respond correctly.
-   **Files to Modify:** N/A (Browser, `curl` commands)
-   **References:**
    -   `speckit.specify` (Section 7: Service Exposure Requirements)
    -   `speckit.plan` (Section 8: Service Access and Testing)