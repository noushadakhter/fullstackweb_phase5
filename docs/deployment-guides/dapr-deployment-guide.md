# Deploying Dapr Control Plane and Components

This guide covers the installation of the Dapr control plane on Kubernetes and the deployment of Dapr components for your application.

## 1. Dapr Control Plane Installation

Dapr is installed on your Kubernetes cluster using Helm.

### Prerequisites

*   A Kubernetes cluster (e.g., OKE)
*   `kubectl` configured to connect to your cluster
*   `helm` CLI installed

### Installation Steps

1.  **Add Dapr Helm repository:**
    ```bash
    helm repo add dapr https://dapr.github.io/helm-charts/
    helm repo update
    ```

2.  **Create a namespace for Dapr (optional, but recommended):**
    ```bash
    kubectl create namespace dapr-system
    ```

3.  **Install Dapr control plane:**
    Install the latest version of Dapr. It's recommended to install Dapr into its own dedicated `dapr-system` namespace.
    ```bash
    helm install dapr dapr/dapr --namespace dapr-system --version 1.12.0 # Use the desired Dapr version
    ```
    *Note: Replace `1.12.0` with the latest stable Dapr version if available.*

4.  **Verify Dapr installation:**
    Check that the Dapr control plane pods are running:
    ```bash
    kubectl get pods --namespace dapr-system
    ```
    You should see pods like `dapr-operator`, `dapr-placement`, `dapr-sentry`, and `dapr-sidecar-injector` in a `Running` state.

## 2. Dapr Components Deployment

After the Dapr control plane is installed, deploy the Dapr components (Pub/Sub, State Store, Secret Store, Jobs API) that your application services will use. These components are defined in the `dapr/components/` directory of this project.

### Deployment Steps

Navigate to your project's root directory:
```bash
cd your-project-root
```

Then apply the Dapr component YAML files:
```bash
kubectl apply -f dapr/components/
```
This will deploy the following components:
*   `pubsub-broker` (Kafka Pub/Sub)
*   `statestore` (Redis State Store)
*   `kubernetes-secrets` (Kubernetes Secret Store)
*   `scheduler` (Dapr Jobs API)
*   `local-secret-store` (Local File Secret Store - primarily for local dev)

## Next Steps

With Dapr and its components deployed, your application services can now leverage Dapr's building blocks by simply being configured with the appropriate Dapr annotations in their Kubernetes deployments (e.g., via Helm charts).
