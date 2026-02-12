# Phase V: Dapr Integration Structured Implementation Tasks

This document details the structured implementation tasks for integrating Dapr into the Todo AI Chatbot, referencing the Dapr Integration Specification (`specs/phase5-dapr-integration/spec.md`) and the Technical Architecture Plan (`specs/phase5-dapr-integration/plan.md`).

## 1. Dapr Installation and Configuration

### Task ID: DAPR-INSTALL-001
-   **Description:** Install Dapr CLI on local development machines and deploy Dapr control plane to the Kubernetes cluster.
-   **Preconditions:**
    -   Kubernetes cluster accessible.
    -   `kubectl` configured.
-   **Expected Output:**
    -   `dapr` CLI installed and functional.
    -   Dapr control plane pods (`dapr-operator`, `dapr-sidecar-injector`, `dapr-placement`, `dapr-sentry`) running in `dapr-system` namespace.
-   **Files to Modify:** N/A (CLI commands and Helm charts)
-   **References:**
    -   `speckit.plan` (Section 2: Dapr Sidecar Architecture)

### Task ID: DAPR-COMP-001
-   **Description:** Create and apply Dapr component YAML for `pubsub-kafka-todo` (Kafka Pub/Sub).
-   **Preconditions:**
    -   DAPR-INSTALL-001 completed.
    -   Kafka cluster and Schema Registry running.
    -   `specs/phase5-event-driven-architecture/SCHEMA-001` (Avro schemas) completed.
-   **Expected Output:**
    -   `pubsub-kafka-todo` Dapr component successfully deployed and visible via `dapr components -k`.
-   **Files to Modify:**
    -   `kubernetes/components/pubsub-kafka-todo.yaml` (new)
-   **References:**
    -   `speckit.specify` (FR1.3)
    -   `speckit.plan` (Section 3.1: Pub/Sub Component)

### Task ID: DAPR-COMP-002
-   **Description:** Create and apply Dapr component YAML for `state-postgresql-todo` (PostgreSQL State Store).
-   **Preconditions:**
    -   DAPR-INSTALL-001 completed.
    -   PostgreSQL database accessible.
-   **Expected Output:**
    -   `state-postgresql-todo` Dapr component successfully deployed and visible via `dapr components -k`.
-   **Files to Modify:**
    -   `kubernetes/components/state-postgresql-todo.yaml` (new)
-   **References:**
    -   `speckit.specify` (FR2.2)
    -   `speckit.plan` (Section 3.2: State Management Component)

### Task ID: DAPR-COMP-003
-   **Description:** Create and apply Dapr component YAML for `secretstore-kubernetes-todo` (Kubernetes Secrets Store).
-   **Preconditions:**
    -   DAPR-INSTALL-001 completed.
-   **Expected Output:**
    -   `secretstore-kubernetes-todo` Dapr component successfully deployed and visible via `dapr components -k`.
-   **Files to Modify:**
    -   `kubernetes/components/secretstore-kubernetes-todo.yaml` (new)
-   **References:**
    -   `speckit.specify` (FR5.2)
    -   `speckit.plan` (Section 3.3: Secrets Management Component)

## 2. Replacing Direct Kafka Usage with Dapr Pub/Sub

### Task ID: DAPR-PUBSUB-001
-   **Description:** Update FastAPI backend to publish `TaskCreated` events using Dapr Pub/Sub API.
-   **Preconditions:**
    -   DAPR-COMP-001 completed.
    -   `specs/phase5-event-driven-architecture/PROD-002` completed (direct Kafka producer for `TaskCreated`).
    -   Python Dapr SDK installed (`dapr-sdk-python`).
-   **Expected Output:**
    -   `TaskCreated` events are published via Dapr `pubsub-kafka-todo` component to `todo.tasks.events`.
    -   Direct Kafka producer code for `TaskCreated` is removed.
-   **Files to Modify:**
    -   `backend/app/api/endpoints/tasks.py`
    -   `backend/app/crud.py`
    -   `backend/services/kafka_producer.py` (modification/removal)
