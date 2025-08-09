from PyQt6.QtCore import QObject, QTimer
from PyQt6.QtWidgets import QSystemTrayIcon
from .processing_service import PostureStatus

class NotificationService(QObject):
    def __init__(self, tray_icon: QSystemTrayIcon, settings_service, parent=None):
        super().__init__(parent)
        self.tray_icon = tray_icon
        self.settings = settings_service
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.show_notification)
        self.current_status = PostureStatus.NOT_DETECTED

    def handle_status_update(self, status: PostureStatus):
        self.current_status = status
        if status == PostureStatus.INCORRECT:
            if not self.timer.isActive():
                delay_ms = self.settings.get("notification_delay_seconds", 10) * 1000
                self.timer.start(delay_ms)
        else:
            if self.timer.isActive():
                self.timer.stop()

    def show_notification(self):
        if self.current_status == PostureStatus.INCORRECT and self.settings.get("notifications_enabled", True):
            self.tray_icon.showMessage(
                "Check Your Posture!",
                "You have been sitting incorrectly for a while. Please sit up straight.",
                QSystemTrayIcon.MessageIcon.Warning,
                3000  # msecs
            )
