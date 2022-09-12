from PySide6 import QtWidgets

from ui_globeview import Ui_MainWindow


class GlobeViewMainWindow(Ui_MainWindow, QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.openGLWidget.statusMessageRequested.connect(self.statusbar.showMessage)
        self.azimuthSlider.valueChanged.connect(self.openGLWidget.set_azimuth)
