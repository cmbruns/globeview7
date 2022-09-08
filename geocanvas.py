import numpy
from OpenGL import GL
from PySide6 import QtCore, QtOpenGLWidgets, QtGui

import coastline


class GeoCanvas(QtOpenGLWidgets.QOpenGLWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseTracking(True)
        # TODO: camera model, data model
        self.aspect2 = 1.0
        self.zoom = 1.0
        self.view_matrix = numpy.eye(3, dtype=numpy.float32)
        # self.model_matrix = numpy.eye(3, dtype=numpy.float32)
        self.projection_matrix = numpy.eye(3, dtype=numpy.float32)
        #
        self.painter = QtGui.QPainter()
        self.font = self.painter.font()
        # self.font.setPointSize(self.font.pointSize() * 4)
        self.coastline = coastline.Coastline()

    def initializeGL(self) -> None:
        self.coastline.initialize_opengl()

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
        # TODO: Experimental coastline sketch
        self.coastline.paint_opengl(context=self)

    def paint_qt(self, painter):
        # Experimental label sketch
        painter.setFont(self.font)
        painter.setPen(QtGui.QColor("#07495f"))  # Dark blue
        painter.drawText(50, 50, "Some Text")

    def resizeGL(self, width: int, height: int) -> None:
        aspect = width / height
        a2 = aspect ** 0.5
        if self.aspect2 == a2:
            return
        self.aspect2 = a2
        self.projection_matrix[:] = numpy.array(
            (
                (1/a2, 0,  0),
                (0,    a2, 0),
                (0,    0,  1),
            ),
            dtype=numpy.float32,
        )
        self.update()

    statusMessageRequested = QtCore.Signal(str, int)

    def wheelEvent(self, event: QtGui.QWheelEvent):
        d_scale = event.angleDelta().y() / 120.0
        if d_scale == 0:
            return
        d_scale = 1.10 ** d_scale
        self.zoom *= d_scale
        self.view_matrix[:] = numpy.array(
            (
                (self.zoom, 0, 0),
                (0, self.zoom, 0),
                (0, 0,  1),
            ),
            dtype=numpy.float32,
        )
        self.update()
