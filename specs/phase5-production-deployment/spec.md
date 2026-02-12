# Phase V: Production Deployment Specification (AKS/GKE/Oracle)

## 1. Introduction
This document outlines the detailed specification for deploying the Todo AI Chatbot project to production environments on major cloud providers (Azure Kubernetes Service - AKS, Google Kubernetes Engine - GKE, or Oracle Container Engine for Kubernetes - OKE). The goal is to define robust, scalable, secure, and highly available deployment standards, integrating Dapr and Kafka, with strong emphasis on infrastructure as code, monitoring, and CI/CD.

## 2. Cluster Requirements

-   **Cloud Provider:** Deployment SHALL support AKS, GKE, or OKE. While specifications are generally cloud-agnostic where possible, cloud-specific integrations will be highlighted.
-   **Kubernetes Version:** Clusters SHALL run a supported and stable Kubernetes version (N-1 or N-2 from latest stable).
-   **Node Pools:**
    -   Multiple node pools SHALL be configured for different workloads (e.g., system services, application workloads, Kafka).
    -   Node pools SHALL use managed node groups where available (e.g., AKS Node Pools, GKE Node Pools) for automated patching and scaling.
    -   Node types SHALL be chosen based on workload requirements (e.g., compute-optimized for Kafka, general-purpose for application pods).
    -   Autoscaling SHALL be enabled for node pools.
-   **Region & Zones:** Deployment SHALL be across multiple availability zones within a single region for high availability and disaster recovery (minimum 3 zones).
-   **Private Cluster:** Clusters SHALL be private with restricted access to the Kubernetes API server endpoint (e.g., private AKS/GKE clusters).

## 3. Resource Limits & Quotas

-   **Pod Resource Limits & Requests:**
    -   All application pods and Dapr sidecars SHALL have CPU and Memory requests and limits defined based on performance testing and observed usage.
    -   These SHALL be configured within Helm charts.
-   **Namespace Resource Quotas:** Resource quotas SHALL be applied per namespace to prevent resource exhaustion and ensure fair sharing.
-   **Storage:**
    -   Managed disk types (e.g., Azure Disk, Google Persistent Disk, Oracle Block Volumes) SHALL be used for persistent storage (e.g., PostgreSQL, Kafka data).
    -   Storage classes SHALL be defined and used for dynamic provisioning.

## 4. Kafka Cloud Integration

-   **Deployment Model:**
    -   **Self-Managed Kafka:** Kafka, ZooKeeper, and Schema Registry will be deployed within the Kubernetes cluster using a Helm chart (as per Minikube setup, but scaled for production).
    -   **Managed Kafka (Alternative):** Consideration for managed Kafka services (e.g., Azure Event Hubs with Kafka API, Confluent Cloud, Aiven Kafka) for reduced operational overhead. If used, Dapr Pub/Sub component will be configured accordingly.
-   **Networking:** Kafka traffic SHALL be isolated to private networks within the cloud provider.
-   **Authentication:** mTLS between Kafka brokers and clients (Dapr sidecars) SHALL be enforced.
-   **Schema Registry:** A Schema Registry SHALL be deployed and accessible to all Kafka producers and consumers for schema validation.

## 5. Networking & Ingress

-   **Virtual Network:** Clusters SHALL reside within a dedicated virtual network (VNet/VPC) with appropriate subnets.
-   **Network Policies:** Kubernetes Network Policies SHALL be implemented to restrict pod-to-pod communication based on least privilege.
-   **Ingress Controller:** A robust Ingress Controller (e.g., NGINX Ingress, Traefik, GKE Ingress/Load Balancer) SHALL be deployed for external access.
-   **DNS:** Managed DNS services (e.g., Azure DNS, Google Cloud DNS, OCI DNS) SHALL be used for domain management.
-   **TLS Termination:** TLS termination SHALL occur at the Ingress Controller level using managed certificates (e.g., Azure Key Vault/Cert Manager, Google Managed Certificates).
-   **External Load Balancer:** A cloud-provider-managed Load Balancer SHALL front the Ingress Controller for high availability and external traffic distribution.
-   **Private Endpoints:** Where applicable, private endpoints/service endpoints SHALL be used for connecting to cloud managed services (e.g., database, managed Kafka) to keep traffic within the private network.

