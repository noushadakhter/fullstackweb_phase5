# Phase V: Dapr Integration Technical Architecture Plan

## 1. Introduction
This document outlines the technical architecture for integrating Dapr (Distributed Application Runtime) into the Todo AI Chatbot microservices, building upon the specification defined in `specs/phase5-dapr-integration/spec.md`. It covers the Dapr sidecar architecture, component configurations, integration designs for Pub/Sub, State Management, Service Invocation, Jobs API, and Secrets Management, all within a Kubernetes deployment model.

## 2. Dapr Sidecar Architecture

-   **Sidecar Injection:** Dapr will be deployed to Kubernetes with automatic sidecar injection enabled. Each application pod (e.g., Chat API, Recurring Task Worker, Reminder Service) will have a Dapr sidecar container (`daprd`) automatically injected alongside its application container.
-   **Communication:**
    -   Application containers will communicate with Dapr building blocks via HTTP/gRPC APIs exposed by the `daprd` sidecar.
    -   The `daprd` sidecar handles communication with external components (Kafka, PostgreSQL, Kubernetes Secrets) on behalf of the application.
-   **Isolation:** Each application instance has its own dedicated Dapr sidecar, providing isolated resource management and API exposure.

## 3. Dapr Components Configuration (Kubernetes YAML)

Dapr components will be defined as Kubernetes YAML files and applied to the cluster.

### 3.1 Pub/Sub Component (`pubsub.kafka`)
-   **Component Name:** `pubsub-kafka-todo`
-   **Type:** `pubsub.kafka`
-   **Configuration:**
    -   `brokers`: List of Kafka broker addresses (e.g., `kafka-broker-0.kafka-headless.default.svc.cluster.local:9092`).
    -   `consumerID`: Dapr will manage consumer groups automatically based on `app-id`.
    -   `schemaRegistryURL`: Address of the Schema Registry (e.g., `schema-registry.default.svc.cluster.local:8081`).
    -   **Kubernetes YAML (Conceptual):**
        ```yaml
        apiVersion: dapr.io/v1alpha1
        kind: Component
        metadata:
          name: pubsub-kafka-todo
          namespace: default
        spec:
          type: pubsub.kafka
          version: v1
          metadata:
          - name: brokers
            value: "kafka-broker-0.kafka-headless.default.svc.cluster.local:9092,kafka-broker-1.kafka-headless.default.svc.cluster.local:9092"
          - name: consumerID
            value: "{{ .appID }}" # Dapr injects this based on app-id
          - name: schemaRegistryURL
            value: "http://schema-registry.default.svc.cluster.local:8081"
          # ... other Kafka-specific configurations (e.g., auth, TLS if needed)
        ```

### 3.2 State Management Component (`state.postgresql`)
-   **Component Name:** `state-postgresql-todo`
-   **Type:** `state.postgresql`
-   **Configuration:**
    -   `connectionString`: Database connection string (retrieved from Secrets).
    -   **Kubernetes YAML (Conceptual):**
        ```yaml
        apiVersion: dapr.io/v1alpha1
        kind: Component
        metadata:
          name: state-postgresql-todo
          namespace: default
        spec:
          type: state.postgresql
          version: v1
          metadata:
          - name: connectionString
            secretKeyRef:
              name: postgresql-secrets # Kubernetes Secret name
              key: connection-string  # Key within the secret
          - name: tablePrefix
            value: "daprstate" # Optional prefix for Dapr tables
        ```

### 3.3 Secrets Management Component (`secretstores.kubernetes`)
-   **Component Name:** `secretstore-kubernetes-todo`
-   **Type:** `secretstores.kubernetes`
-   **Configuration:**
    -   No specific metadata required for Kubernetes secret store, Dapr uses the service account token.
    -   **Kubernetes YAML (Conceptual):**
        ```yaml
        apiVersion: dapr.io/v1alpha1
        kind: Component
        metadata:
          name: secretstore-kubernetes-todo
          namespace: default
        spec:
          type: secretstores.kubernetes
          version: v1
        ```

## 4. Jobs API Integration Design (for Reminders)

Instead of Dapr's Jobs API (which is more about external job scheduling platforms), we will use Dapr's Bindings (Output Binding) or Actors with timers for scheduled reminders.

