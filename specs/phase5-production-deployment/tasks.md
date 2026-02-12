# Phase V: Cloud Deployment Actionable Tasks

This document breaks down the cloud deployment architecture plan into actionable tasks, referencing the Production Deployment Specification (`specs/phase5-production-deployment/spec.md`) and the Cloud Deployment Architecture Plan (`specs/phase5-production-deployment/plan.md`). These tasks are structured for execution in a production environment (AKS/GKE/Oracle).

## 1. Cloud Infrastructure Provisioning (IaC)

### Task ID: INFRA-001
-   **Description:** Provision the Kubernetes cluster (AKS/GKE/OKE) and its associated networking (VNet/VPC, subnets, Network Security Groups, Ingress Load Balancer).
-   **Preconditions:**
    -   Cloud account configured with necessary permissions.
    -   Terraform/ARM/Deployment Manager scripts created.
-   **Expected Output:**
    -   A fully functional Kubernetes cluster deployed across multiple AZs.
    -   Associated virtual network, subnets, and security groups configured.
    -   External Load Balancer provisioned.
-   **Files to Modify:**
    -   `infrastructure/terraform/main.tf` (or equivalent IaC files)
-   **References:**
    -   `speckit.specify` (Section 2: Cluster Requirements, Section 5: Networking & Ingress)
    -   `speckit.plan` (Section 2: Kubernetes Cluster Topology)

### Task ID: INFRA-002
-   **Description:** Provision managed PostgreSQL service.
-   **Preconditions:**
    -   INFRA-001 completed.
    -   Terraform/ARM/Deployment Manager scripts created.
-   **Expected Output:**
    -   Managed PostgreSQL instance provisioned.
    -   Private endpoint configured for secure access from Kubernetes.
-   **Files to Modify:**
    -   `infrastructure/terraform/postgresql.tf`
-   **References:**
    -   `speckit.specify` (Section 3: Resource Limits & Quotas)
    -   `speckit.plan` (Section 4.1: Managed PostgreSQL)

### Task ID: INFRA-003
-   **Description:** Provision managed Kafka service (e.g., Event Hubs, Confluent Cloud) or self-managed Kafka cluster within Kubernetes.
-   **Preconditions:**
    -   INFRA-001 completed.
    -   Terraform/ARM/Deployment Manager scripts created (for managed service) OR Helm chart for self-managed Kafka.
-   **Expected Output:**
    -   Managed Kafka service provisioned OR self-managed Kafka cluster deployed in Kubernetes.
    -   Private endpoint configured (if managed).
-   **Files to Modify:**
    -   `infrastructure/terraform/kafka.tf` (or `helm/kafka/*.yaml` for self-managed)
-   **References:**
    -   `speckit.specify` (Section 4: Kafka Cloud Integration)
    -   `speckit.plan` (Section 4.2: Managed Kafka Service Integration)

### Task ID: INFRA-004
-   **Description:** Configure cloud-managed secrets store (e.g., Azure Key Vault, Google Secret Manager, OCI Vault) and populate with initial secrets.
-   **Preconditions:**
    -   INFRA-001 completed.
    -   Terraform/ARM/Deployment Manager scripts created.
-   **Expected Output:**
    -   Cloud secrets store provisioned.
    -   Initial secrets (e.g., DB connection strings, Kafka credentials) securely stored.
-   **Files to Modify:**
    -   `infrastructure/terraform/secrets.tf`
-   **References:**
    -   `speckit.specify` (Section 6: Security Requirements)
    -   `speckit.plan` (Section 5: Dapr Component Deployment - `secretstore-cloud.yaml`)

## 2. Kubernetes Configuration and Dapr Deployment

### Task ID: K8S-CONFIG-001
-   **Description:** Configure `kubectl` access to the newly provisioned Kubernetes cluster.
-   **Preconditions:**
    -   INFRA-001 completed.
-   **Expected Output:**
    -   `kubectl` commands successfully execute against the production cluster.
-   **Files to Modify:** N/A (CLI commands)
-   **References:** N/A

### Task ID: DAPR-DEPLOY-001
-   **Description:** Install Dapr Control Plane into the Kubernetes cluster using Helm.
-   **Preconditions:**
    -   K8S-CONFIG-001 completed.
    -   Production `helm/dapr/values.yaml` prepared.
-   **Expected Output:**
    -   Dapr control plane pods running in `dapr-system` namespace.
-   **Files to Modify:**
    -   `helm/dapr/values.yaml` (production specific)
-   **References:**
    -   `speckit.plan` (Section 5: Dapr Component Deployment)

