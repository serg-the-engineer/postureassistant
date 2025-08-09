from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QSpinBox,
    QCheckBox,
    QDialogButtonBox,
    QGroupBox,
)
from PyQt6.QtCore import Qt


class SettingsWindow(QDialog):
    """A dialog window for configuring application settings."""

    def __init__(self, settings_service, parent=None):
        super().__init__(parent)
        self.settings_service = settings_service
        self.setWindowTitle("Settings")
        self.setMinimumWidth(400)

        # Main layout
        layout = QVBoxLayout(self)

        # --- Processing Settings ---
        processing_group = QGroupBox("Processing")
        processing_layout = QFormLayout()
        processing_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.tolerance_spinbox = QSpinBox()
        self.tolerance_spinbox.setRange(10, 200)
        self.tolerance_spinbox.setSuffix(" pixels")
        processing_layout.addRow("Posture Tolerance:", self.tolerance_spinbox)

        processing_group.setLayout(processing_layout)
        layout.addWidget(processing_group)

        # --- Notifications Settings ---
        notifications_group = QGroupBox("Notifications")
        notifications_layout = QFormLayout()
        notifications_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.notifications_enabled_checkbox = QCheckBox()
        notifications_layout.addRow("Enable Notifications:", self.notifications_enabled_checkbox)

        self.delay_spinbox = QSpinBox()
        self.delay_spinbox.setRange(10, 86400)  # 1 second to 24 hours
        self.delay_spinbox.setSingleStep(60)  # 1 minute steps
        self.delay_spinbox.setSuffix(" seconds")
        notifications_layout.addRow("Notification Delay:", self.delay_spinbox)

        # Add blinking threshold setting
        self.blinking_threshold_spinbox = QSpinBox()
        self.blinking_threshold_spinbox.setRange(10, 3600)  # 10 seconds to 1 hour
        self.blinking_threshold_spinbox.setSingleStep(10)  # 10 second steps
        self.blinking_threshold_spinbox.setSuffix(" seconds")
        notifications_layout.addRow("Tray Icon Blink Delay:", self.blinking_threshold_spinbox)

        notifications_group.setLayout(notifications_layout)
        layout.addWidget(notifications_group)

        # --- Buttons ---
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)
        self.load_settings()

    def load_settings(self):
        """Loads current settings and populates the UI controls."""
        calib_data = self.settings_service.get_calibration_data()
        self.tolerance_spinbox.setValue(calib_data.get("tolerance_pixels", 50))

        self.notifications_enabled_checkbox.setChecked(
            self.settings_service.get("notifications_enabled", True)
        )
        self.delay_spinbox.setValue(
            self.settings_service.get("notification_delay_seconds", 1800)
        )
        self.blinking_threshold_spinbox.setValue(
            self.settings_service.get("blinking_threshold_seconds", 300)
        )

    def accept(self):
        """Saves the settings and closes the dialog."""
        calib_data = self.settings_service.get_calibration_data()
        calib_data["tolerance_pixels"] = self.tolerance_spinbox.value()
        self.settings_service.set("calibration_data", calib_data)

        self.settings_service.set(
            "notifications_enabled", self.notifications_enabled_checkbox.isChecked()
        )
        self.settings_service.set(
            "notification_delay_seconds", self.delay_spinbox.value()
        )
        self.settings_service.set(
            "blinking_threshold_seconds", self.blinking_threshold_spinbox.value()
        )

        super().accept()
