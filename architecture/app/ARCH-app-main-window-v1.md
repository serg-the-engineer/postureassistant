---
id: ARCH-app-main-window
title: "App. Main Window & Orchestrator"
type: component
layer: presentation
owner: "@team-vision"
version: v1
status: current
created: 2025-08-09
updated: 2025-08-09
tags: [ui, qt, core]
depends_on:
  - ARCH-service-camera
  - ARCH-service-processing
  - ARCH-service-settings
  - ARCH-service-notification
  - ARCH-service-statistics
  - ARCH-app-statistics-window
referenced_by: []
---

## Context
The `MainWindow` is the central graphical user interface (GUI) component of the Vibestand application. It serves as the primary point of interaction for the user and acts as the central orchestrator, initializing and connecting all backend services.

## Structure
*   **Primary File:** `src/main_window.py`
*   **Class:** `MainWindow(QMainWindow)`
*   **Key UI Elements:**
    *   A `QLabel` for displaying the camera feed.
    *   Controls: `QComboBox` for camera selection, `QPushButton` for Start/Stop, Calibrate, and Statistics.
    *   A `QLabel` to display the current posture status text.
    *   A `QSystemTrayIcon` for background operation and notifications.

## Behavior
The `MainWindow` is responsible for the application's lifecycle. It initializes all services (`CameraService`, `ProcessingService`, etc.) and moves them to a separate `QThread` to keep the UI responsive. It connects the signals and slots between services, creating the main data flow pipeline: `CameraService` (frames) → `ProcessingService` (status) → `MainWindow`/`NotificationService`/`StatisticsService`.

User actions in the UI (e.g., clicking "Start") trigger methods that control the services. The window handles its own visibility, hiding to the system tray on close/minimize to allow for unintrusive background monitoring. It also emits signals when its visibility changes so the `CameraService` can reduce its frame rate and save system resources.

## Evolution
### v1: Initial design
*   Combines UI, service orchestration, and system tray management into a single, central class.
