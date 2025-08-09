import json
import os
from typing import Dict, Any

class SettingsService:
    def __init__(self, filename: str = "settings.json"):
        self.filepath = filename
        self.settings = self._load()

    def _load(self) -> Dict[str, Any]:
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return self._get_default_settings()

    def save(self):
        with open(self.filepath, 'w') as f:
            json.dump(self.settings, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)

    def set(self, key: str, value: Any):
        self.settings[key] = value
        self.save()

    def _get_default_settings(self) -> Dict[str, Any]:
        return {
            "version": 1,
            "camera_id": 0,
            "calibration_data": {"reference_y": None, "tolerance_pixels": 50},
            "notifications_enabled": True,
            "notification_delay_seconds": 10
        }

    def get_calibration_data(self) -> Dict[str, Any]:
        return self.get("calibration_data", self._get_default_settings()["calibration_data"])

    def set_calibration_data(self, ref_y: int, tolerance: int):
        self.set("calibration_data", {"reference_y": ref_y, "tolerance_pixels": tolerance})
