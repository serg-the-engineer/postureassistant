from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QSizePolicy,
)
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# Add this class to src/statistics_window.py
class MplCanvas(FigureCanvas):
    """A custom Matplotlib canvas widget to embed in PyQt."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.figure.add_subplot(111)
        super().__init__(self.figure)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.updateGeometry()


class StatisticsWindow(QDialog):
    def __init__(self, stats_service, parent=None):
        super().__init__(parent)
        self.stats_service = stats_service
        self.setWindowTitle("Today's Statistics")
        self.setMinimumSize(500, 400)

        layout = QVBoxLayout(self)
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        layout.addWidget(self.canvas)

        self.summary_label = QLabel("Loading...")
        layout.addWidget(self.summary_label)

        self.update_stats()

        self.setLayout(layout)

    def update_stats(self):
        summary = self.stats_service.get_summary_for_today()
        correct_s = summary.get("CORRECT", 0)
        incorrect_s = summary.get("INCORRECT", 0)

        labels = []
        sizes = []
        colors = []

        if correct_s > 0:
            labels.append("Correct")
            sizes.append(correct_s)
            colors.append("green")
        if incorrect_s > 0:
            labels.append("Incorrect")
            sizes.append(incorrect_s)
            colors.append("red")

        self.canvas.axes.clear()
        if not sizes:
            self.canvas.axes.text(
                0.5, 0.5, "No data for today yet.", ha="center", va="center"
            )
            self.summary_label.setText("Track your posture to see statistics here.")
        else:
            self.canvas.axes.pie(
                sizes, labels=labels, autopct="%1.1f%%", startangle=90, colors=colors
            )
            self.canvas.axes.axis(
                "equal"
            )  # Equal aspect ratio ensures that pie is drawn as a circle.

            correct_m = correct_s / 60
            incorrect_m = incorrect_s / 60
            self.summary_label.setText(
                f"Time with Correct Posture: {correct_m:.1f} minutes\n"
                f"Time with Incorrect Posture: {incorrect_m:.1f} minutes"
            )

        self.canvas.draw()
