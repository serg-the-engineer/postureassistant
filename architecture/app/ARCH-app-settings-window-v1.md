---
id: ARCH-app-settings-window
title: "App. Settings Window"
type: component
layer: presentation
owner: "@team-vision"
version: v1
status: current
created: 2025-08-09
updated: 2025-08-09
tags: [ui, qt, settings]
depends_on:
  - ARCH-service-settings
referenced_by: []
---

## Context
This component is a dialog window that allows users to view and modify the application's configuration settings. It provides a user-friendly interface for parameters that control processing, notifications, and other visual feedback.

## Structure
*   **Primary File:** `src/settings_window.py`
*   **Class:** `SettingsWindow(QDialog)`
*   **Key UI Elements:**
    *   `QSpinBox` for posture tolerance (in pixels).
    *   `QCheckBox` to enable or disable desktop notifications.
    *   `QSpinBox` for the notification delay (in seconds).
    *   `QSpinBox` for the tray icon blinking delay (in seconds).
    *   `QDialogButtonBox` with "Save" and "Cancel" buttons.

## Behavior
When opened, the `SettingsWindow` reads the current configuration from the `SettingsService` and populates the values in its UI controls. If the user clicks "Save", the window reads the new values from the UI controls and uses the `SettingsService` to persist them. This immediately makes the new settings active across the application. If "Cancel" is clicked, any changes are discarded.

## Evolution
### v1: Initial design
*   Provides a centralized UI for managing the most important user-facing settings.
