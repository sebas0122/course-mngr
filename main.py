from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QPushButton, QWidget, QLabel

class TableCell(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setContentsMargins(25, 5, 25, 5)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("border: 1px solid black;")
        # Store data separately from display label, but use label for default.
        self.data = self.text()

    def set_data(self, data):
        self.data = data

class Window(QWidget):
    def __init__(self):
        super().__init__()
        hours = [str(i) for i in range(6, 22)]
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

        self.hours_layout = QVBoxLayout()
        self.daily_layout = QVBoxLayout()
        self.days_layout = QHBoxLayout()

        # Create a widget for the hours layout
        hours_widget = QWidget()
        hours_widget.setLayout(self.hours_layout)

        # Create a widget for the days layout
        days_widget = QWidget()
        days_widget.setLayout(self.days_layout)

        # Populate hours layout
        for hour in hours:
            h_cell = TableCell(hour+":00")
            self.hours_layout.addWidget(h_cell)

        # Create a vertical layout for each day and add to the days layout
        for day in days:
            daily_layout = QVBoxLayout()
            d_cell = TableCell(day)
            daily_layout.addWidget(d_cell)

            # Add empty cells for each hour
            for _ in hours:
                s_cell = TableCell("")  # Blank space for each hour
                daily_layout.addWidget(s_cell)

            # Create a widget for the daily layout and add it to the days layout
            daily_widget = QWidget()
            daily_widget.setLayout(daily_layout)
            self.days_layout.addWidget(daily_widget)

        # Create a general layout and add both widgets
        self.general_table = QHBoxLayout()
        self.general_table.addWidget(hours_widget)
        self.general_table.addWidget(days_widget)

        self.setLayout(self.general_table)


app = QApplication([])
w = Window()
w.show()

app.exec()