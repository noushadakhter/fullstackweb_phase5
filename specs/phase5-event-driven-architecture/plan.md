# Phase V: Kafka Integration Architecture Plan

## 1. Introduction
This plan details the technical architecture for integrating Apache Kafka into the Todo AI Chatbot system, leveraging the Event-Driven Architecture (EDA) principles outlined in `specs/phase5-event-driven-architecture/spec.md`. The focus is on Kafka topic structure, event schemas, producer/consumer flows, asynchronous processing, error handling, and deployment within a Kubernetes environment.

## 2. Kafka Cluster Deployment (Kubernetes)
The Kafka cluster (including ZooKeeper, Kafka Brokers, and Schema Registry) will be deployed within the Kubernetes cluster.
-   **Kafka Brokers:** StatefulSet for persistent storage and high availability.
-   **ZooKeeper:** StatefulSet for coordination.
-   **Schema Registry:** Deployment for managing Avro schemas.
-   **Monitoring:** Prometheus and Grafana for Kafka metrics (consumer lag, throughput, etc.).

## 3. Kafka Topic Structure

### Topic Naming Convention:
`{project_name}.{domain_area}.{event_type}` (e.g., `todo.tasks.events`, `todo.reminders.triggered`)

### Defined Topics:
-   **`todo.tasks.events`**
    -   **Purpose:** Capture all lifecycle changes of `Task` entities.
    -   **Partitions:** Initial 6 (scalable based on user concurrency for `task_id` hashing).
    -   **Replication Factor:** 3 (for high availability).
    -   **Retention:** 7 days.
    -   **Key:** `task_id` (UUID) - ensures all events for a specific task are ordered within a partition.
-   **`todo.reminders.events`**
    -   **Purpose:** Manage reminder lifecycle events (scheduled, triggered, dismissed).
    -   **Partitions:** Initial 3 (scalable based on user concurrency for `reminder_id` hashing).
    -   **Replication Factor:** 3.
    -   **Retention:** 3 days.
    -   **Key:** `reminder_id` (UUID).
-   **`todo.task_updates.broadcast`**
    -   **Purpose:** Broadcast aggregated task changes for UI updates and other interested parties.
    -   **Partitions:** Initial 3 (scalable based on `user_id` hashing).
    -   **Replication Factor:** 3.
    -   **Retention:** 1 day (near real-time updates).
    -   **Key:** `user_id` (UUID) - ensures all updates for a specific user are ordered.

### Dead-Letter Queue (DLQ) Topics:
-   **`todo.tasks.events.dlq`**
-   **`todo.reminders.events.dlq`**
-   **`todo.task_updates.broadcast.dlq`**
-   **`todo.{consumer_group_name}.dlq`** (for consumer-specific processing failures)
    -   **Purpose:** Store events that fail processing after retries for manual intervention.
    -   **Retention:** Configurable (e.g., 30 days).

## 4. Event Schema Definitions (Avro with Schema Registry)

-   All event schemas (e.g., `TaskCreated`, `TaskUpdated`, `ReminderScheduled`) will be defined using Avro.
-   The Schema Registry will host these schemas, ensuring version control and compatibility checks.
-   Producers and consumers will interact with the Schema Registry to serialize/deserialize messages, ensuring data contract adherence.
-   **Example (Conceptual `TaskCreated` Avro Schema):**
    ```json
    {
      "type": "record",
      "name": "TaskCreated",
      "namespace": "com.todo.events",
      "fields": [
        {"name": "id", "type": {"type": "string", "logicalType": "uuid"}},
        {"name": "user_id", "type": {"type": "string", "logicalType": "uuid"}},
        {"name": "title", "type": "string"},
        {"name": "description", "type": ["null", "string"], "default": null},
        {"name": "created_at", "type": {"type": "long", "logicalType": "timestamp-millis"}},
        {"name": "due_date", "type": ["null", {"type": "long", "logicalType": "timestamp-millis"}], "default": null},
        {"name": "priority", "type": ["null", {"type": "enum", "name": "PriorityEnum", "symbols": ["Low", "Medium", "High"]}], "default": null},
        {"name": "tags", "type": {"type": "array", "items": "string"}, "default": []},
        {"name": "is_recurring_template", "type": "boolean", "default": false},
        {"name": "recurrence_pattern", "type": ["null", "string"], "default": null}
      ]
    }
    ```

