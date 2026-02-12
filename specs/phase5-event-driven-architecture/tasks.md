# Phase V: Kafka Integration Atomic Tasks

This document breaks down the Kafka integration into atomic, testable tasks, referencing the Event-Driven Architecture Specification (`specs/phase5-event-driven-architecture/spec.md`) and the Kafka Integration Architecture Plan (`specs/phase5-event-driven-architecture/plan.md`).

## 1. Kafka Environment Setup

### Task ID: KAFKA-ENV-001
-   **Description:** Define and apply Kubernetes manifests/Helm chart for Kafka cluster, ZooKeeper, and Schema Registry deployment.
-   **Preconditions:**
    -   Kubernetes cluster accessible.
-   **Expected Output:**
    -   Running Kafka brokers, ZooKeeper ensemble, and Schema Registry in the Kubernetes cluster.
    -   Verification of pod health and service accessibility.
-   **Files to Modify:**
    -   `helm/kafka/Chart.yaml` (new)
    -   `helm/kafka/values.yaml` (new)
    -   `helm/kafka/templates/*.yaml` (new)
-   **References:**
    -   `speckit.plan` (Section 2: Kafka Cluster Deployment (Kubernetes))

### Task ID: KAFKA-ENV-002
-   **Description:** Create Kafka topics (`todo.tasks.events`, `todo.reminders.events`, `todo.task_updates.broadcast`, DLQs) with specified configurations (partitions, replication factor, retention).
-   **Preconditions:**
    -   KAFKA-ENV-001 completed (Kafka cluster running).
-   **Expected Output:**
    -   All required Kafka topics created and verified using Kafka tooling (e.g., `kafka-topics.sh`).
-   **Files to Modify:**
    -   Kubernetes Job/Script for topic creation (new, e.g., `kubernetes/kafka-setup-job.yaml`)
-   **References:**
    -   `speckit.plan` (Section 3: Kafka Topic Structure)

## 2. Event Schema Definition and Management

### Task ID: SCHEMA-001
-   **Description:** Define Avro schemas for all events (`TaskCreated`, `TaskUpdated`, `TaskCompleted`, `TaskDeleted`, `ReminderScheduled`, `ReminderTriggered`, `ReminderDismissed`, `TaskChanged`).
-   **Preconditions:**
    -   Understanding of event data structures from `speckit.specify`.
-   **Expected Output:**
    -   `.avsc` files for each event schema.
-   **Files to Modify:**
    -   `schemas/avro/todo/tasks/*.avsc` (new)
    -   `schemas/avro/todo/reminders/*.avsc` (new)
-   **References:**
    -   `speckit.specify` (Section 4: Event Contracts (Schemas))
    -   `speckit.plan` (Section 4: Event Schema Definitions (Avro with Schema Registry))

### Task ID: SCHEMA-002
-   **Description:** Register Avro schemas with the Schema Registry.
-   **Preconditions:**
    -   KAFKA-ENV-001 completed (Schema Registry running).
    -   SCHEMA-001 completed (Avro schemas defined).
-   **Expected Output:**
    -   Schemas successfully registered in the Schema Registry, accessible via its API.
-   **Files to Modify:**
    -   Script/Tool for schema registration (new, e.g., `scripts/register_schemas.py`)
-   **References:**
    -   `speckit.plan` (Section 4: Event Schema Definitions (Avro with Schema Registry))

## 3. Producer Implementation (Chat API)

### Task ID: PROD-001
-   **Description:** Integrate an asynchronous Kafka producer client (`aiokafka`) into the FastAPI backend.
-   **Preconditions:**
    -   KAFKA-ENV-001 completed (Kafka/Schema Registry running).
    -   SCHEMA-002 completed (schemas registered).
-   **Expected Output:**
    -   Kafka producer initialized and configured in `backend/main.py` or a dedicated Kafka module.
-   **Files to Modify:**
    -   `backend/main.py`
    -   `backend/config.py` (for Kafka settings)
    -   `backend/services/kafka_producer.py` (new)
-   **References:**
    -   `speckit.plan` (Section 5: Producer Flow (Chat API - FastAPI Backend))

### Task ID: PROD-002
-   **Description:** Implement `TaskCreated` event production for new task creation.
-   **Preconditions:**
    -   PROD-001 completed.
    -   FastAPI task creation endpoint is functional (from previous phase).
    -   DB-001, SCH-001 completed (Advanced Features tasks).
-   **Expected Output:**
    -   Upon task creation via API, a `TaskCreated` event is successfully produced to `todo.tasks.events`.
    -   Event payload matches Avro schema.
