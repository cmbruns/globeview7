import math

import numpy
from numpy.linalg import inv
from OpenGL import GL
from PySide6 import QtCore, QtOpenGLWidgets, QtGui

import coastline


class GeoCanvas(QtOpenGLWidgets.QOpenGLWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseTracking(True)
        # TODO: extract render context
        self.aspect2 = 1.0  # sqrt(width/height)
        self.zoom = 1.0  # windows per hemisphere
        # TODO: test azimuth with everything
        self.azimuth = math.radians(30)  # "up" compass direction
        self.ndc_X_nmc = numpy.eye(3, dtype=numpy.float32)
        self.nmc_X_ndc = numpy.eye(3, dtype=numpy.float32)
        self.center_longitude = math.radians(45)
        self.ecef1_X_ecef = numpy.eye(3, dtype=numpy.float32)
        self._update_view_matrix()
        self._update_centering_matrix()
        #
        self.painter = QtGui.QPainter()
        self.font = self.painter.font()
        # self.font.setPointSize(self.font.pointSize() * 4)
        self.coastline = coastline.Coastline()

    def initializeGL(self) -> None:
        self.coastline.initialize_opengl()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        xyw_win = numpy.array((event.x(), event.y(), 1), dtype=numpy.float)
        ndc_X_win = numpy.array((
            (2/self.width(), 0, -1),
            (0, -2/self.height(), 1),
            (0, 0, 1),
        ), dtype=numpy.float)
        p_ndc = ndc_X_win @ xyw_win
        p_nmc = self.nmc_X_ndc @ p_ndc
        p_wgs = p_nmc * math.pi / 2
        p_deg = p_wgs * 180 / math.pi
        p_ecef = numpy.array([
            math.cos(p_wgs[0]) * math.cos(p_wgs[1]),
            math.sin(p_wgs[0]) * math.cos(p_wgs[1]),
            math.sin(p_wgs[1])
        ], dtype=numpy.float)
        p_ecef2 = self.ecef1_X_ecef @ p_ecef  # Adjust for center longitude
        # Back to wgs84
        p_wgs2 = numpy.array([
            math.atan2(p_ecef2[1], p_ecef2[0]),
            math.asin(p_ecef2[2]),
            1
        ], dtype=numpy.float)
        p_deg2 = p_wgs2 * 180 / math.pi
        # self.statusMessageRequested.emit(f"{xyw_win} [win]", 2000)
        # self.statusMessageRequested.emit(f"({xyw_ndc[0]:.4f}, {xyw_ndc[1]:.4f}) [ndc]", 2000)
        # self.statusMessageRequested.emit(f"({p_nmc[0]:.4f}, {p_nmc[1]:.4f}) [nmc]", 2000)
        # self.statusMessageRequested.emit(f"({p_deg[0]:.4f}, {p_deg[1]:.4f}) [wgs84]", 2000)
        # self.statusMessageRequested.emit(f"({p_ecef[0]:.4f}, {p_ecef[1]:.4f}, {p_ecef[2]:.4f}) [ecef]", 2000)
        # self.statusMessageRequested.emit(f"({p_ecef2[0]:.4f}, {p_ecef2[1]:.4f}, {p_ecef2[2]:.4f}) [ecef]", 2000)
        self.statusMessageRequested.emit(f"({p_deg2[0]:.4f}, {p_deg2[1]:.4f}) [wgs84]", 2000)

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
        self._update_view_matrix()
        self.update()

    def set_center_longitude(self, longitude_degrees):
        lon = math.radians(longitude_degrees)
        if lon == self.center_longitude:
            return
        self.center_longitude = lon
        self._update_centering_matrix()
        self.update()

    statusMessageRequested = QtCore.Signal(str, int)

    def _update_centering_matrix(self):
        clon = math.cos(self.center_longitude)
        slon = math.sin(self.center_longitude)
        self.ecef1_X_ecef[:] = numpy.array([
            [clon, -slon, 0],
            [slon, clon, 0],
            [0, 0, 1]
        ], dtype=numpy.float)
        # TODO: latitude

    def _update_view_matrix(self):
        z = self.zoom
        c = math.cos(self.azimuth)
        s = math.sin(self.azimuth)
        a = self.aspect2
        self.ndc_X_nmc[:] = numpy.array(
            (
                (c * z / a, -s * z / a, 0),
                (s * z * a, c * z * a, 0),
                (0, 0,  1),
            ),
            dtype=numpy.float32,
        )
        self.nmc_X_ndc[:] = numpy.array(
            (
                (c * a / z, s / (z * a), 0),
                (-s * a / z, c / (z * a), 0),
                (0, 0,  1),
            ),
            dtype=numpy.float32,
        )

    def wheelEvent(self, event: QtGui.QWheelEvent):
        d_scale = event.angleDelta().y() / 120.0
        if d_scale == 0:
            return
        d_scale = 1.10 ** d_scale
        new_zoom = self.zoom * d_scale
        if new_zoom < 0.05:
            new_zoom = 0.05
        assert self.zoom >= 0.05
        if new_zoom == self.zoom:
            return
        self.zoom = new_zoom
        self._update_view_matrix()
        self.update()
