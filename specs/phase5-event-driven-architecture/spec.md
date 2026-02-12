# Phase V: Event-Driven Architecture Specification with Kafka

## 1. Introduction
This document outlines the detailed specification for implementing an Event-Driven Architecture (EDA) using Apache Kafka within the Todo AI Chatbot project. The primary goal is to decouple services, enhance scalability, improve fault tolerance, and facilitate real-time data processing for task management and reminders.

## 2. Scope

### In Scope:
-   **Kafka Topics:**
    -   `task-events`: For capturing lifecycle events of tasks (creation, update, completion, deletion).
    -   `reminders`: For triggering and managing reminder notifications.
    -   `task-updates`: For broadcasting significant task changes to downstream consumers (e.g., UI, other microservices).
-   **Event Schemas:** Formal definition of event structures using a schema registry (e.g., Avro).
-   **Producer Responsibilities:** Define which services produce specific events and their role in ensuring event quality and delivery.
-   **Consumer Responsibilities:** Define which services consume specific events and their role in processing events idempotently and reliably.

### Out of Scope:
-   Kafka cluster provisioning and management.
-   Complex event stream processing (e.g., KSQL DB).
-   Detailed Kafka client library implementation choices (e.g., Confluent Kafka Python, aiokafka).
-   Frontend WebSocket integration (will consume `task-updates` via a dedicated microservice).

## 3. Functional Requirements

### FR1: Event Capture
-   **FR1.1:** The Task Service SHALL produce a `TaskCreated` event to the `task-events` topic upon successful creation of a new task.
-   **FR1.2:** The Task Service SHALL produce a `TaskUpdated` event to the `task-events` topic upon successful modification of an existing task.
-   **FR1.3:** The Task Service SHALL produce a `TaskCompleted` event to the `task-events` topic upon a task being marked complete.
-   **FR1.4:** The Task Service SHALL produce a `TaskDeleted` event to the `task-events` topic upon a task being deleted.
-   **FR1.5:** The Reminder Service SHALL produce a `ReminderScheduled` event to the `reminders` topic when a reminder is successfully scheduled.
-   **FR1.6:** The Reminder Service SHALL produce a `ReminderTriggered` event to the `reminders` topic when a reminder's time arrives.
-   **FR1.7:** The Reminder Service SHALL produce a `ReminderDismissed` event to the `reminders` topic when a reminder is explicitly dismissed or its associated task is completed.
-   **FR1.8:** A dedicated `TaskUpdateBroadcaster` Service SHALL consume `task-events` and produce aggregated `TaskChanged` events to the `task-updates` topic for UI/external consumers.

### FR2: Event Consumption
-   **FR2.1:** The Recurring Task Worker SHALL consume `TaskCreated` and `TaskUpdated` events from `task-events` to identify and manage recurring task templates.
-   **FR2.2:** The Reminder Scheduling Worker SHALL consume `TaskCreated` and `TaskUpdated` events from `task-events` to automatically create/update reminders based on task due dates.
-   **FR2.3:** The Notification Service (or a placeholder) SHALL consume `ReminderTriggered` events from the `reminders` topic to deliver user notifications.
-   **FR2.4:** The UI Gateway/Backend-for-Frontend (BFF) Service SHALL consume `task-updates` events to push real-time updates to connected clients (e.g., via WebSockets).

## 4. Event Contracts (Schemas)

All event schemas will be defined and managed by a Schema Registry, ensuring backward and forward compatibility. Avro is the preferred serialization format.

### Topic: `task-events`
-   **`TaskCreated` Event:**
    -   `id`: UUID (Task ID)
    -   `user_id`: UUID
    -   `title`: String
    -   `description`: Optional String
    -   `created_at`: Timestamp
    -   `due_date`: Optional Timestamp
    -   `priority`: Optional String (Enum: Low, Medium, High)
    -   `tags`: Array of Strings
    -   `is_recurring_template`: Boolean
    -   `recurrence_pattern`: Optional String (JSON encoded)
-   **`TaskUpdated` Event:**
    -   `id`: UUID
    -   `user_id`: UUID
    -   `updated_fields`: Map<String, Any> (e.g., `{"title": "New Title", "due_date": "2024-12-31T23:59:59Z"}`)
    -   `timestamp`: Timestamp
-   **`TaskCompleted` Event:**
    -   `id`: UUID
    -   `user_id`: UUID
    -   `completed_at`: Timestamp
-   **`TaskDeleted` Event:**
    -   `id`: UUID
    -   `user_id`: UUID
    -   `deleted_at`: Timestamp