## 5. Producer Flow (Chat API - FastAPI Backend)

The existing FastAPI backend (Chat API) will act as the primary producer for `todo.tasks.events` and `todo.reminders.events`.

1.  **API Request:** User interacts with the Chat API (e.g., creates a task).
2.  **Database Transaction:** The API handler performs database operations (e.g., inserts a new `Task` record) within a transaction.
3.  **Event Creation:** After a successful database commit, the API handler constructs the relevant event object (e.g., `TaskCreated`).
4.  **Serialization & Publishing:** The event is serialized using Avro and the Schema Registry, and then published asynchronously to the appropriate Kafka topic (`todo.tasks.events` or `todo.reminders.events`).
    -   **Asynchronous Publishing:** Use a non-blocking Kafka producer client (e.g., `aiokafka` for Python) to avoid impacting API response times.
    -   **Error Handling:**
        -   **Transient:** Retries with exponential backoff for Kafka broker connectivity issues.
        -   **Persistent:** If publishing ultimately fails (e.g., schema mismatch, Kafka unavailable for extended periods), the event is logged to an internal DLQ or a file system for manual recovery. This is a critical point; database commit *must* precede event publishing to avoid data loss.
5.  **API Response:** The API returns a response to the client.

## 6. Consumer Services

All consumer services will be deployed as separate Kubernetes Deployments, each running instances within a dedicated Kafka Consumer Group. This allows for parallel processing and independent scaling.

### 6.1 Recurring Task Worker (Consumer Group: `recurring-task-cg`)
-   **Subscribed Topic:** `todo.tasks.events`
-   **Functionality:**
    -   Consumes `TaskCreated` and `TaskUpdated` events.
    -   If an event indicates a new or modified recurring task template (`is_recurring_template = True`), it schedules or updates the internal recurrence logic (e.g., in `APScheduler` or a dedicated database table for recurrence schedules).
    -   Upon scheduled triggers, it creates new task instances (by producing new `TaskCreated` events to `todo.tasks.events` or directly inserting into the database, then producing a `TaskCreated` event).
-   **Async Processing:** Leverages `asyncio` for non-blocking I/O with Kafka and database.
-   **Error Handling:**
    -   **Idempotency:** Ensures that processing the same `TaskCreated`/`TaskUpdated` event multiple times does not lead to duplicate recurrence schedules or incorrect updates.
    -   **Retries:** If processing a message fails (e.g., database error), the message is retried for a configurable number of times.
    -   **DLQ:** After maximum retries, the message is moved to `todo.recurring-task-cg.dlq`.

### 6.2 Reminder Scheduling Worker (Consumer Group: `reminder-scheduler-cg`)
-   **Subscribed Topic:** `todo.tasks.events`
-   **Functionality:**
    -   Consumes `TaskCreated` and `TaskUpdated` events.
    -   If an event contains `due_date` information, it calculates and schedules corresponding `Reminder` events in the database.
    -   Produces `ReminderScheduled` events to `todo.reminders.events`.
-   **Async Processing:** `asyncio` based.
-   **Error Handling:** Similar to Recurring Task Worker (Idempotency, Retries, DLQ: `todo.reminder-scheduler-cg.dlq`).

### 6.3 Reminder Triggering Worker (Consumer Group: `reminder-trigger-cg`)
-   **Subscribed Topic:** `todo.reminders.events` (specifically `ReminderScheduled` events)
-   **Functionality:**
    -   Consumes `ReminderScheduled` events.
    -   Manages an in-memory or persistent schedule of reminder trigger times.
    -   When `remind_at` time is reached, it triggers a notification (e.g., calls an external Notification Service API) and produces a `ReminderTriggered` event to `todo.reminders.events`.
-   **Async Processing:** `asyncio` based.
-   **Error Handling:** Similar to other consumers (Idempotency, Retries, DLQ: `todo.reminder-trigger-cg.dlq`).

### 6.4 Task Update Broadcaster (Consumer Group: `task-broadcaster-cg`)
-   **Subscribed Topic:** `todo.tasks.events`
-   **Functionality:**
    -   Consumes all `Task*` events from `todo.tasks.events`.
    -   Aggregates changes and produces a `TaskChanged` event to `todo.task_updates.broadcast`.
    -   This service can enrich the event payload for UI/external consumers.
