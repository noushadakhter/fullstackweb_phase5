# Phase V: Cloud Deployment Architecture Plan (AKS/GKE/Oracle)

## 1. Introduction
This plan details the technical architecture for deploying the Todo AI Chatbot project to a production-grade Kubernetes cluster on a major cloud provider (AKS, GKE, or OKE), based on the specifications in `specs/phase5-production-deployment/spec.md`. It outlines the Kubernetes topology, namespace structure, integration with managed services for Kafka and PostgreSQL, Dapr component deployment, scaling strategies, and observability design.

## 2. Kubernetes Cluster Topology

-   **Cloud Provider:** The specific cloud provider will be chosen based on project requirements, but the architecture will be largely cloud-agnostic.
-   **Private Cluster:** The cluster will be private, with no public IP for the Kubernetes API server. Access will be managed via a bastion host or private network peering.
-   **Node Pools:**
    -   **`system-pool`:** For Kubernetes system components, Dapr control plane, Ingress controller, and monitoring agents.
    -   **`apps-pool`:** For stateless application microservices (Chat API, Frontend, consumer services).
    -   **`db-pool`:** (If deploying PostgreSQL self-managed) A dedicated pool with high-IOPS storage for the database.
-   **Multi-AZ Deployment:** Node pools will be spread across at least three availability zones for high availability.

## 3. Namespace Structure

-   **`dapr-system`:** For Dapr control plane pods.
-   **`monitoring`:** For Prometheus, Grafana, and other observability components.
-   **`ingress-nginx`:** For the NGINX Ingress controller.
-   **`todo-apps`:** For all application microservices (Chat API, Frontend, consumers).
-   **`infra-services`:** (If self-managed) For PostgreSQL, Kafka, and Schema Registry.

## 4. Managed Services Integration

### 4.1 Managed PostgreSQL
-   **Service:** Utilize a managed PostgreSQL service (e.g., Azure Database for PostgreSQL, Google Cloud SQL, OCI PostgreSQL).
-   **Connectivity:** Connect from the Kubernetes cluster via a private endpoint to keep traffic within the virtual network.
-   **Authentication:** Retrieve the database connection string from a cloud-managed secrets store (e.g., Azure Key Vault, Google Secret Manager) via Dapr's Secrets API.

### 4.2 Managed Kafka Service Integration
-   **Service:** Utilize a managed Kafka service (e.g., Azure Event Hubs with Kafka API, Confluent Cloud on Azure/GCP, Aiven Kafka).
-   **Connectivity:** Connect via a private endpoint.
-   **Dapr Pub/Sub Component (`pubsub.kafka`):** The Dapr component will be configured with the managed Kafka brokers, credentials, and SASL/TLS settings. Credentials will be loaded from a cloud-managed secrets store via Dapr's Secrets API.
    ```yaml
    # Conceptual pubsub.kafka component for Managed Kafka
    apiVersion: dapr.io/v1alpha1
    kind: Component
    metadata:
      name: pubsub-kafka-todo
      namespace: todo-apps
    spec:
      type: pubsub.kafka
      version: v1
      metadata:
      - name: brokers
        value: "managed-kafka-broker-1:9092,managed-kafka-broker-2:9092"
      - name: authType
        value: "sasl_ssl"
      - name: saslMechanism
        value: "PLAIN"
      - name: saslUsername
        value: "managed-kafka-user"
      - name: saslPassword
        secretKeyRef:
          name: managed-kafka-secret # Kubernetes Secret for Dapr to access
          key: saslPassword
      # ... other managed Kafka settings
    ```

## 5. Dapr Component Deployment

