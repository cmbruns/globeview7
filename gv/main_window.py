from PySide6 import QtCore, QtGui, QtWidgets

from ui_globeview import Ui_MainWindow
from gv.projection import Projection
from gv.layer import LayerWidget


class GlobeViewMainWindow(Ui_MainWindow, QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.openGLWidget.statusMessageRequested.connect(self.statusbar.showMessage)
        self.actionQuit.setShortcut(QtGui.QKeySequence.Quit)  # no effect on Windows
        self.openGLWidget.actionReset_View = self.actionReset_View
        self.openGLWidget.azimuth_changed.connect(self.azimuthSpinBox.setValue)
        #
        self.layers = self.openGLWidget.layers
        ll = self.layers_listWidget
        for layer in self.layers:
            item = QtWidgets.QListWidgetItem(ll)
            ll.addItem(item)
            row = LayerWidget(layer)
            item.setSizeHint(row.minimumSizeHint())
            ll.setItemWidget(item, row)

    @QtCore.Slot()
    def on_actionReset_View_triggered(self):
        self.openGLWidget.reset_view()

    @QtCore.Slot()
    def on_actionQuit_triggered(self):
        QtCore.QCoreApplication.quit()

    @QtCore.Slot(float)
    def on_azimuthSpinBox_valueChanged(self, azimuth_degrees):
        self.openGLWidget.set_azimuth(azimuth_degrees)

    @QtCore.Slot()
    def on_northDownButton_clicked(self):
        self.azimuthSpinBox.setValue(180)

    @QtCore.Slot()
    def on_northLeftButton_clicked(self):
        self.azimuthSpinBox.setValue(90)

    @QtCore.Slot()
    def on_northRightButton_clicked(self):
        self.azimuthSpinBox.setValue(270)

    @QtCore.Slot()
    def on_northUpButton_clicked(self):
        self.azimuthSpinBox.setValue(0)

    @QtCore.Slot(int)
    def on_projectionComboBox_currentIndexChanged(self, projection: int):
        self.openGLWidget.set_projection(Projection(projection))
