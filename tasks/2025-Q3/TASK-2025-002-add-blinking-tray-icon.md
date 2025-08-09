---
id: TASK-2025-002
title: "Add Blinking Tray Icon for Prolonged Incorrect Posture"
status: done
priority: medium
type: feature
estimate: 2h
assignee: "@dev-team"
created: 2025-08-09
updated: 2025-08-09
arch_refs: [ARCH-app-main-window, ARCH-service-settings]
audit_log:
  - {date: 2025-08-09, user: "@AI-DocArchitect", action: "created with status done"}
---

## Description
To provide a more noticeable but still unobtrusive alert, a feature was added to make the system tray icon blink after a user maintains an incorrect posture for a configurable period. This complements the one-off desktop notification.

## Acceptance Criteria
*   When posture status is `INCORRECT` for a duration longer than the "Tray Icon Blink Delay" setting, the tray icon begins to blink.
*   The blinking stops immediately when the posture status is no longer `INCORRECT`.
*   The delay threshold is configurable in the new Settings window.

## Definition of Done
*   Blinking logic using `QTimer` is implemented in `MainWindow`.
*   Icon drawing logic in `_update_tray_icon` is updated to handle the blinking state.
*   The `ARCH-app-main-window` documentation is updated to describe this new behavior.
