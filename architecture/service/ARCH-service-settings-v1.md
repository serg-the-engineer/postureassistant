---
id: ARCH-service-settings
title: "Service. Settings"
type: service
layer: infrastructure
owner: "@team-vision"
version: v1
status: current
created: 2025-08-09
updated: 2025-08-09
tags: [settings, persistence, json]
depends_on: []
referenced_by: []
---

## Context
This service provides a simple mechanism for persisting application settings and user preferences between sessions.

## Structure
*   **Primary File:** `src/settings_service.py`
*   **Class:** `SettingsService`
*   **Storage Format:** A local `settings.json` file.

## Behavior
The service loads settings from `settings.json` upon initialization. If the file doesn't exist or is invalid, it falls back to a set of default values. It provides simple `get` and `set` methods for other services to read and write configuration values. Any call to `set` immediately triggers a save to the JSON file, ensuring data is not lost.

It manages key application parameters, including:
*   `camera_id`: The index of the selected camera.
*   `calibration_data`: A dictionary containing `reference_y` and `tolerance_pixels` for posture detection.
*   `notifications_enabled`: A boolean to toggle desktop notifications.
*   `notification_delay_seconds`: The time to wait in an incorrect posture before sending a desktop notification.
*   `blinking_threshold_seconds`: The time to wait in an incorrect posture before the tray icon starts blinking.

## Evolution
### v1: Initial design
*   Simple file-based persistence using JSON, sufficient for the application's needs.
