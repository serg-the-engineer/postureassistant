import cv2
import numpy as np
import sys
from PyQt6.QtCore import QThread, pyqtSignal

class CameraService(QThread):
    frame_ready = pyqtSignal(np.ndarray)

    def __init__(self, camera_id=0, parent=None):
        super().__init__(parent)
        self.camera_id = camera_id
        self.cap = None
        self._is_running = False

    def run(self):
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            print(f"Error: Could not open camera {self.camera_id}")
            return

        self._is_running = True
        while self._is_running:
            if not self._is_running:
                if self.cap:
                    self.cap.release()
                    self.cap = None
                break
            ret, frame = self.cap.read()
            if ret:
                self.frame_ready.emit(cv2.flip(frame, 1))
            self.msleep(100)  # Limit to ~10 FPS

    def stop(self):
        self._is_running = False
        self.wait()

    @staticmethod
    def list_available_cameras(limit=10) -> list[dict]:
        """
        Checks for available cameras up to a given limit.
        Returns a list of dicts, each with 'id' and 'name'.
        Uses pygrabber on Windows for friendly names, otherwise uses index.
        """
        available_cameras = []

        if sys.platform == "win32":
            try:
                from pygrabber.dshow_graph import DSShowEvent
                devices = DSShowEvent()
                video_devices = devices.get_input_devices()
                for i, name in enumerate(video_devices):
                    available_cameras.append({'id': i, 'name': name})
                if available_cameras:
                    return available_cameras
            except (ImportError, Exception) as e:
                print(f"INFO: Could not use pygrabber ({e}), falling back to index-based camera names.")

        # Fallback for non-Windows or if pygrabber fails
        for i in range(limit):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available_cameras.append({'id': i, 'name': f"Camera {i}"})
                cap.release()
        return available_cameras
