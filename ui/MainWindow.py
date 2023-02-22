import os
import subprocess

from time import sleep
from PyQt5 import QtCore, QtGui, QtWidgets, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from TextGrabber import *
from PyQt5.QtCore import QLibraryInfo

# Deal with redundant libraries
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = QLibraryInfo.location(
    QLibraryInfo.PluginsPath
)

# Clear image directories
subprocess.run("./CleanDirectories.sh")

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
        self.location       = [50, 50]
        self.charsTyped     = 0
        self.charsCaptured  = 0
        self.newChar        = False

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
        self.editor.textChanged.connect(self.charTyped)

        font = QFont()
        font.setFamily('monospace')
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(14)
        self.editor.setFont(font)
        self.editor.show()

        self.timer = QTimer()
        self.timer.timeout.connect(self.checkForUpdate)
        self.timer.start(100)

    def fontChanged(self):
        self.editor.clear()
        fontSize = self.fontSizeSelection.value()
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        font.setPointSize(int(fontSize))
        self.editor.setFont(font)

    def charTyped(self):
        self.charsTyped += 1

    def checkForUpdate(self):
        if self.charsTyped > self.charsCaptured :
            scrotChar(self.pos().x() + 155, self.pos().y() + 30, 14, self.charsCaptured)
            self.charsCaptured += 1

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setStyleSheet(styleSheet)
    mainUi = MainWindow()

    sys.exit(app.exec_())