import cv2
import numpy as np
import os
import sys
from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot


class CameraService(QThread):
    frame_ready = pyqtSignal(np.ndarray)

    def __init__(self, camera_id=0, parent=None):
        super().__init__(parent)
        self.camera_id = camera_id
        self.cap = None
        self._is_running = False
        self._is_ui_visible = True  # Assume UI is visible on start

    def run(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            self.cap.open(self.camera_id)

        self._is_running = True
        while self._is_running:
            ret, frame = self.cap.read()
            if ret:
                self.frame_ready.emit(cv2.flip(frame, 1))

            sleep_duration = 20 if self._is_ui_visible else 1000
            self.msleep(sleep_duration)  # Dynamic FPS

        if self.cap:
            self.cap.release()
            self.cap = None

    def stop(self):
        self._is_running = False
        self.wait()

    @pyqtSlot(bool)
    def on_visibility_changed(self, is_visible: bool):
        """Slot to update FPS based on UI visibility."""
        self._is_ui_visible = is_visible

    @staticmethod
    def list_available_cameras(limit=10) -> list[dict]:
        """
        Checks for available cameras up to a given limit.
        Returns a list of dicts, each with 'id' and 'name'.
        Tries to use platform-specific libraries for friendly names first.
        If that fails or returns no cameras, it falls back to a generic
        method that is more reliable for indexing but has generic names.
        This prevents duplicate entries and provides a working fallback.
        """
        # --- Attempt platform-specific methods first ---
        try:
            platform_specific_cameras = []
            if sys.platform == "win32":
                from pygrabber.dshow_graph import DSShowEvent

                devices = DSShowEvent().get_input_devices()
                for i, name in enumerate(devices):
                    platform_specific_cameras.append({"id": i, "name": name})

            elif sys.platform == "darwin":
                from AVFoundation import AVCaptureDevice, AVMediaTypeVideo

                devices = AVCaptureDevice.devicesWithMediaType_(AVMediaTypeVideo)
                for i, device in enumerate(devices):
                    platform_specific_cameras.append(
                        {"id": i, "name": device.localizedName()}
                    )

            elif sys.platform.startswith("linux"):
                # This method is generally reliable on Linux but may list non-camera devices.
                video_devices = [
                    dev
                    for dev in os.listdir("/sys/class/video4linux")
                    if dev.startswith("video")
                ]
                for dev_name in sorted(video_devices):
                    index = int(dev_name.replace("video", ""))
                    platform_specific_cameras.append(
                        {"id": index, "name": f"Camera {index}"}
                    )

            # If the platform-specific method found any cameras, return them.
            if platform_specific_cameras:
                return platform_specific_cameras

        except Exception as e:
            print(f"INFO: Platform-specific camera detection failed ({e}).")

        # --- Fallback method ---
        # This part is reached ONLY if the platform-specific methods failed or found no cameras.
        print("INFO: Falling back to generic camera detection method.")
        fallback_cameras = []
        for i in range(limit):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                fallback_cameras.append({"id": i, "name": f"Camera {i}"})
                cap.release()
            else:
                # Assume camera indices are contiguous. Stop after the first failure.
                # This prevents spamming stderr with "out of bound" errors.
                break
        return fallback_cameras
