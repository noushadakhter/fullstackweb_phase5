# Phase V: Advanced Features Atomic Tasks

This document breaks down the implementation of advanced features for the Todo AI Chatbot into atomic, testable tasks. Each task specifies its scope, preconditions, expected output, and relevant files to modify, referencing the previously defined specification (`spec.md`) and technical plan (`plan.md`).

## 1. Database Schema Updates

### Task ID: DB-001
-   **Description:** Add `due_date`, `priority`, `recurrence_pattern`, `recurrence_start_date`, `parent_recurring_task_id`, `is_recurring_template` fields to the `Task` model.
-   **Preconditions:**
    -   `Task` model exists.
-   **Expected Output:**
    -   `Task` model in `backend/models.py` updated with new fields.
    -   Alembic migration script generated to apply these changes to the database.
-   **Files to Modify:**
    -   `backend/models.py`
    -   (Alembic migration file - to be generated)
-   **References:**
    -   `speckit.specify` (Section 2.1: Due Dates & Reminders, Priorities, Recurring Tasks)
    -   `speckit.plan` (Section 3: Database Schema Updates - Task Model Enhancements)

### Task ID: DB-002
-   **Description:** Create a new `Tag` SQLModel with `id`, `name`, and `user_id`.
-   **Preconditions:**
    -   `User` model exists.
-   **Expected Output:**
    -   New `Tag` model defined in `backend/models.py`.
    -   Alembic migration script generated.
-   **Files to Modify:**
    -   `backend/models.py`
    -   (Alembic migration file - to be generated)
-   **References:**
    -   `speckit.specify` (Section 2.1: Tags)
    -   `speckit.plan` (Section 3: Database Schema Updates - New Tag Model)

### Task ID: DB-003
-   **Description:** Create a new `TaskTag` SQLModel for the many-to-many relationship between `Task` and `Tag`.
-   **Preconditions:**
    -   `Task` and `Tag` models exist.
-   **Expected Output:**
    -   New `TaskTag` model defined in `backend/models.py`.
    -   Alembic migration script generated.
-   **Files to Modify:**
    -   `backend/models.py`
    -   (Alembic migration file - to be generated)
-   **References:**
    -   `speckit.specify` (Section 2.1: Tags)
    -   `speckit.plan` (Section 3: Database Schema Updates - New TaskTag Link Model)

### Task ID: DB-004
-   **Description:** Create a new `Reminder` SQLModel with `id`, `task_id`, `remind_at`, `status`.
-   **Preconditions:**
    -   `Task` model exists.
-   **Expected Output:**
    -   New `Reminder` model defined in `backend/models.py`.
    -   Alembic migration script generated.
-   **Files to Modify:**
    -   `backend/models.py`
    -   (Alembic migration file - to be generated)
-   **References:**
    -   `speckit.specify` (Section 2.1: Due Dates & Reminders)
    -   `speckit.plan` (Section 3: Database Schema Updates - New Reminder Model)

## 2. Pydantic Schemas Updates

### Task ID: SCH-001
-   **Description:** Update `TaskCreate` and `TaskUpdate` Pydantic schemas to include new fields (`due_date`, `priority`, `recurrence_pattern`, `tag_names`).
-   **Preconditions:**
    -   `Task` related schemas exist in `backend/schemas.py`.
-   **Expected Output:**
    -   `TaskCreate` and `TaskUpdate` schemas updated.
    -   `TaskRead` schema potentially updated to include new fields for output.
-   **Files to Modify:**
    -   `backend/schemas.py`
-   **References:**
    -   `speckit.plan` (Section 4: API Endpoint Changes - Task Management Endpoints)

### Task ID: SCH-002
-   **Description:** Create `TagCreate`, `TagRead` Pydantic schemas.
-   **Preconditions:** None.
-   **Expected Output:**
    -   New `Tag` related schemas defined in `backend/schemas.py`.
-   **Files to Modify:**
    -   `backend/schemas.py`
-   **References:**
    -   `speckit.plan` (Section 4: API Endpoint Changes - Tag Management Endpoints)

### Task ID: SCH-003
-   **Description:** Create `ReminderCreate`, `ReminderRead` Pydantic schemas.
-   **Preconditions:** None.
-   **Expected Output:**
    -   New `Reminder` related schemas defined in `backend/schemas.py`.
-   **Files to Modify:**
    -   `backend/schemas.py`
-   **References:**
    -   `speckit.plan` (Section 4: API Endpoint Changes - Reminder Management Endpoints)

## 3. API Endpoint Implementation (CRUD & Logic)

### Task ID: API-001
-   **Description:** Implement `POST /tasks/` to handle task creation including `due_date`, `priority`, `recurrence_pattern`, and `tag_names`.
-   **Preconditions:**
    -   DB-001, DB-002, DB-003, SCH-001, SCH-002 completed.
    -   Existing task creation endpoint logic.
