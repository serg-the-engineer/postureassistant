---
id: ARCH-service-processing
title: "Service. Posture Processing"
type: service
layer: application
owner: "@team-vision"
version: v1
status: current
created: 2025-08-09
updated: 2025-08-09
tags: [processing, opencv, computer-vision, core-logic]
depends_on: [ARCH-service-settings]
referenced_by: []
---

## Context
This service contains the core logic of the application. It receives raw video frames, analyzes them to detect the user's face, and determines their posture status based on a prior calibration.

## Structure
*   **Primary File:** `src/processing_service.py`
*   **Class:** `ProcessingService(QObject)`
*   **Dependencies:** `opencv-python` for computer vision, `assets/haarcascade_frontalface_default.xml` for face detection.
*   **Key Data Structure:** `PostureStatus(Enum)` with values `CORRECT`, `INCORRECT`, `NOT_DETECTED`.

## Behavior
The service's main entry point is the `process_frame` slot, which is connected to the `CameraService`. Inside this method, it converts the frame to grayscale and uses a pre-trained Haar Cascade classifier to find faces. If a face is found, it compares its vertical position (`y` coordinate) against a calibrated reference position (`reference_y`) stored in the `SettingsService`.

If the current position is within a defined tolerance of the reference, the status is `CORRECT`; otherwise, it's `INCORRECT`. If no face is detected, the status is `NOT_DETECTED`. The service emits the new `status_updated` signal and a `processed_frame_ready` signal containing the original frame with visual overlays (face rectangle, calibration lines) drawn on it. A calibration mode can be triggered to set the `reference_y` value.

## Evolution
### v1: Initial design
*   Uses a simple but effective Haar Cascade for face detection and a 1D (vertical axis) comparison for posture analysis.
