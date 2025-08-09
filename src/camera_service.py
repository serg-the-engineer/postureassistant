import cv2
import numpy as np
import os
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
        if self.cap is None:
            self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            self.cap.open(self.camera_id)

        self._is_running = True
        while self._is_running:
            ret, frame = self.cap.read()
            if ret:
                self.frame_ready.emit(cv2.flip(frame, 1))
            self.msleep(100)  # Limit to ~10 FPS

        if self.cap:
            self.cap.release()
            self.cap = None

    def stop(self):
        self._is_running = False
        self.wait()

    @staticmethod
    def list_available_cameras(limit=10) -> list[dict]:
        """
        Checks for available cameras up to a given limit.
        Returns a list of dicts, each with 'id' and 'name'.
        Uses platform-specific libraries for friendly names.
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

        elif sys.platform == "darwin": # macOS
            try:
                from AVFoundation import AVCaptureDevice, AVMediaTypeVideo
                devices = AVCaptureDevice.devicesWithMediaType_(AVMediaTypeVideo)
                for i, device in enumerate(devices):
                    available_cameras.append({'id': i, 'name': device.localizedName()})
                if available_cameras:
                    return available_cameras
            except (ImportError, Exception) as e:
                print(f"INFO: Could not use AVFoundation ({e}), falling back to index-based camera names.")

        elif sys.platform.startswith("linux"):
            try:
                video_devices = [dev for dev in os.listdir('/sys/class/video4linux') if dev.startswith('video')]
                for dev_name in sorted(video_devices):
                    dev_path = os.path.join('/sys/class/video4linux', dev_name)
                    with open(os.path.join(dev_path, 'name'), 'r') as f:
                        name = f.read().strip()
                    index = int(dev_name.replace('video', ''))
                    available_cameras.append({'id': index, 'name': f"{name} ({dev_name})"})
                if available_cameras:
                    return available_cameras
            except (IOError, FileNotFoundError, ValueError) as e:
                print(f"INFO: Could not read from /sys/class/video4linux ({e}), falling back to index-based camera names.")

        # Fallback if platform-specific methods fail or for other OS
        for i in range(limit):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available_cameras.append({'id': i, 'name': f"Camera {i}"})
                cap.release()
        return available_cameras