-   **Expected Output:**
    -   API endpoint successfully creates a task with all specified attributes and associated tags.
    -   Validation rules (Section 5, `speckit.plan`) for task creation are applied.
-   **Files to Modify:**
    -   `backend/app/api/endpoints/tasks.py` (or similar tasks API file)
    -   `backend/app/crud.py` (for database interactions)
-   **References:**
    -   `speckit.specify` (Section 4: FR1.1, FR2.1-FR2.3, FR3.1, FR4.1, FR5.1)
    -   `speckit.plan` (Section 4: POST /tasks/, Section 5: Validation Rules)

### Task ID: API-002
-   **Description:** Implement `PUT /tasks/{task_id}` to handle task updates, including modification of `due_date`, `priority`, `recurrence_pattern`, and `tag_names`.
-   **Preconditions:**
    -   DB-001, DB-002, DB-003, SCH-001, SCH-002 completed.
    -   Existing task update endpoint logic.
-   **Expected Output:**
    -   API endpoint successfully updates a task with all specified attributes and manages associated tags (add/remove).
    -   Validation rules (Section 5, `speckit.plan`) for task update are applied.
-   **Files to Modify:**
    -   `backend/app/api/endpoints/tasks.py`
    -   `backend/app/crud.py`
-   **References:**
    -   `speckit.specify` (Section 4: FR1.3, FR2.5, FR3.1, FR4.1, FR5.1-FR5.2)
    -   `speckit.plan` (Section 4: PUT /tasks/{task_id}, Section 5: Validation Rules)

### Task ID: API-003
-   **Description:** Implement `GET /tasks/` with query parameters for filtering by `status`, `priority`, `tags`, `search_query`, and sorting by `sort_by`.
-   **Preconditions:**
    -   DB-001, DB-002, DB-003, SCH-001, SCH-002 completed.
    -   Existing task listing endpoint.
-   **Expected Output:**
    -   API endpoint returns tasks filtered, searched, and sorted according to query parameters.
    -   Acceptance criteria for search, filter, and sort (Section 5, `speckit.specify`) are met.
-   **Files to Modify:**
    -   `backend/app/api/endpoints/tasks.py`
    -   `backend/app/crud.py` (for complex query building)
-   **References:**
    -   `speckit.specify` (Section 4: FR6.1-FR6.2, FR7.1-FR7.4, FR8.1-FR8.3)
    -   `speckit.plan` (Section 4: GET /tasks/)

### Task ID: API-004
-   **Description:** Implement `GET /tags/` to retrieve all tags for the authenticated user.
-   **Preconditions:**
    -   DB-002, SCH-002 completed.
-   **Expected Output:**
    -   API endpoint returns a list of `TagRead` schemas belonging to the current user.
-   **Files to Modify:**
    -   `backend/app/api/endpoints/tags.py` (new file or add to existing)
    -   `backend/app/crud.py`
-   **References:**
    -   `speckit.specify` (Section 4: FR5.3)
    -   `speckit.plan` (Section 4: GET /tags/)

### Task ID: API-005
-   **Description:** Implement `POST /tasks/{task_id}/reminders` to create a new reminder for a task.
-   **Preconditions:**
    -   DB-004, SCH-003 completed.
-   **Expected Output:**
    -   API endpoint successfully creates a `Reminder` object associated with the specified task.
    -   Validation rules (Section 5, `speckit.plan`) for reminder creation are applied.
-   **Files to Modify:**
    -   `backend/app/api/endpoints/reminders.py` (new file or add to existing)
    -   `backend/app/crud.py`
-   **References:**
    -   `speckit.specify` (Section 4: FR3.2-FR3.3)
    -   `speckit.plan` (Section 4: POST /tasks/{task_id}/reminders, Section 5: Validation Rules)

### Task ID: API-006
-   **Description:** Implement `GET /tasks/{task_id}/reminders` and `DELETE /reminders/{reminder_id}`.
-   **Preconditions:**
    -   DB-004, SCH-003 completed.
-   **Expected Output:**
    -   `GET` endpoint returns reminders for a task.
    -   `DELETE` endpoint successfully removes a reminder.
-   **Files to Modify:**
    -   `backend/app/api/endpoints/reminders.py`
    -   `backend/app/crud.py`
-   **References:**
    -   `speckit.plan` (Section 4: Reminder Management Endpoints)

## 4. Background Workers/Services

### Task ID: BG-001
-   **Description:** Develop a background worker (e.g., using `APScheduler`) to process recurring task templates and generate instances.
-   **Preconditions:**
    -   DB-001 completed.
    -   API-001, API-002 support `recurrence_pattern` and `is_recurring_template`.
