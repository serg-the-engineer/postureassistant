from PyQt6.QtCore import QObject, QTimer, QUrl
from PyQt6.QtWidgets import QSystemTrayIcon
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from .processing_service import PostureStatus
from .utils import resource_path


class NotificationService(QObject):
    def __init__(self, tray_icon: QSystemTrayIcon, settings_service, parent=None):
        super().__init__(parent)
        self.tray_icon = tray_icon
        self.settings = settings_service
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.show_notification)
        self.notification_timer_remaining_ms = -1  # For pausing the timer
        self.current_status = PostureStatus.NOT_DETECTED
        self.media_player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.media_player.setAudioOutput(self.audio_output)
        sound_file = self.settings.get(
            "notification_sound_file", resource_path("assets/wilhelm.ogg")
        )
        self.media_player.setSource(QUrl.fromLocalFile(sound_file))

    def handle_status_update(self, status: PostureStatus):
        self.current_status = status
        if status == PostureStatus.INCORRECT:
            # If timer isn't running, start or resume it.
            if not self.timer.isActive():
                # If we have a remaining time, it means we're resuming from a pause.
                if self.notification_timer_remaining_ms > 0:
                    self.timer.start(self.notification_timer_remaining_ms)
                else:
                    # Otherwise, start a fresh timer.
                    delay_ms = (
                        self.settings.get("notification_delay_seconds", 10) * 1000
                    )
                    self.timer.start(delay_ms)
                self.notification_timer_remaining_ms = -1  # Reset after use
        elif status == PostureStatus.NOT_DETECTED:
            # If face is lost while timer is counting down, pause it.
            if self.timer.isActive():
                self.notification_timer_remaining_ms = self.timer.remainingTime()
                self.timer.stop()
        elif status == PostureStatus.CORRECT:
            # Correct posture resets the timer.
            self.timer.stop()
            self.notification_timer_remaining_ms = -1

    def show_notification(self):
        if self.current_status == PostureStatus.INCORRECT and self.settings.get(
            "notifications_enabled", True
        ):
            self.tray_icon.showMessage(
                "Check Your Posture!",
                "You have been sitting incorrectly for a while. Please sit up straight.",
                QSystemTrayIcon.MessageIcon.Information,
                3000,  # msecs
            )
            if self.media_player.source().isValid():
                # Stop and play to ensure the sound restarts from the beginning.
                self.media_player.stop()
                self.media_player.play()
