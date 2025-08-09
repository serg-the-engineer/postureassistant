import numpy as np
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QComboBox,
    QSystemTrayIcon,
    QMenu,
    QApplication,
)
from PyQt6.QtGui import (
    QImage,
    QPixmap,
    QIcon,
    QAction,
    QPainter,
    QColor,
    QBrush,
    QShowEvent,
    QHideEvent,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from .camera_service import CameraService
from .processing_service import ProcessingService, PostureStatus
from .settings_service import SettingsService
from .notification_service import NotificationService
from .statistics_service import StatisticsService
from .statistics_window import StatisticsWindow
from .settings_window import SettingsWindow
from .utils import resource_path


class MainWindow(QMainWindow):
    visibility_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Posture Assistant")
        self.setGeometry(100, 100, 800, 600)

        # --- Services ---
        self.settings_service = SettingsService()
        self.statistics_service = StatisticsService()
        self.camera_service = CameraService(
            camera_id=self.settings_service.get("camera_id", 0)
        )
        self.processing_service = ProcessingService(self.settings_service)

        # --- System Tray and Notifications ---
        self.tray_icon = QSystemTrayIcon(
            QIcon(resource_path("assets/icon.png")), self
        )  # Assumes icon exists
        self.tray_icon.setToolTip("Posture Assistant")
        self.notification_service = NotificationService(
            self.tray_icon, self.settings_service
        )
        self.setup_tray_menu()
        self.tray_icon.show()

        # --- Threading ---
        self.processing_thread = QThread()
        self.processing_service.moveToThread(self.processing_thread)
        self.notification_service.moveToThread(
            self.processing_thread
        )  # Can run in the same thread
        self.processing_thread.start()

        # --- UI Elements ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Video display
        self.video_label = QLabel("Camera feed will appear here.")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("background-color: black; color: white;")
        self.layout.addWidget(self.video_label, 1)

        # Controls
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(15, 5, 15, 5)

        # Camera selection
        controls_layout.addWidget(QLabel("Camera:"))
        self.camera_combo = QComboBox()
        controls_layout.addWidget(self.camera_combo)
        controls_layout.addSpacing(20)

        # Buttons
        self.start_stop_button = QPushButton("Start")
        self.calibrate_button = QPushButton("Calibrate")
        self.calibrate_button.setEnabled(False)
        self.stats_button = QPushButton("Statistics")
        self.settings_button = QPushButton("Settings")

        # Status label
        self.status_label = QLabel("Status: Not Running")
        font = self.status_label.font()
        font.setPointSize(14)
        self.status_label.setFont(font)

        # Add widgets to controls layout
        controls_layout.addWidget(self.start_stop_button)
        controls_layout.addWidget(self.calibrate_button)
        controls_layout.addWidget(self.stats_button)
        controls_layout.addWidget(self.settings_button)
        controls_layout.addStretch()
        controls_layout.addWidget(self.status_label)

        # Add controls to main layout
        self.layout.addLayout(controls_layout)

        # Connect signals/slots
        self.start_stop_button.clicked.connect(self.toggle_monitoring)
        self.calibrate_button.clicked.connect(self.processing_service.start_calibration)
        self.stats_button.clicked.connect(self.show_statistics)
        self.settings_button.clicked.connect(self.show_settings)
        self.camera_combo.currentIndexChanged.connect(self.on_camera_changed)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        self.camera_service.frame_ready.connect(self.processing_service.process_frame)
        self.processing_service.processed_frame_ready.connect(self.update_video_feed)
        self.processing_service.status_updated.connect(self.update_status)
        self.processing_service.status_updated.connect(
            self.notification_service.handle_status_update
        )
        self.processing_service.status_updated.connect(
            self.statistics_service.handle_status_update
        )
        self.visibility_changed.connect(self.camera_service.on_visibility_changed)

        # Populate camera list after all connections are set up
        self.populate_camera_list()

    def populate_camera_list(self):
        self.camera_combo.blockSignals(True)
        self.camera_combo.clear()
        available_cameras = CameraService.list_available_cameras()
        if not available_cameras:
            self.camera_combo.addItem("No cameras found")
            self.camera_combo.setEnabled(False)
            self.start_stop_button.setEnabled(False)
            return

        saved_camera_id = self.settings_service.get("camera_id", 0)
        current_idx = 0
        for i, cam_info in enumerate(available_cameras):
            self.camera_combo.addItem(cam_info["name"], userData=cam_info["id"])
            if cam_info["id"] == saved_camera_id:
                current_idx = i

        self.camera_combo.setCurrentIndex(current_idx)
        self.on_camera_changed(current_idx)
        self.camera_combo.blockSignals(False)

    def on_camera_changed(self, index: int):
        if self.camera_service.isRunning():
            return
        cam_id = self.camera_combo.itemData(index)
        if cam_id is not None:
            self.camera_service.camera_id = cam_id
            self.settings_service.set("camera_id", cam_id)

    def toggle_monitoring(self):
        if self.camera_service.isRunning():
            self.processing_service.set_active(False)
            self.camera_service.stop()
            self.start_stop_button.setText("Start")
            self.calibrate_button.setEnabled(False)
            self.camera_combo.setEnabled(True)
            self.update_status(PostureStatus.NOT_DETECTED)
        else:
            self.camera_combo.setEnabled(False)
            self.camera_service.start()
            self.processing_service.set_active(True)
            self.start_stop_button.setText("Stop")
            self.calibrate_button.setEnabled(True)

    def update_video_feed(self, frame: np.ndarray):
        h, w, ch = frame.shape
        qt_image = QImage(frame.data, w, h, ch * w, QImage.Format.Format_BGR888)
        pixmap = QPixmap.fromImage(qt_image)
        self.video_label.setPixmap(
            pixmap.scaled(self.video_label.size(), Qt.AspectRatioMode.KeepAspectRatio)
        )

    def update_status(self, status: PostureStatus):
        # Update tray icon
        base_pixmap = QPixmap(resource_path("assets/icon.png"))
        if not base_pixmap.isNull():
            painter = QPainter(base_pixmap)
            dot_color = None

            if self.camera_service.isRunning():
                if status == PostureStatus.CORRECT:
                    dot_color = QColor("lightgreen")
                elif status == PostureStatus.INCORRECT:
                    dot_color = QColor("red")
                elif status == PostureStatus.NOT_DETECTED:
                    dot_color = QColor("yellow")

            if dot_color:
                radius = max(2, base_pixmap.width() // 8)
                margin = max(1, base_pixmap.width() // 8)
                x = base_pixmap.width() - (2 * radius) - margin
                y = base_pixmap.height() - (2 * radius) - margin

                painter.setBrush(QBrush(dot_color))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(x, y, 3 * radius, 3 * radius)

            painter.end()
            self.tray_icon.setIcon(QIcon(base_pixmap))

        # Update status label in main window
        if not self.camera_service.isRunning():
            self.status_label.setText("Status: Not Running")
            self.status_label.setStyleSheet("color: gray;")
            return

        if status == PostureStatus.CORRECT:
            self.status_label.setText("Status: Correct")
            self.status_label.setStyleSheet("color: green;")
        elif status == PostureStatus.INCORRECT:
            self.status_label.setText("Status: Incorrect")
            self.status_label.setStyleSheet("color: red;")
        elif status == PostureStatus.NOT_DETECTED:
            if self.settings_service.get_calibration_data().get("reference_y") is None:
                self.status_label.setText("Status: Needs Calibration")
                self.status_label.setStyleSheet("color: orange;")
            else:
                self.status_label.setText("Status: Face Not Detected")
                self.status_label.setStyleSheet("color: orange;")

    def setup_tray_menu(self):
        tray_menu = QMenu()
        show_action = QAction("Show/Hide", self)
        show_action.triggered.connect(self.toggle_visibility)
        tray_menu.addAction(show_action)

        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        tray_menu.addAction(settings_action)

        tray_menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)

    def show_settings(self):
        settings_dialog = SettingsWindow(self.settings_service, self)
        settings_dialog.exec()

    def show_statistics(self):
        # We create a new dialog each time to ensure stats are fresh
        stats_dialog = StatisticsWindow(self.statistics_service, self)
        stats_dialog.exec()

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:  # Left click
            self.toggle_visibility()

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.activateWindow()

    def showEvent(self, event: QShowEvent):
        """Override show event to notify services."""
        super().showEvent(event)
        self.visibility_changed.emit(True)

    def hideEvent(self, event: QHideEvent):
        """Override hide event to notify services."""
        super().hideEvent(event)
        self.visibility_changed.emit(False)

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        if self.tray_icon.isVisible():
            self.tray_icon.showMessage(
                "Still running",
                "Vibestand is running in the system tray.",
                QSystemTrayIcon.MessageIcon.Information,
                2000,
            )

    def quit_application(self):
        self.camera_service.stop()
        self.statistics_service.close()
        self.processing_thread.quit()
        self.processing_thread.wait()
        QApplication.instance().quit()
