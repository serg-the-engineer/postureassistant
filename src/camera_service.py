import cv2
import numpy as np
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
            ret, frame = self.cap.read()
            if ret:
                self.frame_ready.emit(cv2.flip(frame, 1))
            self.msleep(100)  # Limit to ~10 FPS

    def stop(self):
        self._is_running = False
        self.wait()
