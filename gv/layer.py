import abc
from PySide6 import QtCore, QtGui, QtWidgets


# https://stackoverflow.com/questions/54635205/how-do-i-use-generic-typing-with-pyqt-subclass-without-metaclass-conflicts
class QABCMeta(type(QtCore.QObject), abc.ABCMeta):
    pass


class ILayer(QtCore.QObject, metaclass=QABCMeta):
    def __init__(self, name: str):
        super().__init__()
        self._is_visible = True
        self._name = name
        self._display_name = self._name

    @property
    def display_name(self):
        return self._display_name

    @property
    def is_visible(self):
        return self._is_visible

    # noinspection PyCallingNonCallable
    @QtCore.Slot(bool)
    def set_visible(self, is_visible: bool) -> None:
        if self._is_visible == is_visible:
            return  # no change
        self._is_visible = is_visible
        self.visibility_changed.emit(self._is_visible)

    visibility_changed = QtCore.Signal(bool)


class ILayerGL(ILayer, abc.ABC):
    @abc.abstractmethod
    def paint_opengl(self, context):
        pass


class LayerListWidget(QtWidgets.QListWidget):
    def sizeHint(self):
        s = QtCore.QSize()
        s.setHeight(super().sizeHint().height())
        s.setWidth(self.sizeHintForColumn(0) + 2 * self.frameWidth())
        return s


class LayerWidget(QtWidgets.QWidget):
    def __init__(self, layer: ILayer, parent=None):
        super().__init__(parent=parent)
        row = QtWidgets.QHBoxLayout()
        m = row.getContentsMargins()
        row.setContentsMargins(m[0], 0, m[2], 0)  # pack layers together
        checkbox = QtWidgets.QCheckBox(layer.display_name)
        checkbox.setChecked(layer.is_visible)
        checkbox.stateChanged.connect(layer.set_visible)
        row.addWidget(checkbox)
        self.setLayout(row)