-   **Files to Modify:**
    -   `backend/app/api/endpoints/tasks.py`
    -   `backend/app/crud.py` (post-DB commit event generation)
-   **References:**
    -   `speckit.specify` (FR1.1)
    -   `speckit.plan` (Section 5: Producer Flow)

### Task ID: PROD-003
-   **Description:** Implement `TaskUpdated`, `TaskCompleted`, `TaskDeleted` event production for task modifications.
-   **Preconditions:**
    -   PROD-001 completed.
    -   FastAPI task update/delete endpoints are functional.
    -   DB-001, SCH-001 completed.
-   **Expected Output:**
    -   Upon task update, completion, or deletion, corresponding events are produced to `todo.tasks.events`.
    -   Event payloads match Avro schemas.
-   **Files to Modify:**
    -   `backend/app/api/endpoints/tasks.py`
    -   `backend/app/crud.py`
-   **References:**
    -   `speckit.specify` (FR1.2, FR1.3, FR1.4)
    -   `speckit.plan` (Section 5: Producer Flow)

### Task ID: PROD-004
-   **Description:** Implement `ReminderScheduled`, `ReminderTriggered`, `ReminderDismissed` event production from the Reminder Service.
-   **Preconditions:**
    -   PROD-001 completed.
    -   DB-004, SCH-003 completed (Advanced Features reminders).
    -   Reminder scheduling/triggering logic is functional (from Advanced Features).
-   **Expected Output:**
    -   Reminder-related events are produced to `todo.reminders.events` at appropriate lifecycle stages.
    -   Event payloads match Avro schemas.
-   **Files to Modify:**
    -   `backend/app/api/endpoints/reminders.py` (if directly triggered by API)
    -   `backend/app/workers/reminder_worker.py` (for triggered/dismissed events)
-   **References:**
    -   `speckit.specify` (FR1.5, FR1.6, FR1.7)
    -   `speckit.plan` (Section 5: Producer Flow)

## 4. Consumer Services Creation

### Task ID: CONS-001
-   **Description:** Create and configure the Recurring Task Worker service.
-   **Preconditions:**
    -   KAFKA-ENV-001 completed.
    -   PROD-002 completed (`TaskCreated`, `TaskUpdated` events).
    -   DB-001 completed (recurring task fields).
    -   BG-001 completed (core recurring task logic).
-   **Expected Output:**
    -   A new Python service/module (`backend/app/consumers/recurring_task_consumer.py`) that consumes `todo.tasks.events`.
    -   Successfully processes `TaskCreated`/`TaskUpdated` for recurring templates.
    -   Service deployed as a Kubernetes Deployment.
-   **Files to Modify:**
    -   `backend/app/consumers/recurring_task_consumer.py` (new)
    -   `kubernetes/deployments/recurring-task-worker.yaml` (new)
-   **References:**
    -   `speckit.specify` (FR2.1)
    -   `speckit.plan` (Section 6.1: Recurring Task Worker)

### Task ID: CONS-002
-   **Description:** Create and configure the Reminder Scheduling Worker service.
-   **Preconditions:**
    -   KAFKA-ENV-001 completed.
    -   PROD-002 completed (`TaskCreated`, `TaskUpdated` events).
    -   DB-004 completed (Reminder model).
    -   BG-002 completed (core reminder scheduling logic).
-   **Expected Output:**
    -   A new Python service/module (`backend/app/consumers/reminder_scheduling_consumer.py`) that consumes `todo.tasks.events`.
    -   Successfully schedules reminders based on `due_date`.
    -   Service deployed as a Kubernetes Deployment.
-   **Files to Modify:**
    -   `backend/app/consumers/reminder_scheduling_consumer.py` (new)
    -   `kubernetes/deployments/reminder-scheduling-worker.yaml` (new)
-   **References:**
    -   `speckit.specify` (FR2.2)
    -   `speckit.plan` (Section 6.2: Reminder Scheduling Worker)

### Task ID: CONS-003
-   **Description:** Create and configure the Reminder Triggering Worker service.
-   **Preconditions:**
    -   KAFKA-ENV-001 completed.
    -   PROD-004 completed (`ReminderScheduled` events).
-   **Expected Output:**
    -   A new Python service/module (`backend/app/consumers/reminder_trigger_consumer.py`) that consumes `todo.reminders.events`.
    -   Successfully triggers notifications at `remind_at` time.
    -   Service deployed as a Kubernetes Deployment.
-   **Files to Modify:**
    -   `backend/app/consumers/reminder_trigger_consumer.py` (new)
    -   `kubernetes/deployments/reminder-trigger-worker.yaml` (new)