-   **References:**
    -   `speckit.specify` (FR1.1)
    -   `speckit.plan` (Section 7: Integration with Python FastAPI Backend - Pub/Sub)

### Task ID: DAPR-PUBSUB-002
-   **Description:** Update FastAPI backend and consumer services to publish `TaskUpdated`, `TaskCompleted`, `TaskDeleted`, and Reminder-related events using Dapr Pub/Sub API.
-   **Preconditions:**
    -   DAPR-COMP-001 completed.
    -   `specs/phase5-event-driven-architecture/PROD-003`, `PROD-004` completed.
-   **Expected Output:**
    -   All task and reminder lifecycle events are published via Dapr Pub/Sub.
    -   Direct Kafka producer code is removed/updated.
-   **Files to Modify:**
    -   `backend/app/api/endpoints/tasks.py`
    -   `backend/app/crud.py`
    -   `backend/app/workers/reminder_worker.py`
    -   `backend/services/kafka_producer.py` (modification/removal)
-   **References:**
    -   `speckit.specify` (FR1.1, FR1.2, FR1.3, FR1.4, FR1.5, FR1.6, FR1.7)
    -   `speckit.plan` (Section 7: Integration with Python FastAPI Backend - Pub/Sub)

### Task ID: DAPR-PUBSUB-003
-   **Description:** Update consumer services (Recurring Task Worker, Reminder Scheduling Worker, Reminder Triggering Worker, Task Update Broadcaster, Audit Logging Service) to subscribe to Kafka topics using Dapr Pub/Sub API.
-   **Preconditions:**
    -   DAPR-COMP-001 completed.
    -   `specs/phase5-event-driven-architecture/CONS-001` to `CONS-005` completed.
-   **Expected Output:**
    -   Consumer services subscribe to events via Dapr, defining subscription routes in their FastAPI/Python apps.
    -   Direct Kafka consumer code is removed.
-   **Files to Modify:**
    -   `backend/app/consumers/*.py` (all consumer modules)
    -   `backend/main.py` (if subscriptions are declared in main app)
-   **References:**
    -   `speckit.specify` (FR1.2, FR1.3, FR1.4)
    -   `speckit.plan` (Section 7: Integration with Python FastAPI Backend - Pub/Sub)

## 3. Implement Jobs API / Reminder Scheduling

### Task ID: DAPR-JOBS-001
-   **Description:** Implement reminder scheduling using Dapr's Output Binding (e.g., `bindings.cron`) or stateful Actors with timers within the Reminder Service.
-   **Preconditions:**
    -   DAPR-COMP-001 (Pub/Sub) for eventing from Reminder Service.
    -   `specs/phase5-advanced-features/BG-002` (Reminder triggering worker) exists.
-   **Expected Output:**
    -   Reminder Service schedules future invocations via Dapr binding/actors.
    -   Custom background worker for reminder triggering (`backend/app/workers/reminder_worker.py`) is replaced or simplified by Dapr.
-   **Files to Modify:**
    -   `backend/app/api/endpoints/reminders.py` (for scheduling)
    -   `backend/app/workers/reminder_worker.py` (modification/removal)
    -   `kubernetes/components/timer-todo-reminders.yaml` (new Dapr binding component, if using)
-   **References:**
    -   `speckit.specify` (FR4.1, FR4.2)
    -   `speckit.plan` (Section 4: Jobs API Integration Design)

## 4. Implement State Management

### Task ID: DAPR-STATE-001
-   **Description:** Integrate Dapr State Management API for application state persistence where applicable (e.g., for specific Dapr Actor state if adopted, or for shared configuration).
-   **Preconditions:**
    -   DAPR-COMP-002 completed.
    -   Python Dapr SDK installed.
-   **Expected Output:**
    -   Application services can save and retrieve state using Dapr's State API.
-   **Files to Modify:**
    -   `backend/app/services/*.py` (where state is managed)
-   **References:**
    -   `speckit.specify` (FR2.1)
    -   `speckit.plan` (Section 7: Integration with Python FastAPI Backend - State Management)

