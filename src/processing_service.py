import cv2
import numpy as np
from enum import Enum, auto
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QMutex, pyqtSlot
from .utils import resource_path


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
        self._is_visible = True  # Assume visible at start
        self._is_calibrating = False

        cascade_path = resource_path("assets/haarcascade_frontalface_default.xml")
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        if self.face_cascade.empty():
            raise IOError("Could not load haarcascade_frontalface_default.xml")

        self._last_frame = None
        self._frame_lock = QMutex()

        self.analysis_timer = QTimer(self)
        self.analysis_timer.timeout.connect(self._analyze_frame)

    def _update_timer_state(self):
        interval = 250 if self._is_visible else 1500
        self.analysis_timer.start(interval)

    @pyqtSlot(bool)
    def on_visibility_changed(self, is_visible: bool):
        """Stops/starts analysis timer based on window visibility."""
        self._is_visible = is_visible
        self._update_timer_state()

    def start_calibration(self):
        self._is_calibrating = True

    @pyqtSlot(np.ndarray)
    def update_latest_frame(self, frame: np.ndarray):
        """Receives a new frame from the camera and stores it for analysis."""
        self._frame_lock.lock()
        try:
            self._last_frame = frame.copy()
        finally:
            self._frame_lock.unlock()

    def _analyze_frame(self):
        """Periodically called by a timer to analyze the last received frame."""
        self._frame_lock.lock()
        if self._last_frame is None:
            self._frame_lock.unlock()
            return
        # Make a local copy to work with and release the lock
        frame = self._last_frame.copy()
        self._frame_lock.unlock()

        output_frame = frame.copy()

        # Resize image for faster analysis
        h, w, _ = frame.shape
        analysis_width = 320
        scale = w / analysis_width
        analysis_height = int(h / scale)

        resized_frame = cv2.resize(
            frame, (analysis_width, analysis_height), interpolation=cv2.INTER_AREA
        )
        gray = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)

        faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)

        status = PostureStatus.NOT_DETECTED
        if len(faces) > 0:
            # Get largest face from resized detection
            x, y, w_face, h_face = sorted(
                faces, key=lambda f: f[2] * f[3], reverse=True
            )[0]

            # Scale coordinates back to original frame size for calibration and drawing
            orig_x = int(x * scale)
            orig_y = int(y * scale)
            orig_w = int(w_face * scale)
            orig_h = int(h_face * scale)

            if self._is_calibrating:
                ref_y_int = int(orig_y)
                current_tolerance = self.settings.get_calibration_data().get(
                    "tolerance_pixels", 50
                )
                self.settings.set_calibration_data(ref_y_int, current_tolerance)
                self._is_calibrating = False

            calibration_data = self.settings.get_calibration_data()
            ref_y = calibration_data.get("reference_y")
            if ref_y is not None:
                tolerance = calibration_data.get("tolerance_pixels", 50)
                status = (
                    PostureStatus.CORRECT
                    if abs(orig_y - ref_y) <= tolerance
                    else PostureStatus.INCORRECT
                )

            color = (0, 255, 0) if status == PostureStatus.CORRECT else (0, 0, 255)
            cv2.rectangle(
                output_frame,
                (orig_x, orig_y),
                (orig_x + orig_w, orig_y + orig_h),
                color,
                2,
            )

        self.status_updated.emit(status)
        if self._is_visible:
            self._draw_overlays(output_frame)
            self.processed_frame_ready.emit(output_frame)

    def _draw_overlays(self, frame: np.ndarray):
        calibration_data = self.settings.get_calibration_data()
        ref_y = calibration_data.get("reference_y")
        if ref_y is not None:
            tolerance = calibration_data.get("tolerance_pixels", 50)
            w = frame.shape[1]
            cv2.line(
                frame, (0, ref_y - tolerance), (w, ref_y - tolerance), (0, 255, 0), 2
            )
            cv2.line(
                frame, (0, ref_y + tolerance), (w, ref_y + tolerance), (0, 255, 0), 2
            )
            cv2.line(frame, (0, ref_y), (w, ref_y), (0, 255, 255), 2)
