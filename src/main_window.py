import numpy as np
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt, QThread

from .camera_service import CameraService
from .processing_service import ProcessingService, PostureStatus
from .settings_service import SettingsService

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vibestand - Posture Assistant")
        self.setGeometry(100, 100, 800, 600)

        # --- Services ---
        self.settings_service = SettingsService()
        self.camera_service = CameraService(camera_id=self.settings_service.get("camera_id", 0))
        self.processing_service = ProcessingService(self.settings_service)
        
        # --- Threading ---
        self.processing_thread = QThread()
        self.processing_service.moveToThread(self.processing_thread)
        self.processing_thread.start()

        # --- UI Elements ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.video_label = QLabel("Camera feed will appear here.")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("background-color: black; color: white;")
        self.layout.addWidget(self.video_label)

        controls_layout = QHBoxLayout()
        self.start_stop_button = QPushButton("Start")
        self.calibrate_button = QPushButton("Calibrate")
        self.calibrate_button.setEnabled(False)
        self.status_label = QLabel("Status: Not Running")
        font = self.status_label.font(); font.setPointSize(14); self.status_label.setFont(font)

        controls_layout.addWidget(self.start_stop_button)
        controls_layout.addWidget(self.calibrate_button)
        controls_layout.addStretch()
        controls_layout.addWidget(self.status_label)
        self.layout.addLayout(controls_layout)

        # --- Connections ---
        self.start_stop_button.clicked.connect(self.toggle_monitoring)
        self.calibrate_button.clicked.connect(self.processing_service.start_calibration)
        
        self.camera_service.frame_ready.connect(self.processing_service.process_frame)
        self.processing_service.processed_frame_ready.connect(self.update_video_feed)
        self.processing_service.status_updated.connect(self.update_status)

    def toggle_monitoring(self):
        if self.camera_service.isRunning():
            self.processing_service.set_active(False)
            self.camera_service.stop()
            self.start_stop_button.setText("Start")
            self.calibrate_button.setEnabled(False)
            self.update_status(PostureStatus.NOT_DETECTED)
        else:
            self.camera_service.start()
            self.processing_service.set_active(True)
            self.start_stop_button.setText("Stop")
            self.calibrate_button.setEnabled(True)

    def update_video_feed(self, frame: np.ndarray):
        h, w, ch = frame.shape
        qt_image = QImage(frame.data, w, h, ch * w, QImage.Format.Format_BGR888)
        pixmap = QPixmap.fromImage(qt_image)
        self.video_label.setPixmap(pixmap.scaled(
            self.video_label.size(), Qt.AspectRatioMode.KeepAspectRatio
        ))

    def update_status(self, status: PostureStatus):
        if not self.camera_service.isRunning():
            self.status_label.setText("Status: Not Running"); self.status_label.setStyleSheet("color: gray;")
            return

        if status == PostureStatus.CORRECT:
            self.status_label.setText("Status: Correct"); self.status_label.setStyleSheet("color: green;")
        elif status == PostureStatus.INCORRECT:
            self.status_label.setText("Status: Incorrect"); self.status_label.setStyleSheet("color: red;")
        elif status == PostureStatus.NOT_DETECTED:
            if self.settings_service.get_calibration_data().get('reference_y') is None:
                self.status_label.setText("Status: Needs Calibration"); self.status_label.setStyleSheet("color: orange;")
            else:
                self.status_label.setText("Status: Face Not Detected"); self.status_label.setStyleSheet("color: orange;")

    def closeEvent(self, event):
        self.camera_service.stop()
        self.processing_thread.quit()
        self.processing_thread.wait()
        super().closeEvent(event)
