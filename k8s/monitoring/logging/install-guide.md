# Installing Loki and Promtail for Centralized Logging

Loki is a horizontally scalable, highly available, multi-tenant log aggregation system inspired by Prometheus. It is designed to be very cost effective and easy to operate. Promtail is an agent which ships the contents of local logs to a private Loki instance or Grafana Cloud.

## Prerequisites

*   `kubectl` configured to connect to your cluster
*   `helm` CLI installed
*   Prometheus and Grafana installed (optional, but recommended for integration)

## Installation Steps

1.  **Add Grafana Helm repository:**
    ```bash
    helm repo add grafana https://grafana.github.io/helm-charts
    helm repo update
    ```
    *Note: This is the same repository for Loki and Promtail charts.*

2.  **Create a namespace for logging (optional, but recommended):**
    ```bash
    kubectl create namespace logging
    ```

3.  **Install Loki:**
    ```bash
    helm install loki grafana/loki --namespace logging
    ```

4.  **Install Promtail:**
    ```bash
    helm install promtail grafana/promtail --namespace logging 
      --set "loki.serviceName=loki"
    ```
    *Note: Ensure `loki.serviceName` points to the correct Loki service name, which is typically `loki` if installed in the same namespace.*

5.  **Verify installation:**
    ```bash
    kubectl get pods -n logging
    ```
    You should see Loki and Promtail pods running.

## Post-Installation

After Loki and Promtail are installed, Promtail will automatically start collecting logs from your Kubernetes pods and sending them to Loki. You can then configure Loki as a data source in Grafana to view and query your application logs.
