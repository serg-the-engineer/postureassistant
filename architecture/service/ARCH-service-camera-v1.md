---
id: ARCH-service-camera
title: "Service. Camera"
type: service
layer: infrastructure
owner: "@team-vision"
version: v1
status: current
created: 2025-08-09
updated: 2025-08-09
tags: [camera, opencv, video, thread]
depends_on: []
referenced_by: []
---

## Context
This service is responsible for all interactions with the system's webcams. Its primary purpose is to discover available cameras, capture video frames from the selected device, and provide them to other services for processing.

## Structure
*   **Primary File:** `src/camera_service.py`
*   **Class:** `CameraService(QThread)`
*   **Dependencies:** `opencv-python`, `pygrabber` (Windows), `pyobjc-framework-avfoundation` (macOS).

## Behavior
The service runs in a dedicated `QThread` to prevent video capture from blocking the main UI thread. It uses `cv2.VideoCapture` to open a connection to the camera and read frames in a loop. Each successfully read frame is emitted via the `frame_ready` signal.

A key feature is the static method `list_available_cameras`, which attempts to get user-friendly camera names using platform-specific libraries, falling back to generic names if necessary. The service also implements a slot `on_visibility_changed` which, when triggered by the main window hiding, increases the sleep duration in the capture loop. This effectively lowers the frame rate (FPS) to conserve CPU resources when the video feed is not being displayed.

## Evolution
### v1: Initial design
*   Robust camera handling with background threading and dynamic FPS adjustment.
