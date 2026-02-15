# Accessing Grafana

If you have installed the `kube-prometheus-stack` using Helm (as per the Prometheus installation guide), Grafana is already deployed in your cluster.

## Accessing Grafana Dashboard

1.  **Get the Grafana Admin Password:**
    The admin password for Grafana is stored in a Kubernetes secret.
    ```bash
    kubectl get secret -n monitoring prometheus-grafana -o jsonpath="{.data.admin-password}" | base64 --decode
    ```

2.  **Port-forward to Grafana Service:**
    To access Grafana from your local machine, you can port-forward the Grafana service.
    ```bash
    kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring
    ```
    This will make Grafana accessible at `http://localhost:3000`.

3.  **Log in to Grafana:**
    Open `http://localhost:3000` in your browser.
    *   **Username:** `admin`
    *   **Password:** Use the password retrieved in Step 1.

## Creating Custom Dashboards and Data Sources

*   Once logged in, you can configure Prometheus as a data source (it's often pre-configured when installed via `kube-prometheus-stack`).
*   You can then import pre-built dashboards or create your own to visualize your application metrics.
