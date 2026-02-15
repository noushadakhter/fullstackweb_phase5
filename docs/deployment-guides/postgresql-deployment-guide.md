# Deploying PostgreSQL Database

This guide provides steps to deploy a PostgreSQL database instance within your Kubernetes cluster.

## Prerequisites

*   A Kubernetes cluster (e.g., OKE)
*   `kubectl` configured to connect to your cluster

## Deployment Steps

1.  **Apply the Persistent Volume Claim (PVC) manifest:**
    ```bash
    kubectl apply -f k8s/infrastructure/postgresql/postgres-pvc.yaml
    ```
    This creates a request for persistent storage for your PostgreSQL database. Ensure your Kubernetes cluster has a default StorageClass configured or adjust the PVC to specify one.

2.  **Apply the PostgreSQL deployment manifest:**
    ```bash
    kubectl apply -f k8s/infrastructure/postgresql/postgres-deployment.yaml
    ```
    This will create a Deployment for a single PostgreSQL instance, mounting the PVC for data persistence.

3.  **Apply the PostgreSQL service manifest:**
    ```bash
    kubectl apply -f k8s/infrastructure/postgresql/postgres-service.yaml
    ```
    This will create a ClusterIP Service to expose the PostgreSQL instance internally within the cluster.

4.  **Verify PostgreSQL deployment:**
    Check that the PostgreSQL pod and service are running:
    ```bash
    kubectl get pods -l app=postgres
    kubectl get svc -l app=postgres
    ```
    You should see the PostgreSQL pod in a `Running` state and the `postgres` service created.

## Database Access and Configuration

Your application services (e.g., `tasks-service`) will connect to the PostgreSQL database using the internal service name `postgres` and port `5432`.

The environment variables `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD` are set in the `postgres-deployment.yaml`. For production environments, it is highly recommended to manage these credentials securely using Kubernetes Secrets and reference them in the deployment manifest.

## Next Steps

With PostgreSQL deployed and accessible internally, your Dapr-enabled applications can configure their database connection strings to use this instance.
