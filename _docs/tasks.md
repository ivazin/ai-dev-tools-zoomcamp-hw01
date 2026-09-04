# Project Backlog: Household Chore Manager

## 1. Empty Project Setup and Test Harness
Goal: Initialize the repository with a working Django 5 project, dependencies, and a passing smoke test.
Description: Create `requirements.txt` containing Django 5.x, pytest-django, and python-dotenv, then initialize the Django project `chore_manager` and main application `chores`. Configure standard development settings in `settings.py` along with a sample `.env.example` file. Add a basic test in `chores/tests/test_smoke.py` and ensure the test suite runs and passes cleanly via the command line.

## 2. Core Data Models and Migrations
Goal: Define the database schema for roommates, chore templates, active chores, and activity logs.
Description: Implement `UserProfile`, `ChoreTemplate`, `Chore`, and `ChoreLog` models in `chores/models.py` with corresponding choice enums for frequencies, statuses, and assignment strategies. Generate and apply initial database migrations using SQLite as the backing database. Write model unit tests in `chores/tests/test_models.py` verifying field validations, relationships, and string representations.

## 3. Django Admin Customization
Goal: Configure administrative views for managing household members, chore templates, chores, and activity logs.
Description: Register `UserProfile`, `ChoreTemplate`, `Chore`, and `ChoreLog` in `chores/admin.py` with custom list displays, search fields, and status filters. Add an inline log view within the `Chore` admin to display activity history directly on the chore detail page. Verify that administrators can create, update, and filter records for all models through the `/admin/` web interface.

## 4. Round-Robin Rotation Service
Goal: Implement the service logic that calculates and advances recurring chore assignments across roommates.
Description: Create `chores/services/rotation_service.py` with functions to determine the next assignee from a circular list of active housemates according to a template's rotation order. Handle edge cases such as empty roommate lists, inactive users, and order resets gracefully without crashing. Write isolated unit tests in `chores/tests/test_rotation.py` asserting deterministic progression across multiple consecutive cycles.

## 5. Chore Lifecycle and Points Award Service
Goal: Implement domain business logic for claiming open chores, completing tasks, and crediting user points.
Description: Implement service functions in `chores/services/chore_service.py` to handle chore state transitions for claiming, completing, and reassigning tasks. Ensure that task completion automatically credits the configured chore points to the completing roommate's `UserProfile` and appends an immutable entry to `ChoreLog`. Write comprehensive unit tests in `chores/tests/test_chore_service.py` verifying correct status changes, point calculations, and log creation.

## 6. Database Seed Data Management Command
Goal: Create a management command to populate the database with realistic sample household data for development.
Description: Implement a custom Django management command `seed_data` in `chores/management/commands/seed_data.py`. Generate a default household containing multiple sample roommates, common recurring chore templates, active chores with varying deadlines, and initial point distributions. Ensure the command can be safely re-run to reset or replenish development data without duplicate key conflicts.

## 7. Modern CSS Design System and Base Layout
Goal: Establish the global HTML layout shell, typography, and responsive CSS design system.
Description: Build `templates/base.html` and `static/css/styles.css` using modern Vanilla CSS with dark and light color tokens, clean typography, and a mobile-friendly layout. Integrate the HTMX library via CDN script tag to power subsequent asynchronous interactions. Include reusable styling components for cards, badges, buttons, navigation bars, and notification banners.

## 8. User Authentication and Roommate Session Views
Goal: Provide login, logout, and session handling for household roommates.
Description: Configure Django authentication views and URLs, and create a styled login page in `templates/registration/login.html`. Add an authenticated user widget to the main navigation bar displaying the logged-in roommate's name and live point score. Ensure unauthenticated visitors are redirected to the login page when attempting to access chore management views.

## 9. Main Household Dashboard and Chore Lists
Goal: Create the main dashboard view displaying personal and household chores organized by status tabs.
Description: Implement a dashboard view in `chores/views.py` and template `templates/chores/dashboard.html` with tabs for "My Chores", "All Household Chores", and "Completed Recently". Render chore cards displaying title, description, points, assignee, and due date using a modular partial `templates/chores/partials/chore_card.html`. Write view tests verifying correct context filtering by current user and task status.

## 10. Claim Pool Board with HTMX Instant Claiming
Goal: Allow roommates to browse unassigned chores and claim them instantly without page reloads.
Description: Create a claim board partial `templates/chores/partials/claim_pool.html` displaying all currently unassigned chores available for pickup. Implement an HTMX-powered POST endpoint that assigns the chosen chore to the requesting roommate and returns an updated chore card snippet. Add tests verifying that claiming a chore updates the assignee in the database, records a log entry, and renders without full-page reloads.