-   **References:**
    -   `speckit.specify` (FR2.3)
    -   `speckit.plan` (Section 6.3: Reminder Triggering Worker)

### Task ID: CONS-004
-   **Description:** Create and configure the Task Update Broadcaster service.
-   **Preconditions:**
    -   KAFKA-ENV-001 completed.
    -   PROD-002, PROD-003 completed (all `Task*` events).
-   **Expected Output:**
    -   A new Python service/module (`backend/app/consumers/task_update_broadcaster.py`) that consumes `todo.tasks.events`.
    -   Successfully produces `TaskChanged` events to `todo.task_updates.broadcast`.
    -   Service deployed as a Kubernetes Deployment.
-   **Files to Modify:**
    -   `backend/app/consumers/task_update_broadcaster.py` (new)
    -   `kubernetes/deployments/task-update-broadcaster.yaml` (new)
-   **References:**
    -   `speckit.specify` (FR1.8, FR2.4)
    -   `speckit.plan` (Section 6.4: Task Update Broadcaster)

### Task ID: CONS-005
-   **Description:** Create and configure the Audit Logging Service.
-   **Preconditions:**
    -   KAFKA-ENV-001 completed.
    -   All producer tasks completed (events flowing to topics).
-   **Expected Output:**
    -   A new Python service/module (`backend/app/consumers/audit_log_consumer.py`) that consumes relevant events.
    -   Successfully logs events to an audit store.
    -   Service deployed as a Kubernetes Deployment.
-   **Files to Modify:**
    -   `backend/app/consumers/audit_log_consumer.py` (new)
    -   `kubernetes/deployments/audit-log-service.yaml` (new)
-   **References:**
    -   `speckit.plan` (Section 6.5: Audit Logging Service)

## 5. Error Handling and Reliability

### Task ID: ERR-001
-   **Description:** Implement producer-side error handling including retries and logging to DLQ for persistent failures.
-   **Preconditions:**
    -   PROD-001 completed.
-   **Expected Output:**
    -   Producer logic handles transient Kafka errors with retries.
    -   Persistent failures result in logging to an internal DLQ or file system for recovery.
-   **Files to Modify:**
    -   `backend/services/kafka_producer.py`
    -   `backend/app/api/endpoints/tasks.py`
-   **References:**
    -   `speckit.specify` (Section 6: Failure Handling Expectations - Producer Failures)
    -   `speckit.plan` (Section 8: Error Handling and Retries - Producers)

### Task ID: ERR-002
-   **Description:** Implement consumer-side error handling for all consumer services (CONS-001 to CONS-005), including idempotency, retries, and DLQ routing.
-   **Preconditions:**
    -   All consumer services (CONS-001 to CONS-005) created.
-   **Expected Output:**
    -   Each consumer service correctly handles message processing failures with retries.
    -   Messages failing after max retries are moved to service-specific DLQs.
    -   All consumer processing is idempotent.
-   **Files to Modify:**
    -   `backend/app/consumers/*.py` (all consumer modules)
-   **References:**
    -   `speckit.specify` (Section 5: Reliability Requirements, Section 6: Failure Handling Expectations - Consumer Failures)
    -   `speckit.plan` (Section 8: Error Handling and Retries - Consumers)

## 6. Testing Strategy

### Task ID: TEST-KAFKA-001
-   **Description:** Write integration tests for Kafka topic creation and Schema Registry operations.
-   **Preconditions:**
    -   KAFKA-ENV-002 and SCHEMA-002 completed.
-   **Expected Output:**
    -   Tests verify topics exist and schemas are registered correctly.
-   **Files to Modify:**
    -   `backend/tests/test_kafka_setup.py` (new)
-   **References:** N/A

### Task ID: TEST-KAFKA-002
-   **Description:** Write integration tests for producer functionality (PROD-001 to PROD-004), verifying events are produced correctly.
-   **Preconditions:**
    -   All PROD tasks completed.
-   **Expected Output:**
    -   Tests confirm events are published to Kafka with correct schemas and content.
-   **Files to Modify:**
    -   `backend/tests/test_kafka_producers.py` (new)
-   **References:** N/A

### Task ID: TEST-KAFKA-003
-   **Description:** Write integration tests for consumer services (CONS-001 to CONS-005), verifying correct event consumption and processing.
-   **Preconditions:**
    -   All CONS tasks completed.
-   **Expected Output:**
    -   Tests simulate event flow and verify consumer logic (e.g., recurring tasks are created, reminders scheduled, audits logged).
    -   Error handling and DLQ mechanisms are tested.
-   **Files to Modify:**
    -   `backend/tests/test_kafka_consumers.py` (new)
-   **References:** N/A