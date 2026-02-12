# Phase V: Minikube Local Deployment Technical Plan

## 1. Introduction
This document details the technical plan for deploying the Todo AI Chatbot microservices, Dapr, Kafka, and PostgreSQL within a local Minikube environment. It outlines the pod structure, service definitions, exposure mechanisms, Helm chart configurations, and Dapr sidecar injection strategy, all geared towards creating a reproducible and efficient local development and testing setup.

## 2. Minikube Cluster Initialization

-   **Command:** `minikube start --cpus 4 --memory 8192mb --disk-size 50g --driver=docker`
-   **Addons:** `minikube addons enable ingress && minikube addons enable dashboard`
-   **Local Docker Registry (Optional but Recommended):** `minikube cache add <image>:<tag>` or configure an in-cluster registry.

## 3. Core Infrastructure Deployment (Helm Charts)

All infrastructure components will be deployed using their respective Helm charts.

### 3.1 PostgreSQL
-   **Helm Chart:** Stable PostgreSQL chart (e.g., `bitnami/postgresql`).
-   **Values Configuration (`helm/postgresql/values-minikube.yaml`):**
    -   `master.persistence.enabled: true`
    -   `master.persistence.size: 10Gi` (sufficient for local)
    -   `auth.database: todo_db`
    -   `auth.username: todo_user`
    -   `auth.password: supersecret` (local only)
    -   `service.type: ClusterIP` (accessed internally by services)
-   **Deployment Command:** `helm install postgresql bitnami/postgresql -f helm/postgresql/values-minikube.yaml -n todo-system --create-namespace`

### 3.2 Kafka (with ZooKeeper and Schema Registry)
-   **Helm Chart:** Stable Kafka chart (e.g., `bitnami/kafka`).
-   **Values Configuration (`helm/kafka/values-minikube.yaml`):**
    -   `replicaCount: 1` (for brokers and ZooKeeper in Minikube)
    -   `zookeeper.replicaCount: 1`
    -   `schemaRegistry.enabled: true`
    -   `externalAccess.enabled: false`
    -   `service.type: ClusterIP`
-   **Deployment Command:** `helm install kafka bitnami/kafka -f helm/kafka/values-minikube.yaml -n todo-system`

### 3.3 Dapr Control Plane
-   **Helm Chart:** Official Dapr chart (`dapr/dapr`).
-   **Values Configuration (`helm/dapr/values-minikube.yaml`):**
    -   `global.logAsJson: true` (optional)
    -   `dapr_sidecar_injector.sidecarImage: dapr/daprd:latest` (use latest for local development)
-   **Deployment Command:** `helm install dapr dapr/dapr -n dapr-system --create-namespace -f helm/dapr/values-minikube.yaml`

### 3.4 Dapr Components (Post-Dapr Control Plane Deployment)
These will be standard Dapr component YAMLs as defined in `specs/phase5-dapr-integration/plan.md` and applied directly.

-   **`pubsub-kafka-todo.yaml`** (configured with internal Kafka broker addresses)
-   **`state-postgresql-todo.yaml`** (configured with internal PostgreSQL connection string)
-   **`secretstore-kubernetes-todo.yaml`** (default for K8s secrets)
-   **Deployment Command (example):** `kubectl apply -f kubernetes/components/pubsub-kafka-todo.yaml -n todo-apps`

## 4. Application Microservices Deployment (Helm Charts)

Each application microservice (Chat API, Recurring Task Worker, Reminder Services, Audit Service, Task Broadcaster) will have its own Helm chart.

### 4.1 Pod Structure (Example: Chat API)
-   **Application Container:** Python FastAPI application.
-   **Dapr Sidecar Container:** `daprd` injected automatically by Dapr control plane.
-   **Init Containers:** Potentially for database migrations or pre-start checks.

### 4.2 Service Definitions (Example: Chat API)
-   **Type:** `ClusterIP` for internal communication.
-   **Port:** Exposing the application port (e.g., 8000 for FastAPI).
-   **Dapr Annotations:** For sidecar injection and `app-id`, `app-port`.

### 4.3 Ingress or NodePort Exposure

For local access, `NodePort` is simpler for individual services, while `Ingress` (with `minikube addons enable ingress`) provides a more realistic routing setup.

-   **Frontend (e.g., Next.js app):**
    -   `service.type: NodePort` (for direct `minikube service frontend-service` access)
    -   OR an Ingress resource:
        ```yaml
        apiVersion: networking.k8s.io/v1
        kind: Ingress
        metadata:
          name: frontend-ingress
          namespace: todo-apps
        spec:
          rules:
          - http:
              paths:
              - path: /
                pathType: Prefix
                backend:
                  service:
                    name: frontend-service
                    port:
                      number: 3000 # Frontend service port
        ```
-   **Chat API:**
    -   `service.type: NodePort`
    -   OR an Ingress rule for `/api` path to route to the Chat API service.

## 5. Helm Value Configuration for Applications

Each application Helm chart (`helm/backend/`, `helm/frontend/`, etc.) will have a `values-minikube.yaml` override.

-   **`values-minikube.yaml` for `backend` (Chat API, Workers):**
    -   `image.repository: localhost:5000/backend` (if using local registry)
    -   `image.tag: latest`
    -   `resources.limits.cpu: 200m`, `resources.limits.memory: 512Mi` (reduced for local)
    -   `env.DAPR_HOST: "http://localhost:3500"` (if connecting from outside Dapr sidecar, otherwise not needed)
    -   `env.DATABASE_URL: "postgresql://todo_user:supersecret@postgresql.todo-system.svc.cluster.local:5432/todo_db"`
    -   `dapr.enabled: true`
    -   `dapr.appId: chat-api` (for Chat API)
    -   `dapr.appPort: 8000` (for Chat API)
    -   `dapr.config: app-config` (optional DaprConfiguration resource)

## 6. Dapr Sidecar Injection

-   **Automatic Injection:** Enabled by the Dapr control plane.
-   **Application Annotations:**
    -   `dapr.io/enabled: "true"`
    -   `dapr.io/app-id: "<unique-service-id>"`
    -   `dapr.io/app-port: "<application-listening-port>"`
    -   `dapr.io/config: "app-config"` (if using a custom DaprConfiguration)
    -   `dapr.io/log-level: "debug"` (useful for local debugging)

## 7. Configuration for Local Development Workflow

-   **Local Image Builds:** Modify `backend/Dockerfile` and `frontend/Dockerfile` for local building. Use `minikube image load <image>:<tag>` or push to Minikube's built-in registry.
-   **Hot Reloading:** For local Python development, `skaffold` or similar tools can be integrated to monitor local file changes and automatically rebuild/redeploy to Minikube for rapid iteration.
-   **Debugging:** Configure IDEs for remote debugging to pods running in Minikube.

## 8. Service Access and Testing

-   **Frontend:** `minikube service frontend-service` (if NodePort) or access via Ingress URL.
-   **Backend API:** `minikube service chat-api` (if NodePort) or access via Ingress URL `/api`.
-   **Dapr Dashboard:** `dapr dashboard -k`
-   **Kafka UI:** Deploy a Kafka UI Helm chart to Minikube (e.g., `helm install kafka-ui kafkamanager/kafka-ui -n todo-system`).

## 9. Next Steps

-   Create comprehensive Helm charts for all application microservices (backend, frontend, all consumers/workers).
-   Finalize Minikube-specific `values.yaml` overrides for all charts.
-   Develop and document a `README.md` or `SETUP.md` with step-by-step instructions for local Minikube setup and deployment.
-   Automate the local build and deploy process using scripts or `skaffold`.