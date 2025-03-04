from PySide6.QtCore import Qt, QMimeData, Signal
from PySide6.QtGui import QPixmap, QDrag
from PySide6.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QMainWindow

class DragItem(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setContentsMargins(25, 5, 25, 5)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("border: 1px solid black;")
        # Store data separately from display label, but use label for default.
        self.data = self.text()

    def set_data(self, data):
        self.data = data

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)

            pixmap = QPixmap(self.size())
            self.render(pixmap)
            drag.setPixmap(pixmap)

            drag.exec(Qt.DropAction.MoveAction)


class DragWidget(QWidget):
    """
    Handles sorting and drag-and-drop of items inside it.
    """

    orderChanged = Signal(list)

    def __init__(self, *args, orientation=Qt.Orientation.Vertical, **kwargs):
        super().__init__()
        self.setAcceptDrops(True)

        # Store the orientation for drag checks later.
        self.orientation = orientation

        if self.orientation == Qt.Orientation.Vertical:
            self.blayout = QVBoxLayout()
        else:
            self.blayout = QHBoxLayout()

        self.setLayout(self.blayout)

    def dragEnterEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        pos = e.position()
        widget = e.source()
        self.blayout.removeWidget(widget)

        for n in range(self.blayout.count()):
            # Get the widget at each index in turn.
            w = self.blayout.itemAt(n).widget()
            if self.orientation == Qt.Orientation.Vertical:
                # Drag drop vertically.
                drop_here = pos.y() < w.y() + w.size().height() // 2
            else:
                # Drag drop horizontally.
                drop_here = pos.x() < w.x() + w.size().width() // 2

            if drop_here:
                break

        else:
            # We aren't on the left hand/upper side of any widget,
            # so we're at the end. Increment 1 to insert after.
            n += 1

        self.blayout.insertWidget(n, widget)
        self.orderChanged.emit(self.get_item_data())

        e.accept()

    def add_item(self, item):
        self.blayout.addWidget(item)

    def get_item_data(self):
        data = []
        for n in range(self.blayout.count()):
            # Get the widget at each index in turn.
            w = self.blayout.itemAt(n).widget()
            data.append(w.data)
        return data


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create the main layout for the window
        self.main_layout = QVBoxLayout()

        # Create the outer drag widget for the grid
        self.grid_layout = DragWidget(orientation=Qt.Orientation.Vertical)

        # Create the 4 rows
        for i in range(4):  # 4 rows (A, B, C, D)
            row_layout = DragWidget(orientation=Qt.Orientation.Horizontal)  # For each row, use a horizontal layout
            for j in range(3):  # 3 columns
                label = f"{chr(65+i)}{j+1}"  # Generate labels like A1, A2, A3, ...
                item = DragItem(label)
                item.set_data((chr(65+i), j+1))  # Store the row and column info
                row_layout.add_item(item)

            self.grid_layout.add_item(row_layout)  # Add the row to the grid

        container = QWidget()
        container.setLayout(self.grid_layout.blayout)  # Set the grid layout as the container layout

        self.setCentralWidget(container)


app = QApplication([])
w = Window()
w.show()

app.exec()
