# Deploying Apache Kafka using Strimzi Operator

This guide provides steps to deploy Apache Kafka within your Kubernetes cluster using the Strimzi Kafka Operator. Strimzi simplifies the deployment and management of Kafka on Kubernetes.

## Prerequisites

*   A Kubernetes cluster (e.g., OKE)
*   `kubectl` configured to connect to your cluster

## 1. Install Strimzi Operator

The Strimzi Operator manages Kafka clusters deployed in Kubernetes.

1.  **Create a namespace for Kafka:**
    ```bash
    kubectl create namespace kafka
    ```

2.  **Apply the Strimzi installation manifest:**
    ```bash
    kubectl apply -f https://strimzi.io/install/latest?namespace=kafka
    ```
    *Note: This command applies the latest stable version of Strimzi Operator. For a specific version, you might need to download the manifest first.*

3.  **Verify Strimzi operator deployment:**
    Check that the Strimzi operator pods are running in the `kafka` namespace:
    ```bash
    kubectl get pods -n kafka
    ```
    You should see pods like `strimzi-cluster-operator-...` in a `Running` state.

## 2. Deploy Kafka Cluster

After the Strimzi Operator is running, you can deploy your Kafka cluster by creating a `Kafka` custom resource.

1.  **Apply the Kafka cluster manifest:**
    ```bash
    kubectl apply -f k8s/infrastructure/strimzi-kafka/02-kafka-cluster.yaml -n kafka
    ```
    The `k8s/infrastructure/strimzi-kafka/02-kafka-cluster.yaml` file defines a basic Kafka cluster named `taskflow-kafka` with one replica for both Kafka and ZooKeeper.

2.  **Verify Kafka cluster deployment:**
    Check that the Kafka and ZooKeeper pods are running in the `kafka` namespace:
    ```bash
    kubectl get pods -n kafka
    kubectl get kafka -n kafka
    ```
    You should see `taskflow-kafka-kafka-0`, `taskflow-kafka-zookeeper-0` (and potentially `entity-operator` pods) in a `Running` state.

## 3. Creating Kafka Topics

Once the Kafka cluster is up, you can create topics using the Strimzi `KafkaTopic` custom resource.

*   **For `task-events`, `reminders`, `task-updates`:**
    You will need to define `KafkaTopic` resources. For example, for `task-events`:
    ```yaml
    apiVersion: kafka.strimzi.io/v1beta2
    kind: KafkaTopic
    metadata:
      name: task-events
      labels:
        strimzi.io/cluster: taskflow-kafka
    spec:
      partitions: 1
      replicas: 1
      config:
        retention.ms: 604800000 # 7 days
        segment.bytes: 1073741824 # 1GB
    ```
    You would create similar YAML files for `reminders` and `task-updates` topics, and apply them with `kubectl apply -f your-topic.yaml -n kafka`.

## Next Steps

With Kafka deployed, your Dapr Pub/Sub component (`pubsub-broker`) configured to connect to `kafka:9092` (which will resolve to the internal Kafka service), your application services can now publish and subscribe to these topics via Dapr.