### Topic: `reminders`
-   **`ReminderScheduled` Event:**
    -   `id`: UUID (Reminder ID)
    -   `task_id`: UUID
    -   `user_id`: UUID
    -   `remind_at`: Timestamp
    -   `status`: String (Enum: pending)
-   **`ReminderTriggered` Event:**
    -   `id`: UUID (Reminder ID)
    -   `task_id`: UUID
    -   `user_id`: UUID
    -   `triggered_at`: Timestamp
-   **`ReminderDismissed` Event:**
    -   `id`: UUID (Reminder ID)
    -   `task_id`: UUID
    -   `user_id`: UUID
    -   `dismissed_at`: Timestamp

### Topic: `task-updates`
-   **`TaskChanged` Event:**
    -   `task_id`: UUID
    -   `user_id`: UUID
    -   `change_type`: String (Enum: created, updated, completed, deleted)
    -   `payload`: JSON (full `Task` object or relevant diff, depending on consumer needs)
    -   `timestamp`: Timestamp

## 5. Reliability Requirements

-   **At-Least-Once Delivery:** All critical events (e.g., `TaskCreated`, `ReminderTriggered`) SHALL be delivered at least once to consumers. Consumers must be designed to handle duplicate messages idempotently.
-   **Ordered Delivery:** Events within a partition SHALL be processed in the order they were produced. Kafka's default behavior satisfies this for single partitions. Keys (e.g., `task_id`, `user_id`) will be used to ensure related events go to the same partition.
-   **Durability:** Events SHALL be durably stored in Kafka for a configurable retention period (e.g., 7 days) to allow for consumer recovery and replay.
-   **Monitoring:** Comprehensive monitoring for Kafka topics (lag, throughput, errors) and consumer group health SHALL be implemented.

## 6. Failure Handling Expectations

### Producer Failures:
-   **Transient Errors:** Producers SHALL implement retry mechanisms with exponential backoff for transient Kafka broker connection issues.
-   **Persistent Errors:** For persistent errors (e.g., invalid schema), events SHALL be logged to a Dead-Letter Queue (DLQ) topic (e.g., `task-events-dlq`) for manual inspection and reprocessing.
-   **Schema Validation:** Producers SHALL validate event schemas before producing to Kafka.

### Consumer Failures:
-   **Processing Errors:** Consumers SHALL handle message processing failures gracefully. Failed messages will be retried (potentially with a delay) or moved to a consumer-specific DLQ (e.g., `recurring-task-worker-dlq`) to prevent blocking the consumer group.
-   **Idempotency:** All consumers MUST be idempotent, meaning processing the same message multiple times has the same effect as processing it once. This is crucial for at-least-once delivery.
-   **Offset Management:** Consumers SHALL commit offsets reliably to ensure progress is tracked and messages are not reprocessed unnecessarily after restarts.

### Kafka Broker Failures:
-   Kafka's inherent replication and fault-tolerance mechanisms are relied upon to ensure high availability and data durability.

## 7. Scalability Expectations

-   **Topic Partitioning:** Topics SHALL be partitioned appropriately (e.g., based on `user_id` or `task_id`) to allow for horizontal scaling of consumers and producers. The initial number of partitions will be determined during implementation, with provisions for future repartitioning.
-   **Consumer Groups:** Multiple instances of consumer services SHALL operate within a consumer group, allowing for parallel processing of partitions.
-   **Service Decoupling:** The EDA approach inherently supports scalability by decoupling services, allowing them to evolve and scale independently.

## 8. Producer Responsibilities

-   **Serialization:** Serialize events using the agreed-upon schema (e.g., Avro).
-   **Keying:** Use meaningful keys (e.g., `task_id`, `user_id`) for events to ensure ordering within partitions.
-   **Error Handling:** Implement retry logic and DLQ for failed message production.
-   **Schema Evolution:** Coordinate with Schema Registry for schema updates.

## 9. Consumer Responsibilities

-   **Deserialization:** Deserialize events using the agreed-upon schema.
-   **Idempotency:** Ensure all event processing logic is idempotent.
-   **Error Handling:** Implement retry logic and DLQ for failed message processing.
-   **Offset Committing:** Commit offsets regularly and reliably.
-   **Monitoring:** Report consumer lag and processing metrics.
-   **Schema Evolution:** Handle schema changes gracefully (e.g., by using schema evolution features of Avro and Schema Registry).

## 10. Next Steps

-   Detailed Avro schema definitions for all events.
-   Integration with a Schema Registry.
-   Producer and Consumer client library selection and configuration.
-   Implementation of core event-producing and event-consuming logic within services.