### Option A: Using Dapr Bindings (Output Binding) - Preferred for simplicity
-   **Design:** The Reminder Service will use Dapr's Output Binding to trigger a function call or message to a specific endpoint at a scheduled time.
-   **Component Type:** `bindings.cron` or a custom timer binding.
-   **Flow:**
    1.  Reminder Service calculates `remind_at` time for a task.
    2.  Reminder Service calls Dapr's Output Binding API, effectively scheduling a "call-back" to itself or another service at `remind_at`.
    3.  Dapr's binding component handles the scheduling and invocation.
    4.  The invoked endpoint processes the reminder (e.g., sends a notification, produces a `ReminderTriggered` event).
-   **Kubernetes YAML (Conceptual for a Timer Binding):**
    ```yaml
    apiVersion: dapr.io/v1alpha1
    kind: Component
    metadata:
      name: timer-todo-reminders
      namespace: default
    spec:
      type: bindings.cron
      version: v1
      metadata:
      - name: schedule
        value: "0 * * * *" # Example: every hour, actual schedule managed by Reminder Service
    ```
    (Note: A more direct timer solution via Actors or custom logic is often used for precise reminders).

### Option B: Using Dapr Actors with Timers
-   **Design:** Each reminder could be represented as a Dapr Actor instance, with a durable timer set for the `remind_at` time.
-   **Flow:**
    1.  Reminder Service receives a request to schedule a reminder.
    2.  It activates a Dapr Actor (e.g., `ReminderActor_{task_id}_{reminder_id}`).
    3.  The Actor creates a durable timer for `remind_at`.
    4.  When the timer fires, the Actor's method is invoked, which then processes the reminder.
-   **Consideration:** This adds Actor state management complexity. Option A is simpler for initial Phase V.

## 5. Service Invocation Flow

-   **Cross-Service Calls:** When Service A needs to call Service B, it will invoke Service B via its local Dapr sidecar.
-   **Flow:**
    1.  Service A makes an HTTP/gRPC call to `http://localhost:3500/v1.0/invoke/<app-id-of-service-B>/method/<method-name>`.
    2.  Dapr sidecar of Service A intercepts the call.
    3.  Dapr sidecar uses mTLS and built-in service discovery (via Kubernetes DNS) to locate Service B's Dapr sidecar.
    4.  Dapr sidecar of Service A makes the call to Dapr sidecar of Service B.
    5.  Dapr sidecar of Service B invokes the actual method on Service B's application container.
-   **Example:** Chat API invoking a Notification Service.

## 6. Kubernetes Application Deployment Annotations

Each microservice Deployment YAML will be annotated to enable Dapr sidecar injection and configure Dapr-specific settings.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chat-api
  namespace: default
spec:
  # ... standard deployment spec ...
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "chat-api" # Unique ID for this service
        dapr.io/app-port: "8000" # Port FastAPI listens on
        dapr.io/config: "app-config" # Optional: reference to a DaprConfiguration
    spec:
      containers:
      - name: chat-api
        image: your-repo/chat-api:latest
        ports:
        - containerPort: 8000
```

## 7. Integration with Python FastAPI Backend

-   **Dapr SDK:** Utilize the Python Dapr SDK (`dapr-sdk-python`) within FastAPI services for interacting with Dapr APIs.
-   **Pub/Sub:**
    -   **Publishing:** `dapr_client.publish_event(pubsub_name="pubsub-kafka-todo", topic="todo.tasks.events", data=event_payload)`
    -   **Subscribing:** Use Dapr's HTTP subscription endpoint (e.g., `/dapr/subscribe`) in FastAPI to declare topic subscriptions. FastAPI routes will then handle incoming Dapr POST requests for new messages.
-   **State Management:** `dapr_client.save_state("state-postgresql-todo", key="task-123", value=task_object)`
-   **Secrets:** `dapr_client.get_secret("secretstore-kubernetes-todo", "db-connection-string")`
-   **Service Invocation:** `dapr_client.invoke_method("notification-service", "send-notification", data=notification_payload)`

## 8. Next Steps

-   **Dapr Components YAMLs:** Finalize and create actual Dapr component YAML files for `pubsub-kafka-todo`, `state-postgresql-todo`, and `secretstore-kubernetes-todo`.
-   **Application Annotations:** Update existing Kubernetes Deployment YAMLs for all services to include Dapr annotations.
-   **Python SDK Integration:** Begin integrating Dapr SDK calls into the FastAPI backend and consumer services where Dapr building blocks are used.
-   **Reminder Scheduling:** Decide on the exact mechanism for reminder scheduling using Dapr (e.g., `bindings.cron` vs. custom timer with state).