-   **Async Processing:** `asyncio` based.
-   **Error Handling:** Similar to other consumers (Idempotency, Retries, DLQ: `todo.task-broadcaster-cg.dlq`).

### 6.5 Audit Logging Service (Consumer Group: `audit-log-cg`)
-   **Subscribed Topics:** `todo.tasks.events`, `todo.reminders.events`, `todo.task_updates.broadcast` (or specific audit-relevant events).
-   **Functionality:**
    -   Consumes events and writes audit logs to a dedicated audit database or log storage.
-   **Async Processing:** `asyncio` based.
-   **Error Handling:** Standard consumer error handling, including DLQ (`todo.audit-log-cg.dlq`).

## 7. Async Processing Design

-   **FastAPI Producers:** Use `aiokafka` for asynchronous Kafka message production within FastAPI endpoints. This ensures that publishing events does not block the main event loop, maintaining low latency for API responses.
-   **Consumer Services:** Each consumer service will be an `asyncio` application that uses `aiokafka` to consume messages. Processing logic within consumers will also leverage `asyncio` for database interactions and external API calls (e.g., Notification Service).

## 8. Error Handling and Retries

### 8.1 Producers:
-   **Network Issues:** `aiokafka` producers include internal retry mechanisms for transient network issues.
-   **Message Delivery Failure:** Implement custom callbacks for `on_delivery` to check for successful delivery. If delivery fails persistently, log the event to a file/DB for out-of-band recovery.
-   **Schema Mismatch:** Pre-production schema validation will minimize this. If it occurs, the producer should log an error and route to a DLQ topic.

### 8.2 Consumers:
-   **Consumer Group Management:** Kafka consumer groups handle consumer crashes and rebalancing automatically.
-   **Processing Logic Retries:**
    -   Each consumer will have a structured try-except block for its processing logic.
    -   Upon an exception, the message will be retried (e.g., by not committing the offset and letting Kafka redeliver, or by using a retry topic with delays).
    -   **Retry Strategy:** Exponential backoff for retries to prevent overwhelming downstream services.
    -   **Max Retries:** After a configured number of retries, if processing still fails, the message will be published to a service-specific DLQ (`todo.{consumer_group_name}.dlq`).
-   **Idempotency:** Critical for all consumers. Each consumer will implement mechanisms (e.g., checking for existence before insertion, using unique keys for updates) to ensure processing a message multiple times yields the same result.
-   **Monitoring:** Consumer lag is a key metric to monitor. High lag indicates processing bottlenecks or failures.

## 9. Kubernetes Deployment Considerations

-   **StatefulSets for Kafka/ZooKeeper:** Ensures stable network identities and persistent storage for brokers and ZooKeeper nodes.
-   **Deployments for Services:** All producer (FastAPI backend) and consumer services (Recurring, Reminder Scheduler, Reminder Trigger, Task Broadcaster, Audit) will be deployed as standard Kubernetes Deployments.
-   **Horizontal Pod Autoscaler (HPA):** Configure HPA for consumer deployments based on CPU utilization and/or custom metrics (e.g., consumer lag) to scale consumers dynamically.
-   **ConfigMaps & Secrets:** Use Kubernetes ConfigMaps for Kafka broker addresses, Schema Registry URL, topic names, and other configuration. Use Secrets for any sensitive credentials.
-   **Network Policies:** Implement network policies to restrict communication between pods to only necessary services (e.g., consumers can only talk to Kafka, producers can only talk to Kafka and the database).
-   **Liveness and Readiness Probes:** Implement robust probes for all pods to ensure healthy operation and graceful restarts/shutdowns.
-   **Helm Charts:** Use Helm charts for managing the deployment lifecycle of the Kafka cluster and all related services, simplifying installation, upgrades, and configuration.

## 10. Next Steps

-   Define Helm Charts for Kafka cluster and individual services.
-   Implement Avro schema definitions in the Schema Registry.
-   Develop base Kafka producer and consumer client libraries.
-   Implement producer logic within existing FastAPI endpoints.
-   Develop individual consumer services as described above.