# Installing Prometheus Operator on Kubernetes

The Prometheus Operator provides Kubernetes native deployment and management of Prometheus and related monitoring components.

## Prerequisites

*   `kubectl` configured to connect to your cluster
*   `helm` CLI installed

## Installation Steps

1.  **Add Prometheus Community Helm repository:**
    ```bash
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update
    ```

2.  **Create a namespace for monitoring (optional, but recommended):**
    ```bash
    kubectl create namespace monitoring
    ```

3.  **Install Prometheus Operator:**
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
    *Note: `kube-prometheus-stack` is a comprehensive chart that includes Prometheus, Grafana, Alertmanager, and the Prometheus Operator.*

4.  **Verify installation:**
    ```bash
    kubectl get pods -n monitoring
    ```
    You should see Prometheus, Grafana, and Alertmanager pods running.

## Post-Installation

After Prometheus is installed, you can create `ServiceMonitor` resources to automatically scrape metrics from your application services.
