from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, QWidget,
                             QHBoxLayout, QSizePolicy)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from datetime import datetime, timedelta

class StatisticsWindow(QDialog):
    def __init__(self, stats_service, parent=None):
        super().__init__(parent)
        self.stats_service = stats_service
        self.setWindowTitle("Today's Posture Statistics")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout()
        
        # Add a figure canvas for the chart
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Add summary labels
        self.summary_label = QLabel("Loading...")
        layout.addWidget(self.summary_label)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.update_stats)
        layout.addWidget(refresh_button)

        self.update_stats()
        
        self.setLayout(layout)
        self.update_chart()
    
    def update_stats(self):
        summary = self.stats_service.get_summary_for_today()
        correct_s = summary.get('CORRECT', 0.0)
        incorrect_s = summary.get('INCORRECT', 0.0)
        total = correct_s + incorrect_s
        
        if total > 0:
            # Calculate percentages
            correct_pct = (correct_s / total) * 100
            incorrect_pct = 100 - correct_pct
            
            # Update summary label
            self.summary_label.setText(
                f"Today's Posture Summary:\n"
                f"• Correct Posture: {correct_s/60:.1f} minutes ({correct_pct:.1f}%)\n"
                f"• Incorrect Posture: {incorrect_s/60:.1f} minutes ({incorrect_pct:.1f}%)"
            )
        else:
            # No data available
            self.summary_label.setText("No posture data available for today.")
    
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