## 6. Security Requirements

-   **Identity and Access Management (IAM):**
    -   Kubernetes RBAC SHALL be strictly enforced with least privilege principle.
    -   Cloud IAM (e.g., Azure AD, Google Cloud IAM, OCI IAM) SHALL be integrated for cluster access and control.
    -   Service accounts SHALL be used for pods, with granular permissions.
-   **Secrets Management:**
    -   All application secrets (database credentials, API keys) SHALL be stored in a cloud-managed secrets store (e.g., Azure Key Vault, Google Secret Manager, OCI Vault) and accessed via Dapr's Secrets building block.
    -   No secrets SHALL be stored directly in source code or Kubernetes manifests.
-   **Network Security:**
    -   Firewalls, Network Security Groups (NSGs), or equivalent cloud security features SHALL restrict traffic to/from the cluster.
    -   DDoS protection SHALL be enabled for public endpoints.
-   **Container Security:**
    -   Container images SHALL be scanned for vulnerabilities as part of the CI/CD pipeline.
    -   Only trusted base images SHALL be used.
    -   Runtime security scanning (e.g., Falco) SHOULD be considered.
-   **Auditing and Logging:**
    -   All cluster activities and application logs SHALL be collected, centralized, and sent to a cloud-managed logging service (e.g., Azure Log Analytics, Google Cloud Logging, OCI Logging).
    -   Audit logs SHALL be enabled for Kubernetes API server.
-   **Compliance:** Adherence to relevant security standards and best practices (e.g., CIS Kubernetes Benchmark).

## 7. CI/CD Requirements

-   **Automated Builds:** All code changes SHALL trigger automated builds of Docker images.
-   **Automated Testing:** Unit, integration, and end-to-end tests SHALL be executed automatically in the CI pipeline.
-   **Image Scanning:** Docker images SHALL be scanned for vulnerabilities.
-   **Helm Chart Linting & Validation:** Helm charts SHALL be linted and validated.
-   **Automated Deployment:** Approved changes SHALL be automatically deployed to production via GitOps (e.g., Argo CD, Flux CD) or a robust CD pipeline.
-   **Rollback Strategy:** Automated rollback capabilities SHALL be in place for failed deployments.
-   **Environment Promotion:** A clear promotion path (Dev -> Staging -> Production) SHALL be defined and automated.
-   **Infrastructure as Code (IaC):** All infrastructure (Kubernetes cluster, networking, cloud resources) SHALL be defined and managed using IaC tools (e.g., Terraform).

## 8. Monitoring & Observability

-   **Centralized Logging:** All application and system logs collected (see Security section).
-   **Metrics:** Prometheus and Grafana (or cloud-managed alternatives like Azure Monitor, Google Cloud Monitoring) SHALL be used for collecting and visualizing metrics from Kubernetes, Dapr, Kafka, and application services.
-   **Alerting:** Alerting rules SHALL be configured for critical system health indicators (e.g., service availability, error rates, resource utilization, Dapr/Kafka lag).
-   **Tracing:** Distributed tracing (e.g., OpenTelemetry, Jaeger) SHOULD be implemented for end-to-end request visibility.

## 9. Next Steps

-   Selection of specific cloud provider (AKS, GKE, OKE) for detailed implementation.
-   Develop Terraform/ARM/Deployment Manager scripts for cloud resource provisioning.
-   Finalize Helm chart `values.yaml` for production environments.
-   Implement CI/CD pipelines for automated deployment.
-   Configure monitoring and alerting solutions.