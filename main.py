import sys, os
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QMainWindow
from PySide6 import QtCore
                                                     
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        label = QLabel("Hello World", alignment=Qt.Alignment.AlignCenter)
        button = QPushButton(self.tr("Rock and Roll"), self)
        button.setShortcut(self.tr("Alt+F4"))
        label.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    translator = QtCore.QTranslator(app)
    translator.load('i18n/tr_de', os.path.dirname(__file__))
    app.installTranslator(translator)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())