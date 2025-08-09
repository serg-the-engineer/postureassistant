---
id: ARCH-app-statistics-window
title: "App. Statistics Window"
type: component
layer: presentation
owner: "@team-vision"
version: v1
status: current
created: 2025-08-09
updated: 2025-08-09
tags: [ui, qt, statistics, matplotlib]
depends_on: [ARCH-service-statistics]
referenced_by: []
---

## Context
This component is a dialog window responsible for visualizing the user's posture statistics for the current day.

## Structure
*   **Primary File:** `src/statistics_window.py`
*   **Classes:** `StatisticsWindow(QDialog)`, `MplCanvas(FigureCanvas)`
*   **Key UI Elements:**
    *   `MplCanvas`: A custom widget that embeds a Matplotlib figure into the PyQt6 application.
    *   `QLabel`: Displays a text summary of the statistics.

## Behavior
When instantiated, the `StatisticsWindow` requests the summary data for the day from the `StatisticsService`. It then uses this data (time spent in 'CORRECT' vs 'INCORRECT' states) to render a pie chart on the `MplCanvas`. If no data is available, it displays a message prompting the user to use the application. The window is modal, meaning the user must close it before interacting with the main window again.

## Evolution
### v1: Initial design
*   Provides a simple, effective visualization of daily posture data using Matplotlib.