-   **Dapr Control Plane:** Deployed via Helm into the `dapr-system` namespace.
-   **Dapr Application Components:** Deployed into the `todo-apps` namespace.
    -   **`pubsub-kafka-todo.yaml`:** Configured to connect to the managed Kafka service.
    -   **`state-postgresql-todo.yaml`:** Configured to connect to the managed PostgreSQL service.
    -   **`secretstore-cloud.yaml`:** This component will replace the Kubernetes secret store for production, configured to connect to the cloud provider's native secrets manager (e.g., `secretstores.azure.keyvault`, `secretstores.gcp.secretmanager`).
        ```yaml
        # Conceptual secretstore component for Azure Key Vault
        apiVersion: dapr.io/v1alpha1
        kind: Component
        metadata:
          name: secretstore-cloud
          namespace: todo-apps
        spec:
          type: secretstores.azure.keyvault
          version: v1
          metadata:
          - name: vaultName
            value: "todo-production-kv"
        ```

## 6. Scaling Strategy

-   **Horizontal Pod Autoscaler (HPA):**
    -   **Stateless Services (Chat API, Frontend, Consumers):** HPAs will be configured for each deployment based on CPU and Memory utilization.
    -   **Consumer Services:** HPAs for consumer services will also be triggered by custom metrics, specifically Kafka consumer lag, exposed via a Prometheus adapter. This ensures that consumers scale up when message processing falls behind.
-   **Cluster Autoscaler:** The Kubernetes Cluster Autoscaler will be configured to automatically add or remove nodes from node pools based on pod scheduling demands (e.g., if HPA scales pods beyond current node capacity).
-   **Kafka Partitions:** The number of partitions for Kafka topics will be a key factor in consumer scalability. A higher number of partitions allows for more consumer pods to process messages in parallel. This will be tuned based on load testing.

## 7. Observability Design

-   **Logging:**
    -   **Agent:** Fluentd or a similar log forwarding agent will be deployed as a DaemonSet to collect container logs from all nodes.
    -   **Destination:** Logs will be forwarded to a centralized cloud logging service (e.g., Azure Log Analytics, Google Cloud Logging) for analysis and long-term storage.
-   **Metrics:**
    -   **Agent:** Prometheus will be deployed to scrape metrics from:
        -   Kubernetes API server and nodes.
        -   Dapr control plane and sidecars (which expose Prometheus metrics).
        -   Kafka brokers (if self-managed) or managed Kafka service metrics.
        -   Application services (via a Prometheus client library).
    -   **Visualization:** Grafana will be used for creating dashboards to visualize these metrics.
-   **Tracing:**
    -   **Agent:** OpenTelemetry Collector will be deployed to receive traces from Dapr-instrumented applications. Dapr will be configured to automatically generate trace contexts and export them.
    -   **Backend:** Jaeger or a cloud-managed tracing service (e.g., Azure Application Insights, Google Cloud Trace) will be used to store and visualize distributed traces.

## 8. CI/CD and GitOps

-   **CI (e.g., GitHub Actions, Azure DevOps, Jenkins):**
    -   On every merge to `main`, the CI pipeline will build, test, and scan the Docker image.
    -   The image will be pushed to a cloud container registry (e.g., Azure Container Registry, Google Artifact Registry).
-   **CD (GitOps - Argo CD/Flux CD):**
    -   A GitOps controller will monitor a dedicated Git repository containing the Kubernetes manifests (Helm charts and `values.yaml`).
    -   The CI pipeline will update the image tag in this Git repository.
    -   The GitOps controller will detect the change and automatically sync the new application version to the production cluster, ensuring the cluster state matches the Git repository.
    -   This provides a declarative, auditable, and easily-revertible deployment process.

## 9. Next Steps

-   **Infrastructure as Code (IaC):** Develop Terraform scripts to provision the Kubernetes cluster, virtual network, managed PostgreSQL, and managed Kafka service.
-   **Helm Charts:** Finalize production `values.yaml` for all application and infrastructure Helm charts.
-   **CI/CD Pipeline:** Implement the described CI/CD pipeline using the chosen tools.
-   **GitOps Configuration:** Set up Argo CD or Flux CD to manage deployments.
-   **Monitoring Dashboards:** Create Grafana dashboards for key application and system metrics.
-   **Load Testing:** Perform comprehensive load testing to fine-tune resource limits, autoscaling parameters, and Kafka partition counts.