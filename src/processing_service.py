import cv2
import numpy as np
from enum import Enum, auto
from PyQt6.QtCore import QObject, pyqtSignal

class PostureStatus(Enum):
    CORRECT = auto()
    INCORRECT = auto()
    NOT_DETECTED = auto()

class ProcessingService(QObject):
    status_updated = pyqtSignal(PostureStatus)
    processed_frame_ready = pyqtSignal(np.ndarray)

    def __init__(self, settings_service, parent=None):
        super().__init__(parent)
        self.settings = settings_service
        self._is_active = False
        self.face_cascade = cv2.CascadeClassifier('assets/haarcascade_frontalface_default.xml')
        if self.face_cascade.empty():
            raise IOError("Could not load haarcascade_frontalface_default.xml")
        
        self.calibration_data = self.settings.get_calibration_data()
        self._is_calibrating = False

    def set_active(self, active: bool):
        self._is_active = active
        if not active:
            self.status_updated.emit(PostureStatus.NOT_DETECTED)

    def start_calibration(self):
        self._is_calibrating = True

    def process_frame(self, frame: np.ndarray):
        output_frame = frame.copy()
        if not self._is_active:
            self.processed_frame_ready.emit(output_frame)
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)

        status = PostureStatus.NOT_DETECTED
        if len(faces) > 0:
            x, y, w, h = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)[0]
            
            if self._is_calibrating:
                self.calibration_data['reference_y'] = y
                self.settings.set_calibration_data(y, self.calibration_data['tolerance_pixels'])
                self._is_calibrating = False

            ref_y = self.calibration_data.get('reference_y')
            if ref_y is not None:
                tolerance = self.calibration_data.get('tolerance_pixels', 50)
                status = PostureStatus.CORRECT if abs(y - ref_y) <= tolerance else PostureStatus.INCORRECT
            
            color = (0, 255, 0) if status == PostureStatus.CORRECT else (0, 0, 255)
            cv2.rectangle(output_frame, (x, y), (x+w, y+h), color, 2)

        self._draw_overlays(output_frame)
        self.status_updated.emit(status)
        self.processed_frame_ready.emit(output_frame)

    def _draw_overlays(self, frame: np.ndarray):
        ref_y = self.calibration_data.get('reference_y')
        if ref_y is not None:
            tolerance = self.calibration_data.get('tolerance_pixels', 50)
            w = frame.shape[1]
            cv2.line(frame, (0, ref_y - tolerance), (w, ref_y - tolerance), (0, 255, 0), 1)
            cv2.line(frame, (0, ref_y + tolerance), (w, ref_y + tolerance), (0, 255, 0), 1)
            cv2.line(frame, (0, ref_y), (w, ref_y), (0, 255, 255), 2)
