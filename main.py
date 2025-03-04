from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QPixmap, QDrag
from PySide6.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget, QLabel
#from excel import read_excel_file, getWeekSchedule

class TableCell(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setContentsMargins(25, 5, 25, 5)
        self.setFixedHeight(25)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("border: 1px solid black;")
        # Store data separately from display label, but use label for default.
        self.data = self.text()

    def set_data(self, data):
        self.data = data

class Division(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.setContentsMargins(25, 5, 25, 5)
        self.setFixedHeight(25)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("border: 1px solid black;")

class ClassesTableCell(TableCell):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        height_size = [0, 25, 28*2, 29*3, 29.6*4, 29.8*5, 28*6, 28*7, 28*8, 28*9, 28*10, 28*11, 28*12, 28*13, 28*14, 28*15, 30.6*16]
        cell_info = self.text().split("_")
        self.setFixedHeight(height_size[int(cell_info[1])])
        self.setText(cell_info[0])

    def set_data(self, data):
        self.data = data

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)
            drag.exec(Qt.DropAction.MoveAction)
        

class Image(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.setFixedSize(100, 100)
        pixmap = QPixmap("data/UdeA.png")
        pixmap.scaledToHeight(100)
        pixmap.scaledToWidth(100)
        self.setPixmap(pixmap)

class Window(QWidget):
    def __init__(self):

        super().__init__()
        self.setAcceptDrops(True)

        hours = [str(i) for i in range(6, 22)]
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        classes = [
            ["Lab1_3", "Class1_2", "TEST_2", "Class2_2", "Class3_4", "Lab2_3"],
            ["Class1_2", "_1", "Lab1_3", "_1", "Lab2_3", "Class3_4", "Class2_2"],
            ["Lab1_3", "Class1_2", "_1", "_1", "Class2_2", "Class3_4", "Lab2_3"],
            ["Class1_2", "_1", "Lab1_3", "_1", "Lab2_3", "Class3_4", "Class2_2"],
            ["Lab1_3", "Class1_2", "_1", "_1", "Class2_2", "Class3_4", "Lab2_3"],
            ["Class1_2", "_1", "Lab1_3", "_1", "Lab2_3", "Class3_4", "Class2_2"],
            ]

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
        self.hours_layout.addWidget(Division())
        for hour in hours:
            h_cell = TableCell(hour+":00")
            self.hours_layout.addWidget(h_cell)

        # Create a vertical layout for each day and add to the days layout
        daily_layout = QVBoxLayout()
        daily_widget = QWidget()
        daily_widget.setLayout(daily_layout)
        self.days_layout.addWidget(hours_widget)

        cl_idx = 0
        for day in days:
            daily_layout = QVBoxLayout()
            d_cell = TableCell(day)
            daily_layout.addWidget(d_cell)

            # Add empty cells for each hour
            for c in classes[cl_idx]:
                s_cell = ClassesTableCell(c)  # Blank space for each hour
                
                daily_layout.addWidget(s_cell)

            # Create a widget for the daily layout and add it to the days layout
            daily_widget = QWidget()
            daily_widget.setLayout(daily_layout)
            self.days_layout.addWidget(daily_widget)
            cl_idx += 1

        # Create a general layout and add both widgets
        self.general_table = QHBoxLayout()
        # self.general_table.addWidget(hours_widget)
        self.general_table.addWidget(days_widget)

        self.setLayout(self.general_table)

    def dragEnterEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        pos = e.position()
        widget_moved = e.source()
        #widget_target = e.sender()
        self.general_table.removeWidget(widget_moved)
        #self.general_table.removeWidget(widget_target)
        print(self.general_table.count())

        for n in range(self.daily_layout.count()):
            # Get the widget at each index in turn.
            w = self.daily_layout.itemAt(n).widget()
            if pos.x() < w.x() + w.size().width() // 2:
                # We didn't drag past this widget.
                # insert to the left of it.
                break
        else:
            # We aren't on the left hand side of any widget,
            # so we're at the end. Increment 1 to insert after.
            n += 1

        self.general_table.insertWidget(n, widget_moved)

        e.accept()


app = QApplication([])
w = Window()
w.show()

app.exec()