## 5. Implement Secrets Retrieval

### Task ID: DAPR-SECRETS-001
-   **Description:** Modify services to retrieve sensitive configurations (e.g., DB connection strings, API keys) using Dapr Secrets API.
-   **Preconditions:**
    -   DAPR-COMP-003 completed.
    -   Kubernetes Secrets configured with necessary values.
    -   Python Dapr SDK installed.
-   **Expected Output:**
    -   Application services retrieve secrets via Dapr API calls.
    -   Direct environment variable or file-based secret loading is replaced.
-   **Files to Modify:**
    -   `backend/config.py`
    -   `backend/db.py` (for connection string)
-   **References:**
    -   `speckit.specify` (FR5.1)
    -   `speckit.plan` (Section 7: Integration with Python FastAPI Backend - Secrets)

## 6. Service Invocation

### Task ID: DAPR-INVOKE-001
-   **Description:** Implement Dapr Service Invocation for inter-service communication (e.g., Chat API calling a new Notification Service).
-   **Preconditions:**
    -   DAPR-INSTALL-001 completed.
    -   Target service is Dapr-enabled.
    -   Python Dapr SDK installed.
-   **Expected Output:**
    -   Service-to-service calls utilize Dapr's Service Invocation API.
-   **Files to Modify:**
    -   `backend/app/api/endpoints/tasks.py` (if calling another service)
    -   `backend/app/services/notification_service.py` (new service)
-   **References:**
    -   `speckit.specify` (FR3.1)
    -   `speckit.plan` (Section 5: Service Invocation Flow)

## 7. Kubernetes Deployment Updates

### Task ID: DAPR-K8S-001
-   **Description:** Add Dapr annotations to existing Kubernetes Deployment YAMLs for all FastAPI backend and consumer services to enable sidecar injection.
-   **Preconditions:**
    -   DAPR-INSTALL-001 completed.
    -   All services have existing Kubernetes Deployment YAMLs.
-   **Expected Output:**
    -   All application pods automatically start with a Dapr sidecar.
    -   Services can communicate with Dapr APIs.
-   **Files to Modify:**
    -   `kubernetes/deployments/*.yaml` (all service deployment files)
-   **References:**
    -   `speckit.plan` (Section 6: Kubernetes Application Deployment Annotations)

## 8. Testing

### Task ID: TEST-DAPR-001
-   **Description:** Write integration tests to verify Dapr Pub/Sub functionality (publishers and subscribers).
-   **Preconditions:**
    -   All DAPR-PUBSUB tasks completed.
-   **Expected Output:**
    -   Tests confirm events flow correctly through Dapr Pub/Sub.
-   **Files to Modify:**
    -   `backend/tests/test_dapr_pubsub.py` (new)
-   **References:** N/A

### Task ID: TEST-DAPR-002
-   **Description:** Write integration tests to verify Dapr Secrets retrieval.
-   **Preconditions:**
    -   DAPR-SECRETS-001 completed.
-   **Expected Output:**
    -   Tests confirm secrets are retrieved securely via Dapr.
-   **Files to Modify:**
    -   `backend/tests/test_dapr_secrets.py` (new)
-   **References:** N/A

### Task ID: TEST-DAPR-003
-   **Description:** Write integration tests to verify Dapr Service Invocation.
-   **Preconditions:**
    -   DAPR-INVOKE-001 completed.
-   **Expected Output:**
    -   Tests confirm inter-service calls using Dapr work correctly.
-   **Files to Modify:**
    -   `backend/tests/test_dapr_invocation.py` (new)
-   **References:** N/A

### Task ID: TEST-DAPR-004
-   **Description:** Write integration tests for Dapr Jobs API / reminder scheduling.
-   **Preconditions:**
    -   DAPR-JOBS-001 completed.
-   **Expected Output:**
    -   Tests confirm reminders are scheduled and triggered correctly by Dapr.
-   **Files to Modify:**
    -   `backend/tests/test_dapr_jobs.py` (new)
-   **References:** N/A