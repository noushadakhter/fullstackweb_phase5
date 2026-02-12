# Phase V: Advanced Features Technical Architecture Plan

## 1. Introduction
This document outlines the technical architecture plan for integrating advanced features into the Todo AI Chatbot, as defined in the `spec.md`. The plan focuses on extending the existing FastAPI, SQLModel, and Neon DB stack to support recurring tasks, due dates with reminders, priorities, tags, and enhanced search/filter/sort capabilities, while adhering to the specified constraints.

## 2. Core Architectural Principles
-   **Modularity:** Ensure new features are developed with clear boundaries to minimize coupling.
-   **Scalability:** Design for potential growth in tasks and users, especially for reminder and recurring task processing.
-   **Maintainability:** Follow existing code patterns and conventions (FastAPI routing, SQLModel schemas).
-   **Data Integrity:** Implement robust validation and transactional operations.

## 3. Database Schema Updates (SQLModel)

### `Task` Model Enhancements:
-   **`due_date`**: `Optional[datetime]` - Stores the exact due date and time for the task.
-   **`priority`**: `Optional[str]` - Enum: `Low`, `Medium`, `High`. Default to `Medium`.
-   **`recurrence_pattern`**: `Optional[str]` - Stores a JSON string or a custom format defining recurrence (e.g., `{"type": "daily"}`, `{"type": "weekly", "days": ["Mon", "Wed"]}`, `{"type": "custom", "interval": 3}`).
-   **`recurrence_start_date`**: `Optional[date]` - The date from which the recurrence starts.
-   **`parent_recurring_task_id`**: `Optional[UUID]` - Foreign key to `Task.id` for instances of a recurring task.
-   **`is_recurring_template`**: `bool` - True if this task is the template for recurring tasks, False for instances.

### New `Tag` Model:
-   **`id`**: `UUID` - Primary Key.
-   **`name`**: `str` - Unique name for the tag (e.g., "work", "personal").
-   **`user_id`**: `UUID` - Foreign key to `User.id`, linking tags to specific users.

### New `TaskTag` Link Model (Many-to-Many relationship between Task and Tag):
-   **`task_id`**: `UUID` - Foreign key to `Task.id`.
-   **`tag_id`**: `UUID` - Foreign key to `Tag.id`.
-   Composite Primary Key: `(task_id, tag_id)`.

### New `Reminder` Model:
-   **`id`**: `UUID` - Primary Key.
-   **`task_id`**: `UUID` - Foreign key to `Task.id`.
-   **`remind_at`**: `datetime` - The exact datetime when the reminder should trigger.
-   **`status`**: `str` - Enum: `pending`, `triggered`, `dismissed`.

## 4. API Endpoint Changes (FastAPI)

### Task Management Endpoints (`/tasks`):
-   **`POST /tasks/`**:
    -   Request Body: `TaskCreate` schema including `due_date`, `priority`, `recurrence_pattern`, `tag_names`.
    -   Response: `TaskRead` schema.
    -   Logic: Create task, parse recurrence, create associated `TaskTag` entries.
-   **`PUT /tasks/{task_id}`**:
    -   Request Body: `TaskUpdate` schema allowing modification of `due_date`, `priority`, `recurrence_pattern`, `tag_names`, and other fields.
    -   Response: `TaskRead` schema.
    -   Logic: Update task, manage `TaskTag` entries (add/remove tags).
-   **`GET /tasks/`**:
    -   Query Parameters: `status`, `priority`, `tags` (comma-separated string), `search_query`, `sort_by` (e.g., `due_date:asc`, `priority:desc`, `created_at:asc`).
    -   Response: List of `TaskRead` schemas.
    -   Logic: Implement dynamic query building based on filters, search, and sort parameters.

### Tag Management Endpoints (`/tags`):
-   **`GET /tags/`**:
    -   Response: List of `TagRead` schemas (all tags for the authenticated user).
-   **`POST /tags/`**: (Potentially auto-created via task creation)
    -   Request Body: `TagCreate` schema including `name`.
    -   Response: `TagRead` schema.
    -   Logic: Create a new user-specific tag if it doesn't exist.

### Reminder Management Endpoints (`/reminders`):
-   **`POST /tasks/{task_id}/reminders`**:
    -   Request Body: `ReminderCreate` schema including `remind_at` (or `offset_minutes` from due date).
    -   Response: `ReminderRead` schema.
    -   Logic: Create a reminder associated with the task.