-   **Expected Output:**
    -   Worker periodically runs and creates new task instances based on recurring templates.
    -   New instances have correct `parent_recurring_task_id` and `due_date`.
    -   New instances have associated reminders generated.
-   **Files to Modify:**
    -   `backend/app/agent_runner.py` (or similar entry point for background jobs)
    -   New background worker module (e.g., `backend/app/workers/recurring_tasks_worker.py`)
    -   `backend/main.py` (to integrate worker)
-   **References:**
    -   `speckit.plan` (Section 6: Recurring Logic Flow, Section 8: Recurring Task Management Service)

### Task ID: BG-002
-   **Description:** Develop a background worker to trigger notifications for `pending` reminders at their `remind_at` time.
-   **Preconditions:**
    -   DB-004 completed.
    -   API-005 supports reminder creation.
-   **Expected Output:**
    -   Worker periodically checks for `pending` reminders.
    -   Triggers a notification mechanism (e.g., logging for now, or a placeholder for future notification service integration).
    -   Updates `Reminder.status` to `triggered`.
-   **Files to Modify:**
    -   `backend/app/agent_runner.py` (or similar)
    -   New background worker module (e.g., `backend/app/workers/reminder_worker.py`)
    -   `backend/main.py` (to integrate worker)
-   **References:**
    -   `speckit.specify` (Section 4: FR3.4)
    -   `speckit.plan` (Section 7: Reminder Scheduling Logic, Section 8: Reminder Service)

### Task ID: BG-003
-   **Description:** Enhance `Task` completion logic to update associated `Reminder` status to `dismissed`.
-   **Preconditions:**
    -   DB-004 completed.
-   **Expected Output:**
    -   When a task is marked `completed`, its associated `pending` reminders are marked `dismissed`.
-   **Files to Modify:**
    -   `backend/app/crud.py` (task update logic)
-   **References:**
    -   `speckit.plan` (Section 7: Reminder Scheduling Logic - Cancellation)

## 5. General Enhancements

### Task ID: GEN-001
-   **Description:** Implement logic for task status updates (e.g., `completed`, `incomplete`).
-   **Preconditions:** None.
-   **Expected Output:** Tasks can be toggled between completed and incomplete status.
-   **Files to Modify:**
    -   `backend/app/api/endpoints/tasks.py`
    -   `backend/app/crud.py`
-   **References:**
    -   `speckit.specify` (Section 4: FR1.2)

### Task ID: GEN-002
-   **Description:** Integrate authentication and authorization to ensure tasks/tags/reminders are scoped to the authenticated user.
-   **Preconditions:**
    -   Existing authentication system.
    -   All API endpoints implemented.
-   **Expected Output:**
    -   Users can only access/modify their own tasks, tags, and reminders.
-   **Files to Modify:**
    -   `backend/app/api/endpoints/tasks.py`
    -   `backend/app/api/endpoints/reminders.py`
    -   `backend/app/api/endpoints/tags.py`
    -   `backend/app/dependencies.py`
-   **References:**
    -   `speckit.plan` (Section 8: Authentication & Authorization Service)

## 6. Testing

### Task ID: TEST-001
-   **Description:** Write unit and integration tests for DB-001 to DB-004 (Database schema updates).
-   **Preconditions:** DB-001 to DB-004 completed.
-   **Expected Output:** All database-related tests pass.
-   **Files to Modify:**
    -   `backend/tests/test_models.py` (new or existing)
-   **References:** N/A (General testing practice)

### Task ID: TEST-002
-   **Description:** Write unit and integration tests for SCH-001 to SCH-003 (Pydantic schemas).
-   **Preconditions:** SCH-001 to SCH-003 completed.
-   **Expected Output:** All schema-related tests pass, ensuring correct serialization/deserialization and validation.
-   **Files to Modify:**
    -   `backend/tests/test_schemas.py` (new or existing)
-   **References:** N/A

### Task ID: TEST-003
-   **Description:** Write integration tests for API-001 to API-006 (API endpoints).
-   **Preconditions:** API-001 to API-006 completed.
-   **Expected Output:** All API endpoint tests pass, covering CRUD operations, filtering, searching, and sorting as per acceptance criteria.
-   **Files to Modify:**
    -   `backend/tests/test_api.py` (new or existing)
-   **References:**
    -   `speckit.specify` (Section 5: Acceptance Criteria)

### Task ID: TEST-004
-   **Description:** Write integration tests for BG-001 to BG-003 (Background workers/services).
-   **Preconditions:** BG-001 to BG-003 completed.
-   **Expected Output:** All background worker tests pass, verifying recurring task generation, reminder triggering, and reminder cancellation.
-   **Files to Modify:**
    -   `backend/tests/test_workers.py` (new or existing)
-   **References:**
    -   `speckit.specify` (Section 5: AC1, AC2)