import sqlite3
import time
from datetime import datetime, date
from .processing_service import PostureStatus

class StatisticsService:
    def __init__(self, db_path="statistics.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_table()
        self.current_status = PostureStatus.NOT_DETECTED
        self.last_status_change_time = time.time()

    def _create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posture_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_timestamp REAL NOT NULL,
                end_timestamp REAL NOT NULL,
                duration_seconds REAL NOT NULL,
                state TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def handle_status_update(self, new_status: PostureStatus):
        now = time.time()
        if new_status != self.current_status:
            duration = now - self.last_status_change_time
            # Log the previous state's duration, but only if it's meaningful
            if self.current_status in [PostureStatus.CORRECT, PostureStatus.INCORRECT]:
                self._log_entry(self.last_status_change_time, now, duration, self.current_status.name)
            
            # Reset for the new state
            self.current_status = new_status
            self.last_status_change_time = now

    def _log_entry(self, start, end, duration, state):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO posture_log (start_timestamp, end_timestamp, duration_seconds, state) VALUES (?, ?, ?, ?)",
            (start, end, duration, state)
        )
        self.conn.commit()

    def get_summary_for_today(self):
        today_start = datetime.combine(date.today(), datetime.min.time()).timestamp()
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT state, SUM(duration_seconds) FROM posture_log WHERE start_timestamp >= ? GROUP BY state",
            (today_start,)
        )
        summary = { 'CORRECT': 0, 'INCORRECT': 0 }
        for row in cursor.fetchall():
            state, total_duration = row
            if state in summary:
                summary[state] = total_duration if total_duration else 0
        return summary

    def close(self):
        # Log the final session before closing
        self.handle_status_update(PostureStatus.NOT_DETECTED)
        self.conn.close()
