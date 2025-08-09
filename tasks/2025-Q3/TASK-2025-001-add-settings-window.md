---
id: TASK-2025-001
title: "Implement Settings Window"
status: done
priority: high
type: feature
estimate: 3h
assignee: "@dev-team"
created: 2025-08-09
updated: 2025-08-09
arch_refs: [ARCH-app-settings-window, ARCH-service-settings]
audit_log:
  - {date: 2025-08-09, user: "@AI-DocArchitect", action: "created with status done"}
---

## Description
A dedicated settings window was implemented to allow users to configure key application parameters without editing configuration files manually. This improves usability and provides control over the application's behavior.

## Acceptance Criteria
*   A "Settings" button is present in the main window's control area.
*   Clicking the button opens a modal dialog for settings.
*   The dialog allows configuration of: Posture Tolerance, Notification Enabled/Disabled, Notification Delay, and Tray Icon Blink Delay.
*   Settings are loaded from `SettingsService` when the dialog opens.
*   Changes are saved via `SettingsService` when the "Save" button is clicked.

## Definition of Done
*   Code for the `SettingsWindow` is implemented in `src/settings_window.py`.
*   The window is integrated into `MainWindow`.
*   The `SettingsService` is updated to handle all new settings.
*   Documentation (`ARCH-app-settings-window`, `ARCH-service-settings`) is updated.
