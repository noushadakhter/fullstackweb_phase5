# Deploying Redis for Dapr State Store

This guide provides steps to deploy a Redis instance within your Kubernetes cluster to be used as a Dapr State Store component.

## Prerequisites

*   A Kubernetes cluster (e.g., OKE)
*   `kubectl` configured to connect to your cluster

## Deployment Steps

1.  **Apply the Redis deployment manifest:**
    ```bash
    kubectl apply -f k8s/infrastructure/redis/redis-deployment.yaml
    ```
    This will create a Deployment for a single Redis instance.

2.  **Apply the Redis service manifest:**
    ```bash
    kubectl apply -f k8s/infrastructure/redis/redis-service.yaml
    ```
    This will create a ClusterIP Service to expose the Redis instance internally within the cluster.

3.  **Verify Redis deployment:**
    Check that the Redis pod and service are running:
    ```bash
    kubectl get pods -l app=redis
    kubectl get svc -l app=redis
    ```
    You should see the Redis pod in a `Running` state and the `redis` service created.

## Configuration for Dapr State Store

Your Dapr `statestore-redis.yaml` component is configured to connect to the `redis:6379` service. This internal DNS name will automatically resolve to the Redis service you deployed.

```yaml
# Example from dapr/components/statestore-redis.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: redis:6379 # This points to the Kubernetes Service name
  # ... (other metadata like password)
```

## Next Steps

With Redis deployed and accessible internally, your Dapr-enabled applications can use the `statestore` component for state management.
