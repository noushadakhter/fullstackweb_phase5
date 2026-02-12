# Phase V: Dapr Integration Specification

## 1. Introduction
This document specifies the integration of Dapr (Distributed Application Runtime) into the Todo AI Chatbot system for Phase V. Dapr will be utilized to provide building blocks for microservices, abstracting away common complexities such as state management, pub/sub messaging, service invocation, and secret management, thereby enhancing portability, resilience, and operational efficiency.

## 2. Scope

### In Scope:
-   **Pub/Sub Abstraction over Kafka:** Dapr's Pub/Sub building block will be configured to use Kafka as the message broker, providing a standardized API for event publishing and subscription across services. This will abstract direct Kafka client interactions.
-   **State Management Abstraction:** Dapr's State Management building block will be used to store and retrieve application state, abstracting the underlying state store (e.g., PostgreSQL, Redis). This will allow for easier state management and future flexibility in state store choices.
-   **Service Invocation:** Dapr's Service Invocation building block will be used for reliable, discoverable, and secure communication between microservices (e.g., between the Chat API and a new Notification Service).
-   **Jobs API for Reminders:** Dapr's Bindings/Triggers or Actors with timers will be explored to manage scheduled reminders, potentially replacing custom background workers or providing a more robust scheduling mechanism.
-   **Secrets Management:** Dapr's Secrets building block will be used to securely retrieve application secrets (e.g., database connection strings, API keys) from a configured secrets store (e.g., Kubernetes Secrets, Azure Key Vault, AWS Secrets Manager).

### Out of Scope:
-   Dapr Actors for complex stateful logic beyond simple job scheduling.
-   Dapr Observability building block (existing monitoring solutions will be used initially).
-   Dapr Resiliency (will rely on Dapr's defaults for service invocation and Pub/Sub, custom policies will be considered in future phases).
-   Full migration of all existing internal communication to Dapr Service Invocation in Phase V.
-   In-depth security analysis of Dapr's internal mechanisms (will assume Dapr's security best practices).

## 3. Functional Requirements

### FR1: Pub/Sub Messaging
-   **FR1.1:** Services SHALL be able to publish events to Kafka topics (e.g., `todo.tasks.events`, `todo.reminders.events`) using Dapr's Pub/Sub API.
-   **FR1.2:** Services SHALL be able to subscribe to Kafka topics and receive events using Dapr's Pub/Sub API.
-   **FR1.3:** Dapr's Pub/Sub component SHALL be configured to use the existing Kafka cluster.

### FR2: State Management
-   **FR2.1:** Services SHALL be able to save and retrieve key/value state using Dapr's State Management API.
-   **FR2.2:** Dapr's State Management component SHALL be configured to use a suitable persistent store (e.g., PostgreSQL or Redis for caching).
-   **FR2.3:** Services requiring transactional state operations SHALL be able to use Dapr's transactional state API.

### FR3: Service Invocation
-   **FR3.1:** Services SHALL be able to reliably invoke methods on other Dapr-enabled services using Dapr's Service Invocation API (e.g., Chat API invoking a Notification Service).
-   **FR3.2:** Service invocation SHALL support HTTP/gRPC protocols.

### FR4: Scheduled Jobs for Reminders
-   **FR4.1:** The Reminder Service SHALL be able to schedule future tasks (reminders) using Dapr's Jobs API or timers in a Dapr Actor (if adopted).
-   **FR4.2:** Scheduled jobs SHALL reliably trigger actions at specified times.

### FR5: Secrets Management
-   **FR5.1:** Services SHALL be able to securely fetch secrets using Dapr's Secrets API from a configured secret store.
-   **FR5.2:** Dapr's Secrets component SHALL be configured to integrate with Kubernetes Secrets.

## 4. Non-Functional Requirements (NFRs)

-   **Performance:**
    -   **Latency:** Dapr sidecar introduction SHALL not add more than 10ms P95 latency to critical paths (Pub/Sub, Service Invocation, State Management).
    -   **Throughput:** Dapr integration SHALL support existing and planned throughput requirements for messaging and service interactions.
-   **Reliability:**
    -   **Resilience:** Dapr's built-in retry policies for service invocation and message delivery SHALL be utilized to enhance resilience.
    -   **Availability:** Dapr sidecars and control plane SHALL be highly available within the Kubernetes cluster.
-   **Security:**
    -   **Authentication/Authorization:** Dapr's mTLS for service invocation and integration with existing authentication mechanisms SHALL be configured where applicable.
    -   **Secrets:** Secrets retrieved via Dapr SHALL never be exposed in plain text within application code or logs.
-   **Maintainability:**
    -   Dapr configuration (components, applications) SHALL be managed via declarative YAML, integrated with existing Helm charts.
    -   Dapr upgrade paths SHALL be clear and manageable.

## 5. Portability Requirements

-   **Infrastructure Agnostic:** Services built with Dapr SHALL be deployable across different Kubernetes environments (on-prem, various cloud providers) without code changes related to underlying infrastructure (Kafka, state stores, secret stores).
-   **Language Agnostic:** Dapr's sidecar model SHALL allow services written in Python (FastAPI backend) to seamlessly interact with Dapr building blocks.

## 6. Cloud Compatibility Constraints

-   **Kubernetes Native:** Dapr integration is primarily constrained to Kubernetes environments.
-   **Kafka Compatibility:** Dapr's Pub/Sub component for Kafka SHALL be compatible with the deployed Kafka cluster version.
-   **State Store Compatibility:** Dapr's State Management component SHALL be compatible with PostgreSQL (primary database) and potentially Redis (for caching/ephemeral state).
-   **Secret Store Compatibility:** Dapr's Secrets component SHALL be compatible with Kubernetes Secrets initially. Future compatibility with cloud-specific secret stores (e.g., Azure Key Vault, AWS Secrets Manager) is desirable but not a Phase V hard constraint.

## 7. Next Steps

-   Detailed Dapr component YAML definitions for Pub/Sub, State Management, and Secrets.
-   Integration strategy for Dapr with existing FastAPI services.
-   Decision on using Dapr's Jobs API versus custom workers for reminders.
-   Kubernetes deployment manifests for Dapr sidecar injection.