### Task ID: DAPR-DEPLOY-002
-   **Description:** Apply Dapr component YAMLs for production (`pubsub-kafka-todo`, `state-postgresql-todo`, `secretstore-cloud`).
-   **Preconditions:**
    -   DAPR-DEPLOY-001 completed.
    -   INFRA-002, INFRA-003, INFRA-004 completed (managed services ready).
-   **Expected Output:**
    -   Dapr components successfully deployed and configured to use managed services.
    -   Visible via `dapr components -k`.
-   **Files to Modify:**
    -   `kubernetes/components/pubsub-kafka-todo.yaml`
    -   `kubernetes/components/state-postgresql-todo.yaml`
    -   `kubernetes/components/secretstore-cloud.yaml`
-   **References:**
    -   `speckit.plan` (Section 5: Dapr Component Deployment)

## 3. Application Deployment (Helm)

### Task ID: APP-DEPLOY-PROD-001
-   **Description:** Deploy all application microservices (backend, frontend, consumers/workers) using their respective Helm charts.
-   **Preconditions:**
    -   DAPR-DEPLOY-002 completed.
    -   Docker images built and pushed to cloud container registry.
    -   Production `helm/*/values.yaml` prepared for all services.
-   **Expected Output:**
    -   All application pods with Dapr sidecars running in `todo-apps` namespace.
    -   Dapr sidecar injection successful.
-   **Files to Modify:**
    -   `helm/*/values.yaml` (production specific for all apps)
-   **References:**
    -   `speckit.specify` (Section 3: Resource Limits & Quotas)
    -   `speckit.plan` (Section 2: Kubernetes Cluster Topology, Section 6: Scaling Strategy)

## 4. Post-Deployment Configuration & Verification

### Task ID: POST-DEPLOY-001
-   **Description:** Configure Kubernetes Network Policies for inter-service communication and external access.
-   **Preconditions:**
    -   APP-DEPLOY-PROD-001 completed.
-   **Expected Output:**
    -   Network policies applied, restricting unauthorized traffic.
-   **Files to Modify:**
    -   `kubernetes/network-policies/*.yaml` (new)
-   **References:**
    -   `speckit.specify` (Section 5: Networking & Ingress, Section 6: Security Requirements)

### Task ID: VERIFY-PROD-001 (Smoke Testing)
-   **Description:** Perform smoke tests to verify core application functionality and infrastructure connectivity.
-   **Preconditions:**
    -   All previous deployment tasks completed.
-   **Expected Output:**
    -   Frontend accessible.
    -   Key API endpoints respond correctly.
    -   Tasks can be created, updated, and retrieved.
    -   Basic Kafka message flow observed (e.g., by checking consumer logs).
-   **Files to Modify:** N/A (Automated tests, manual checks)
-   **References:** N/A

### Task ID: VERIFY-PROD-002
-   **Description:** Verify monitoring and logging systems are collecting data from the deployed services.
-   **Preconditions:**
    -   Monitoring agents/tools deployed.
-   **Expected Output:**
    -   Logs from all services appearing in centralized logging.
    -   Metrics being collected and visible in dashboards (Grafana/Cloud Monitoring).
    -   Alerts are configured and functional.
-   **Files to Modify:** N/A (Monitoring dashboards, alerting rules)
-   **References:**
    -   `speckit.specify` (Section 6: Security Requirements - Auditing and Logging)
    -   `speckit.plan` (Section 7: Observability Design)

## 5. CI/CD Pipeline Implementation

### Task ID: CICD-001
-   **Description:** Implement and configure the Continuous Integration (CI) pipeline for building, testing, and image scanning.
-   **Preconditions:**
    -   All application code committed to Git repository.
    -   Cloud container registry configured.
-   **Expected Output:**
    -   CI pipeline successfully builds Docker images, runs tests, scans images, and pushes to registry.
-   **Files to Modify:**
    -   `.github/workflows/ci.yaml` (or equivalent CI pipeline definition)
-   **References:**
    -   `speckit.specify` (Section 7: CI/CD Requirements)

### Task ID: CICD-002
-   **Description:** Implement and configure the Continuous Deployment (CD) pipeline (GitOps with Argo CD/Flux CD) for automated deployment to production.
-   **Preconditions:**
    -   CICD-001 completed.
    -   GitOps controller (Argo CD/Flux CD) deployed to cluster.
-   **Expected Output:**
    -   Changes merged to `main` trigger automated deployment to production.
    -   Rollback mechanism is functional.
-   **Files to Modify:**
    -   `infrastructure/gitops-repo/app-of-apps.yaml` (or equivalent GitOps manifest)
    -   `infrastructure/gitops-repo/applications/*.yaml`
-   **References:**
    -   `speckit.specify` (Section 7: CI/CD Requirements)
    -   `speckit.plan` (Section 8: CI/CD and GitOps)