-   **`GET /tasks/{task_id}/reminders`**:
    -   Response: List of `ReminderRead` schemas for a specific task.
-   **`DELETE /reminders/{reminder_id}`**:
    -   Logic: Delete a reminder.

## 5. Validation Rules

-   **Task Title/Description:** Length constraints (Min 1, Max 255 for title; Max 1000 for description).
-   **Priority:** Must be one of `Low`, `Medium`, `High`.
-   **Due Date:** Must be a future date/time or current time for new tasks.
-   **Recurrence Pattern:** Must conform to a defined schema (e.g., `{"type": "daily"}`).
-   **Tag Name:** Length constraints (Min 1, Max 50). Special characters restriction.
-   **Tags per Task:** Maximum of 10 tags.
-   **Reminder Time:** Must be before the task's `due_date`.
-   **Search Query:** Minimum length (e.g., 2 characters).

## 6. Recurring Logic Flow

### Create Recurring Task:
1.  User creates a task with a `recurrence_pattern`.
2.  The backend marks this task as `is_recurring_template = True` and sets `recurrence_start_date`.
3.  A background worker (e.g., using `APScheduler` or a dedicated cron job) is scheduled to:
    -   Periodically check for recurring templates.
    -   Based on `recurrence_pattern` and `recurrence_start_date`, generate new task instances for the upcoming period (e.g., next 7 days).
    -   Each generated instance will have `parent_recurring_task_id` pointing to the template and `is_recurring_template = False`.
    -   Instances will have their `due_date` calculated based on the pattern.
    -   Reminders for instances will also be generated based on the template's reminder settings.

### Complete Recurring Task Instance:
1.  User marks a task instance (where `is_recurring_template = False`) as complete.
2.  This action only affects the specific instance; the `is_recurring_template = True` task remains unchanged, and future instances continue to be generated.

### Edit/Delete Recurring Task Template:
1.  If the template task (`is_recurring_template = True`) is edited, subsequent instances will reflect the changes.
2.  If the template task is deleted, all associated future instances (with `parent_recurring_task_id` pointing to it) should also be deleted or marked as orphaned.

## 7. Reminder Scheduling Logic

1.  **Creation:** When a task with a `due_date` is created/updated, or a `Reminder` object is explicitly created:
    -   Calculate the exact `remind_at` time based on `due_date` and reminder offset.
    -   Store the `Reminder` object in the database with `status = 'pending'`.
2.  **Processing:** A separate background worker/service (e.g., `APScheduler`, Celery, or a simple cron job that checks the `reminders` table) will:
    -   Periodically query for `Reminder` objects where `remind_at <= current_time` and `status = 'pending'`.
    -   For each found reminder, trigger a notification (e.g., via a WebSocket, email, or push notification service).
    -   Update the `Reminder.status` to `triggered`.
3.  **Cancellation:** If a task is marked complete *before* a reminder triggers, the associated `Reminder.status` should be updated to `dismissed`, preventing it from triggering.

## 8. Service Boundaries

-   **Authentication & Authorization Service:** Remains as is, handling user authentication and ensuring tasks/tags/reminders are scoped to the authenticated user.
-   **Task Management Service:**
    -   Handles CRUD operations for tasks.
    -   Integrates with `Tag` and `TaskTag` models for tag associations.
    -   Includes logic for dynamic filtering, searching, and sorting.
-   **Recurring Task Management Service:**
    -   Responsible for creating, managing, and generating instances of recurring tasks.
    -   Likely implemented as a separate background process or an endpoint triggered by a cron job.
-   **Reminder Service:**
    -   Manages `Reminder` objects.
    -   Responsible for scheduling and triggering notifications at the correct time.
    -   Implemented as a background process.
-   **Notification Service:** (Conceptual)
    -   Handles the actual delivery of notifications (e.g., to chatbot, email, push notifications). This service might be external or a component within the existing backend. For the initial phase, a simple in-app notification mechanism or logging could suffice.

## 9. Next Steps

-   Detailed SQLModel schema definitions.
-   FastAPI endpoint implementation with Pydantic schemas.
-   Implementation of background workers for recurrence and reminders.
-   Integration with a notification mechanism.