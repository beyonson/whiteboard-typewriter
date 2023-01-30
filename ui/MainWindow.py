from PyQt5 import QtCore, QtGui, QtWidgets, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

# Style sheet
styleSheet = """
QWidget {
    background-color: #747c8a;
}
QPushButton {
    background-color: #e8c33c;
}
QTableWidget {
    background-color: #747c8a;
}
QListWidget {
    background-color: #747c8a;
}
QTabWidget {
    background-color: #858e9e;
}
QTabBar {
    background-color: #7b8fb0;
}
QComboBox {
    background-color: #7b8fb0;
}
QDoubleSpinBox {
    background-color: #7b8fb0;
}
QCheckBox {
    background-color: #858e9e; border : 2px solid #7b8fb0;
}
QLCDNumber {
    border : 2px solid #7b8fb0;
}
"""

class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setupUi()

    def setupUi(self):
        self.setObjectName("self")
        self.setGeometry(50, 50, 500, 200)
        self.setMouseTracking(True)
        self.show()

        self.fontSizeSelection = QtWidgets.QSpinBox(self)
        self.fontSizeSelection.setGeometry(QtCore.QRect(20,60,110,30))
        self.fontSizeSelection.setRange(14,28)
        self.fontSizeSelection.show()

        self.fontSelection = QComboBox(self)
        self.fontSelection.setGeometry(QtCore.QRect(20,30,110,30))
        self.fontSelection.addItem("Monospace")
        self.fontSelection.addItem("Papyrus")
        self.fontSelection.show()

        self.changeFont = QPushButton(self)
        self.changeFont.setGeometry(QtCore.QRect(20,140,110,30))
        self.changeFont.setText("Set font")
        self.changeFont.clicked.connect(self.fontChanged)
        self.changeFont.show()

        self.editor = QPlainTextEdit(self)
        self.editor.setGeometry(QtCore.QRect(150,30,320,140))

        fixedfont = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        fixedfont.setPointSize(14)
        self.editor.setFont(fixedfont)
        self.editor.show()

    def fontChanged(self):
        self.editor.clear()
        fontSize = self.fontSizeSelection.value()
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        font.setPointSize(int(fontSize))
        self.editor.setFont(font)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setStyleSheet(styleSheet)
    mainUi = MainWindow()

    sys.exit(app.exec_())