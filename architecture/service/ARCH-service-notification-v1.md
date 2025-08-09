---
id: ARCH-service-notification
title: "Service. Notifications"
type: service
layer: application
owner: "@team-vision"
version: v1
status: current
created: 2025-08-09
updated: 2025-08-09
tags: [notification, audio, qt]
depends_on: [ARCH-service-settings]
referenced_by: []
---

## Context
This service provides non-intrusive feedback to the user about their posture, primarily through system tray notifications and optional audio alerts. It is designed to alert the user even when the main application window is hidden.

## Structure
*   **Primary File:** `src/notification_service.py`
*   **Class:** `NotificationService(QObject)`
*   **Dependencies:** `PyQt6.QtMultimedia` for audio playback.

## Behavior
The service has a slot `handle_status_update` which is connected to the `status_updated` signal from the `ProcessingService`. When the status changes to `INCORRECT`, it starts a `QTimer`. If the status remains `INCORRECT` for the duration of the timer (configured via `SettingsService`), the `show_notification` method is called. This method displays a `QSystemTrayIcon` message and plays a notification sound. If the posture is corrected before the timer finishes, the timer is stopped, preventing the notification.

## Evolution
### v1: Initial design
*   Timer-based notification logic to avoid spamming the user with alerts.