## 11. Chore Completion Flow with Dynamic HTMX Update
Goal: Enable roommates to mark tasks completed with real-time UI updates and points tally reflection.
Description: Implement an HTMX-powered endpoint that transitions a chore to `COMPLETED`, records the completing roommate, and updates the user's total points. Return updated chore card HTML or trigger DOM removal while updating the roommate's point counter in the header via an out-of-band swap. Write tests verifying that double-completion is prevented and point values are incremented accurately.

## 12. Chore Creation and Template Management Form
Goal: Provide forms and views for creating ad-hoc chores and recurring chore templates.
Description: Create Django model forms in `chores/forms.py` and template `templates/chores/chore_form.html` for defining one-off chores and recurring templates with frequency and rotation strategy. Implement validation for future due dates, positive point values, and optional default assignees. Write form and view tests ensuring valid submissions persist records correctly and invalid inputs display descriptive error messages.

## 13. Household Leaderboard and Fairness Metrics
Goal: Display a leaderboard ranking housemates by points earned and completed chores to promote fairness.
Description: Build a leaderboard view and template component in `templates/chores/partials/leaderboard.html` calculating total points and task counts per roommate for current and monthly intervals. Add visual progress indicators to compare contributions and highlight the most active housemate. Write unit tests validating ranking order, point calculations, and empty-state handling when no chores have been finished.

## 14. Roommate Profile and Activity History
Goal: Build a user profile view showing personal chore statistics, point totals, and completed history.
Description: Create `profile_view` in `chores/views.py` and template `templates/chores/profile.html` rendering the logged-in user's profile information, lifetime points, and completion rate. Render a paginated historical list of all chores completed by the user along with timestamped entries from `ChoreLog`. Write tests confirming that user profiles display accurate metrics and only show personal history.

## 15. Recurring Chore Generation Service
Goal: Implement the service that evaluates active chore templates and generates new chore instances on schedule.
Description: Build an automated generation service in `chores/services/scheduler.py` that checks active `ChoreTemplate` entries against their recurrence frequencies (Daily, Weekly, Bi-weekly, Monthly). For each due template, instantiate a new `Chore` record using the template's assignment strategy (Round-Robin or Claim Pool) and advance the template's rotation pointer. Add unit tests asserting proper next-run calculations and preventing duplicate chore generation within the same cycle.

## 16. Deadline Tracking and Status Transition Service
Goal: Automatically update chore urgency statuses to Due Soon or Overdue based on due dates.
Description: Implement a status evaluation routine in `chores/services/scheduler.py` that inspects pending chores and flags those within 24 hours of deadline as "Due Soon" and those past deadline as "Overdue". Update visual status attributes and record an alert event in `ChoreLog` whenever a chore transitions into an overdue state. Write unit tests with mock timestamps to verify that deadline thresholds trigger expected status updates and logs.

## 17. Background Scheduler Integration and Management Command
Goal: Integrate APScheduler to run periodic chore generation and status checks in the background and via CLI.
Description: Configure an in-process background scheduler in `chores/apps.py` to periodically trigger recurring generation and deadline checking jobs while the web server runs. Implement a standalone management command `process_tasks` in `chores/management/commands/process_tasks.py` to enable manual triggering or external cron execution. Write tests verifying that the management command executes both task generation and status checks without error.

## 18. End-to-End Workflow Integration Tests
Goal: Verify full end-to-end user workflows across chore creation, claiming, completion, rotation, and leaderboard updates.
Description: Create an end-to-end integration test suite in `chores/tests/test_integration.py` simulating a full household lifecycle across multiple roommate accounts. Verify that creating a recurring template generates chores, claiming and completing updates points, and the rotation service deterministically assigns the subsequent cycle to the next roommate. Assert that database states, point totals, and `ChoreLog` timelines remain consistent throughout the entire scenario.

## 19. Documentation, Configuration, and Developer Quickstart
Goal: Create clear documentation for setting up, running, testing, and developing the Household Chore Manager.
Description: Write a comprehensive `README.md` detailing system prerequisites, virtual environment setup, configuration options via `.env.example`, and database migration commands. Document how to seed test data, execute automated tests, and start the local development server. Include an architecture overview highlighting the HTMX interaction model and service layer design for future contributors.
