from PySide6 import QtCore, QtGui, QtWidgets

from ui_globeview import Ui_MainWindow


class GlobeViewMainWindow(Ui_MainWindow, QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.openGLWidget.statusMessageRequested.connect(self.statusbar.showMessage)
        self.actionQuit.setShortcut(QtGui.QKeySequence.Quit)  # no effect on Windows

    @QtCore.Slot()
    def on_actionQuit_triggered(self):
        QtCore.QCoreApplication.quit()

    @QtCore.Slot(int)
    def on_azimuthSlider_valueChanged(self, azimuth_degrees):
        self.openGLWidget.set_azimuth(azimuth_degrees)

    @QtCore.Slot(int)
    def on_projectionComboBox_currentIndexChanged(self, projection: int):
        print(f"projection changed to {projection}")
