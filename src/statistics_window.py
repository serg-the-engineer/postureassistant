from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, QWidget,
                             QHBoxLayout, QSizePolicy)
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from datetime import datetime, timedelta

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
        self.update_chart()
    
    def update_stats(self):
        summary = self.stats_service.get_summary_for_today()
        correct_s = summary.get('CORRECT', 0)
        incorrect_s = summary.get('INCORRECT', 0)

        labels = []
        sizes = []
        colors = []

        if correct_s > 0:
            labels.append('Correct')
            sizes.append(correct_s)
            colors.append('green')
        if incorrect_s > 0:
            labels.append('Incorrect')
            sizes.append(incorrect_s)
            colors.append('red')

        self.canvas.axes.clear()
        if not sizes:
            self.canvas.axes.text(0.5, 0.5, 'No data for today yet.', ha='center', va='center')
            self.summary_label.setText("Track your posture to see statistics here.")
        else:
            self.canvas.axes.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
            self.canvas.axes.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

            correct_m = correct_s / 60
            incorrect_m = incorrect_s / 60
            self.summary_label.setText(
                f"Time with Correct Posture: {correct_m:.1f} minutes\n"
                f"Time with Incorrect Posture: {incorrect_m:.1f} minutes"
            )
        
        self.canvas.draw()
    
    def update_chart(self):
        """Update the chart with the latest statistics."""
        # Clear the previous figure
        self.figure.clear()
        
        # Get today's summary
        summary = self.stats_service.get_summary_for_today()
        total = summary['CORRECT'] + summary['INCORRECT']
        
        if total > 0:
            # Calculate percentages
            correct_pct = (summary['CORRECT'] / total) * 100
            incorrect_pct = 100 - correct_pct
            
            # Create pie chart
            ax = self.figure.add_subplot(111)
            ax.pie(
                [summary['CORRECT'], summary['INCORRECT']],
                labels=['Correct Posture', 'Incorrect Posture'],
                autopct='%1.1f%%',
                startangle=90,
                colors=['#4CAF50', '#F44336']
            )
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        else:
            # No data available
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No data for today yet.', 
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes)
            ax.axis('off')
        
        self.canvas.draw()
