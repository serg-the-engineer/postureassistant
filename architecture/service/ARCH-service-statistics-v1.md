---
id: ARCH-service-statistics
title: "Service. Statistics"
type: service
layer: application
owner: "@team-vision"
version: v1
status: current
created: 2025-08-09
updated: 2025-08-09
tags: [statistics, persistence, sqlite]
depends_on: []
referenced_by: []
---

## Context
This service is responsible for logging the user's posture over time, persisting this data, and providing summaries for analysis.

## Structure
*   **Primary File:** `src/statistics_service.py`
*   **Class:** `StatisticsService`
*   **Storage:** An SQLite database file (`statistics.db`).

## Behavior
The service connects to an SQLite database and creates a `posture_log` table if it doesn't exist. It has a `handle_status_update` slot that listens for posture changes. When the status changes, it calculates the duration of the *previous* state and writes a new entry to the database with the start time, end time, duration, and state name (`CORRECT` or `INCORRECT`). It provides a `get_summary_for_today` method that queries the database to sum the total duration for each state for the current day. The database connection is configured with `check_same_thread=False` to allow access from the processing thread where the status updates originate.

## Evolution
### v1: Initial design
*   Uses a robust SQLite backend for reliable and queryable data logging.
