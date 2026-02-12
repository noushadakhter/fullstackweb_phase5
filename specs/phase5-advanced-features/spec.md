# Phase V: Advanced Features Specification for Todo AI Chatbot

## 1. Introduction
This document outlines the detailed specification for implementing advanced features in Phase V of the Todo AI Chatbot project. The goal is to enhance user task management capabilities by introducing recurring tasks, due dates with reminders, task priorities, tagging, and robust search, filter, and sort functionalities.

## 2. Scope

### In Scope:
-   **Recurring Tasks:**
    -   Daily recurrence.
    -   Weekly recurrence on specific days of the week.
    -   Custom interval recurrence (e.g., every N days).
    -   Ability to mark a recurring task's current instance as complete without affecting future instances.
-   **Due Dates & Reminders:**
    -   Setting a specific due date and time for a task.
    -   Setting reminders at configurable intervals before the due date (e.g., 15 mins, 1 hour, 1 day).
-   **Priorities:**
    -   Assigning a priority level to tasks: Low, Medium, High.
-   **Tags:**
    -   Attaching multiple descriptive tags to a single task (e.g., #work, #personal, #urgent).
    -   Viewing all tasks associated with a specific tag.
-   **Search:**
    -   Keyword-based search across task titles and descriptions.
-   **Filter:**
    -   Filtering tasks by status (e.g., pending, completed).
    -   Filtering tasks by priority (Low, Medium, High).
    -   Filtering tasks by one or more selected tags.
-   **Sort:**
    -   Sorting tasks by due date (ascending/descending).
    -   Sorting tasks by priority (High to Low, Low to High).
    -   Sorting tasks by creation date (newest/oldest).

### Out of Scope:
-   Complex recurring patterns (e.g., monthly on the first Monday, yearly).
-   Location-based reminders.
-   Sub-tasks or task dependencies.
-   Natural language processing for setting due dates or recurrence.

## 3. User Journeys

### User Journey: Creating a Recurring Daily Task
1.  User initiates creation of a new task (e.g., "Add new task").
2.  User provides task title and optional description.
3.  User selects "Recurrence" option.
4.  User selects "Daily" from recurrence options.
5.  System confirms daily recurring task creation.
6.  Each day, a new instance of the task appears in the user's task list until explicitly stopped.

### User Journey: Setting a Due Date and Reminder
1.  User selects an existing task or creates a new one.
2.  User chooses "Set Due Date" option.
3.  User inputs a specific date and time for the task.
4.  User chooses "Add Reminder" option.
5.  User selects reminder interval (e.g., "1 hour before").
6.  System confirms due date and reminder setup.
7.  At the specified reminder time, the user receives a notification.

### User Journey: Assigning Priority and Tags
1.  User selects an existing task.
2.  User chooses "Set Priority" option.
3.  User selects "High" priority.
4.  User chooses "Add Tag" option.
5.  User types a new tag (e.g., "meeting") or selects from existing tags.
6.  User adds another tag (e.g., "client").
7.  System updates task with "High" priority and "meeting", "client" tags.

### User Journey: Searching for Tasks
1.  User activates search functionality.
2.  User types a keyword (e.g., "report").
3.  System displays all tasks whose title or description contains "report".

### User Journey: Filtering Tasks
1.  User activates filter functionality.
2.  User selects "Priority" filter and chooses "High".
3.  System displays all tasks with "High" priority.
4.  User refines filter by also selecting "Tag" filter and choosing "#work".
5.  System displays all "High" priority tasks that also have the "#work" tag.

### User Journey: Sorting Tasks
1.  User activates sort functionality.
2.  User selects "Sort by Due Date" with "Ascending" order.
3.  System reorders the displayed tasks with the soonest due dates first.

## 4. Functional Requirements

### FR1: Task Creation and Management
-   **FR1.1:** Users SHALL be able to create new tasks with a title and optional description.
-   **FR1.2:** Users SHALL be able to mark tasks as complete or incomplete.
-   **FR1.3:** Users SHALL be able to edit existing tasks.

### FR2: Recurring Tasks
-   **FR2.1:** Users SHALL be able to set a task to recur daily.
-   **FR2.2:** Users SHALL be able to set a task to recur weekly on selected days (e.g., Monday, Wednesday, Friday).
-   **FR2.3:** Users SHALL be able to set a task to recur at a custom interval (e.g., every 3 days, every 7 days).
-   **FR2.4:** Completing an instance of a recurring task SHALL NOT affect future instances.
-   **FR2.5:** Users SHALL be able to stop recurrence for a task.

### FR3: Due Dates and Reminders
-   **FR3.1:** Users SHALL be able to assign a specific due date and time to a task.
-   **FR3.2:** Users SHALL be able to set reminders for tasks.
-   **FR3.3:** Reminder intervals SHALL include at least: 15 minutes before, 1 hour before, 1 day before.
-   **FR3.4:** The system SHALL generate notifications for reminders.

### FR4: Priorities
-   **FR4.1:** Users SHALL be able to assign a priority level (Low, Medium, High) to any task.
-   **FR4.2:** Default priority for new tasks SHALL be Medium.

### FR5: Tags
-   **FR5.1:** Users SHALL be able to add multiple custom tags to a task.
-   **FR5.2:** Users SHALL be able to remove tags from a task.
-   **FR5.3:** The system SHALL maintain a list of unique tags used by the user.

### FR6: Search
-   **FR6.1:** Users SHALL be able to perform a keyword search across task titles and descriptions.
-   **FR6.2:** Search SHALL be case-insensitive.

### FR7: Filter
-   **FR7.1:** Users SHALL be able to filter tasks by their completion status (pending, completed).
-   **FR7.2:** Users SHALL be able to filter tasks by their assigned priority (Low, Medium, High).
-   **FR7.3:** Users SHALL be able to filter tasks by one or more selected tags.
-   **FR7.4:** Multiple filter criteria (status, priority, tags) SHALL be combinable using an "AND" logic.

### FR8: Sort
-   **FR8.1:** Users SHALL be able to sort tasks by due date in ascending or descending order.
-   **FR8.2:** Users SHALL be able to sort tasks by priority (High to Low, Low to High).
-   **FR8.3:** Users SHALL be able to sort tasks by creation date (newest first, oldest first).

## 5. Acceptance Criteria

### AC1: Recurring Tasks
-   **AC1.1:** A task set to recur daily appears in the task list every day at the specified time or at the beginning of the day if no time is specified.
-   **AC1.2:** A task set to recur weekly on Mon, Wed, Fri appears on those days, and completing Monday's instance does not affect Wednesday's instance.
-   **AC1.3:** A task set to recur every 3 days correctly generates new instances every third day.
-   **AC1.4:** Stopping recurrence prevents any new instances from being created.

### AC2: Due Dates & Reminders
-   **AC2.1:** A task with a due date of "tomorrow 10:00 AM" correctly shows "tomorrow 10:00 AM" as its due date.
-   **AC2.2:** A reminder set for "1 hour before" a task due at 3:00 PM triggers a notification at 2:00 PM.
-   **AC2.3:** Reminders are clearly distinguishable from other system notifications.

### AC3: Priorities
-   **AC3.1:** A task assigned "High" priority is visibly differentiated from "Medium" or "Low" priority tasks in the UI.
-   **AC3.2:** Changing a task's priority updates its display accordingly.

### AC4: Tags
-   **AC4.1:** Adding "#work" and "#urgent" tags to a task displays both tags alongside the task.
-   **AC4.2:** Clicking on a tag (e.g., "#work") displays all tasks associated with "#work".
-   **AC4.3:** Removing a tag (e.g., "#urgent") from a task no longer displays that tag for the task.

### AC5: Search
-   **AC5.1:** Searching for "report" returns tasks with titles like "Project Report" and descriptions like "Prepare financial report".
-   **AC5.2:** Searching for "Report" returns the same results as "report".

### AC6: Filter
-   **AC6.1:** Filtering by "completed" status displays only completed tasks.
-   **AC6.2:** Filtering by "High" priority displays only tasks marked as High priority.
-   **AC6.3:** Filtering by "#work" tag displays only tasks with the "#work" tag.
-   **AC6.4:** Filtering by "High" priority AND "#work" tag displays only tasks that are both high priority and have the "#work" tag.

### AC7: Sort
-   **AC7.1:** Sorting by "Due Date (Ascending)" arranges tasks from nearest due date to furthest.
-   **AC7.2:** Sorting by "Priority (High to Low)" arranges tasks with High priority first, then Medium, then Low.
-   **AC7.3:** Sorting by "Creation Date (Newest First)" places the most recently created tasks at the top.

## 6. Edge Cases

-   **Recurring Tasks:**
    -   What happens if a recurring task's due date falls on a non-existent date (e.g., Feb 30th)? (Not applicable with current recurrence scope).
    -   What if a user tries to complete a future instance of a recurring task? (Only current instance can be completed).
    -   What if a recurring task is created with an interval that makes it recur less frequently than once a month, e.g. every 366 days? (Should function correctly based on N days).
-   **Due Dates & Reminders:**
    -   What if a reminder is set *after* the due date? (System should prevent this or warn the user).
    -   What if a task is marked complete before a reminder triggers? (Reminder should be cancelled).
    -   What if multiple reminders are set for the same task? (All should trigger independently or as configured).
-   **Priorities:**
    -   What if no priority is explicitly set? (Default to Medium).
-   **Tags:**
    -   What if a task has too many tags? (UI might need to handle display gracefully).
    -   What if a tag name is too long? (Truncate or wrap in UI).
    -   What if a user tries to create a tag with special characters? (Sanitize input or restrict characters).
    -   What if a user deletes a tag that is used by many tasks? (Tag should be removed from all associated tasks, and from the global tag list if no longer used by any task).
-   **Search:**
    -   What if the search query is empty? (Return all tasks or no results).
    -   What if the search query contains only spaces? (Treat as empty query).
-   **Filter:**
    -   What if no tasks match the filter criteria? (Display "No matching tasks").
    -   What if filters conflict (e.g., filter by both "completed" and "pending")? (Logically impossible with distinct status values, but if possible, result in no tasks).
-   **Sort:**
    -   What if two tasks have the same due date/priority/creation date? (Maintain existing relative order or apply secondary sort criteria).

## 7. Domain Constraints

-   **Task Title Length:** Minimum 1 character, Maximum 255 characters.
-   **Task Description Length:** Maximum 1000 characters (optional).
-   **Tag Name Length:** Minimum 1 character, Maximum 50 characters.
-   **Maximum Tags per Task:** 10 tags.
-   **Date & Time Format:** All dates and times SHALL adhere to ISO 8601 standard internally. Display format can be localized.
-   **Recurrence Interval:** Positive integers only for "every N days".
-   **Reminder Intervals:** Predefined intervals plus user-defined custom intervals.
