import numpy
from OpenGL import GL
from PySide6 import QtCore, QtOpenGLWidgets, QtGui


class GeoCanvas(QtOpenGLWidgets.QOpenGLWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseTracking(True)
        self.painter = QtGui.QPainter()
        self.font = self.painter.font()
        # self.font.setPointSize(self.font.pointSize() * 4)

    def initializeGL(self) -> None:
        pass

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        xyw_win = numpy.array((event.x(), event.y(), 1), dtype=numpy.float)
        self.statusMessageRequested.emit(f"{xyw_win} [win]", 2000)

    def paintGL(self) -> None:
        self.painter.begin(self)
        self.painter.beginNativePainting()
        self.paint_opengl()
        self.painter.endNativePainting()
        self.paint_qt(self.painter)
        self.painter.end()

    def paint_opengl(self):
        GL.glClearColor(254/255, 247/255, 228/255, 1)  # Ivory
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

    def paint_qt(self, painter):
        painter.setFont(self.font)
        painter.setPen(QtGui.QColor("#07495f"))  # Dark blue
        painter.drawText(50, 50, "Some Text")

    def resizeGL(self, width: int, height: int) -> None:
        pass

    statusMessageRequested = QtCore.Signal(str, int)
