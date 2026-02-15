# Comprehensive Monitoring and Logging Setup Guide

This guide provides instructions for setting up a robust monitoring and logging solution in your Kubernetes cluster using Prometheus, Grafana, Loki, and Promtail.

## Prerequisites

*   A Kubernetes cluster (e.g., OKE)
*   `kubectl` configured to connect to your cluster
*   `helm` CLI installed

## 1. Monitoring with Prometheus and Grafana

We use the `kube-prometheus-stack` Helm chart to deploy Prometheus Operator, Prometheus, Grafana, and Alertmanager.

### Installation Steps

1.  **Add Prometheus Community Helm repository:**
    ```bash
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update
    ```

2.  **Create a namespace for monitoring (optional, but recommended):**
    ```bash
    kubectl create namespace monitoring
    ```

3.  **Install `kube-prometheus-stack`:**
    ```bash
    helm install prometheus prometheus-community/kube-prometheus-stack 
      --namespace monitoring 
      --set grafana.service.type=ClusterIP 
      --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false 
      --set prometheus.prometheusSpec.podMonitorSelectorNilUsesHelmValues=false 
      --set alertmanager.alertmanagerSpec.route.groupBy='{job}' 
      --set alertmanager.alertmanagerSpec.route.groupWait='30s' 
      --set alertmanager.alertmanagerSpec.route.groupInterval='5m' 
      --set alertmanager.alertmanagerSpec.route.repeatInterval='12h'
    ```
    *Note: This chart installs Prometheus, Grafana, Alertmanager, and the Prometheus Operator.*

4.  **Verify installation:**
    ```bash
    kubectl get pods -n monitoring
    ```
    You should see Prometheus, Grafana, and Alertmanager pods running.

### Accessing Grafana Dashboard

1.  **Get the Grafana Admin Password:**
    ```bash
    kubectl get secret -n monitoring prometheus-grafana -o jsonpath="{.data.admin-password}" | base64 --decode
    ```

2.  **Port-forward to Grafana Service:**
    ```bash
    kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring
    ```
    This will make Grafana accessible at `http://localhost:3000`.

3.  **Log in to Grafana:**
    Open `http://localhost:3000` in your browser.
    *   **Username:** `admin`
    *   **Password:** Use the password retrieved in Step 1.

## 2. Centralized Logging with Loki and Promtail

Loki and Promtail provide a cost-effective and scalable logging solution that integrates seamlessly with Grafana.

### Installation Steps

1.  **Add Grafana Helm repository:**
    (If not already added for Prometheus stack)
    ```bash
    helm repo add grafana https://grafana.github.io/helm-charts
    helm repo update
    ```

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
    *Note: Ensure `loki.serviceName` points to the correct Loki service name.*

5.  **Verify installation:**
    ```bash
    kubectl get pods -n logging
    ```
    You should see Loki and Promtail pods running.

### Accessing Logs in Grafana

After Loki and Promtail are installed, you can configure Loki as a data source in Grafana to view and query your application logs.

1.  **Log in to Grafana** (as per instructions above).
2.  **Add Loki as a Data Source:**
    *   Navigate to **Configuration (Gear icon) -> Data Sources**.
    *   Click "Add data source" and select "Loki".
    *   **Name:** `Loki`
    *   **URL:** `http://loki.logging.svc.cluster.local:3100` (assuming Loki is in `logging` namespace)
    *   Save and Test.
3.  **Explore Logs:**
    Navigate to **Explore** and select the Loki data source. You can then write LogQL queries to filter and analyze your application logs.
