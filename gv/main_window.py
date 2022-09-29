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
        # Allow action shortcuts even when toolbar and menu bar are hidden
        self.addAction(self.actionFull_Screen)
        self.addAction(self.actionNormal_View)
        #
        self.layers = self.openGLWidget.layers
        ll = self.layers_listWidget
        for layer in self.layers:
            item = QtWidgets.QListWidgetItem(ll)
            ll.addItem(item)
            row = LayerWidget(layer)
            item.setSizeHint(row.minimumSizeHint())
            ll.setItemWidget(item, row)

    @QtCore.Slot(bool)
    def on_actionFull_Screen_toggled(self, is_checked: bool):
        if is_checked:
            self.menubar.hide()
            # self.toolBar.hide()
            self.rightArea_widget.hide()
            self.leftArea_widget.hide()
            self.statusbar.hide()
            self.showFullScreen()
        else:
            self.menubar.show()
            # self.toolBar.show()
            self.rightArea_widget.show()
            self.leftArea_widget.show()
            self.statusbar.show()
            self.showNormal()

    @QtCore.Slot()
    def on_actionNormal_View_triggered(self):
        self.actionFull_Screen.setChecked(False)

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
