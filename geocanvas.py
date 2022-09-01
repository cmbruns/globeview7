import numpy
from OpenGL import GL
from PySide6 import QtCore, QtOpenGLWidgets, QtGui


class GeoCanvas(QtOpenGLWidgets.QOpenGLWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseTracking(True)
        self.painter = QtGui.QPainter()
        self.font = self.painter.font()
        self.font.setPointSize(self.font.pointSize() * 4)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        xy = numpy.array((event.x(), event.y()), dtype=numpy.float)
        self.statusMessageRequested.emit(f"{xy} [win]")

    def paintGL(self) -> None:
        self.painter.begin(self)
        self.painter.beginNativePainting()

        GL.glClearColor(254/255, 247/255, 228/255, 1)  # Ivory
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        self.painter.endNativePainting()

        self.painter.setFont(self.font)
        self.painter.setPen(QtGui.QColor("#03446e"))  # Dark blue
        self.painter.drawText(50, 50, "Some Text")

        self.painter.end()

    statusMessageRequested = QtCore.Signal(str)
