# Installing Dapr Control Plane on Kubernetes

Dapr can be installed on a Kubernetes cluster using Helm. This guide provides the steps to set up the Dapr control plane.

## Prerequisites

*   A Kubernetes cluster (e.g., OKE, AKS, GKE)
*   `kubectl` configured to connect to your cluster
*   `helm` CLI installed

## Installation Steps

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

## Post-Installation

After the Dapr control plane is installed, you can deploy your Dapr components (like pubsub, state store, secret store) and enable Dapr sidecar injection for your application pods.
