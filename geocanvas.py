import math

import numpy
from numpy.linalg import inv
from OpenGL import GL
from PySide6 import QtCore, QtOpenGLWidgets, QtGui
from PySide6.QtCore import Qt

import coastline


class GeoCanvas(QtOpenGLWidgets.QOpenGLWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseTracking(True)
        # TODO: extract render context
        self.aspect2 = 1.0  # sqrt(width/height)
        self.zoom = 1.0  # windows per hemisphere
        # TODO: test azimuth with everything
        self.azimuth = math.radians(0)  # "up" compass direction
        self.ndc_X_nmc = numpy.eye(3, dtype=numpy.float32)
        self.nmc_X_ndc = numpy.eye(3, dtype=numpy.float32)
        self.center_longitude = math.radians(30)
        self.center_latitude = math.radians(0)
        self.ecf_X_obq = numpy.eye(3, dtype=numpy.float32)
        self._update_view_matrix()
        self._update_centering_matrix()
        #
        self.painter = QtGui.QPainter()
        self.font = self.painter.font()
        # self.font.setPointSize(self.font.pointSize() * 4)
        self.coastline = coastline.Coastline()
        self.previous_mouse = None

    def initializeGL(self) -> None:
        self.coastline.initialize_opengl()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        xyw_win = numpy.array((event.x(), event.y(), 1), dtype=numpy.float)
        ndc_X_win = numpy.array((
            (2 / self.width(), 0, -1),
            (0, -2 / self.height(), 1),
            (0, 0, 1),
        ), dtype=numpy.float)
        p_ndc = ndc_X_win @ xyw_win
        p_nmc = self.nmc_X_ndc @ p_ndc
        p_prj = p_nmc * math.pi / 2
        p_deg = p_prj * 180 / math.pi
        p_obq = numpy.array([
            math.cos(p_prj[0]) * math.cos(p_prj[1]),
            math.sin(p_prj[0]) * math.cos(p_prj[1]),
            math.sin(p_prj[1])
        ], dtype=numpy.float)
        p_ecf = self.ecf_X_obq @ p_obq  # Adjust for center longitude
        if event.buttons() & Qt.LeftButton:  # dragging
            if self.previous_mouse is not None:
                dwin = xyw_win[:2] - self.previous_mouse[:2]
                a2 = self.aspect2
                w = self.width()
                h = self.height()
                z = self.zoom
                ca = math.cos(self.azimuth)
                sa = math.sin(self.azimuth)
                nmc_J_win = numpy.array([
                    [2.0 * a2 * ca / (w * z), -2.0 * sa / (a2 * h * z)],
                    [-2.0 * a2 * sa / (w * z), -2.0 * ca / (a2 * h * z)]], dtype=numpy.float)
                dnmc = nmc_J_win @ dwin
                self.statusMessageRequested.emit(f"{dnmc[0]:.3f}, {dnmc[1]:.3f}", 2000)
                # Display projection specific Jacobian
                wgs84prj_J_nmc = numpy.array([
                    [math.pi / 2.0, 0],
                    [0, math.pi / 2.0]], dtype=numpy.float)
                dwgs84prj = wgs84prj_J_nmc @ dnmc
                # print(dwgs84prj)
                c0 = math.cos(p_prj[0])
                s0 = math.sin(p_prj[0])
                c1 = math.cos(p_prj[1])
                s1 = math.sin(p_prj[1])
                obq_J_wgs84prj = numpy.array([
                    [-s0 * c1, -c0 * s1],
                    [c0 * c1, -s0 * s1],
                    [0, c1]], dtype=numpy.float)
                dobq = obq_J_wgs84prj @ dwgs84prj
                ecf_J_obq = self.ecf_X_obq[0:3, 0:3]
                decf = ecf_J_obq @ dobq
                # print([f"{x:0.3f}" for x in p_ecf])
                xy2 = p_ecf[0]**2 + p_ecf[1]**2
                sxy2 = xy2 ** 0.5
                wgs_J_ecf = numpy.array([
                    [-p_ecf[1] / xy2, p_ecf[0] / xy2, 0],
                    [-p_ecf[0] * p_ecf[2] / sxy2, -p_ecf[1] * p_ecf[2] / sxy2, sxy2],
                ], dtype=numpy.float)
                dwgs = wgs_J_ecf @ decf
                self.center_longitude -= dwgs[0]
                self.center_latitude -= dwgs[1]
                # TODO: check latitude in setter
                if self.center_latitude > math.pi/2:
                    self.center_latitude = math.pi/2
                if self.center_latitude < -math.pi/2:
                    self.center_latitude = -math.pi/2
                self._update_centering_matrix()
                self.update()
            self.previous_mouse = xyw_win
            return
        # Back to wgs84
        p_wgs = numpy.array([
            math.atan2(p_ecf[1], p_ecf[0]),
            math.asin(p_ecf[2]),
            1
        ], dtype=numpy.float)
        p_deg2 = p_wgs * 180 / math.pi
        # self.statusMessageRequested.emit(f"{xyw_win} [win]", 2000)
        # self.statusMessageRequested.emit(f"({xyw_ndc[0]:.4f}, {xyw_ndc[1]:.4f}) [ndc]", 2000)
        # self.statusMessageRequested.emit(f"({p_nmc[0]:.4f}, {p_nmc[1]:.4f}) [nmc]", 2000)
        # self.statusMessageRequested.emit(f"({p_deg[0]:.4f}, {p_deg[1]:.4f}) [wgs84]", 2000)
        # self.statusMessageRequested.emit(f"({p_obq[0]:.4f}, {p_obq[1]:.4f}, {p_obq[2]:.4f}) [ecef]", 2000)
        # self.statusMessageRequested.emit(f"({p_ecf[0]:.4f}, {p_ecf[1]:.4f}, {p_ecf[2]:.4f}) [ecef]", 2000)
        self.statusMessageRequested.emit(f"({p_deg2[0]:.4f}, {p_deg2[1]:.4f}) [wgs84]", 2000)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        xyw_win = numpy.array((event.x(), event.y(), 1), dtype=numpy.float)
        self.previous_mouse = xyw_win

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        self.previous_mouse = None

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

    def set_azimuth(self, azimuth_degrees):
        az = math.radians(azimuth_degrees)
        if self.azimuth == az:
            return
        self.azimuth = az
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
        rot_lon = numpy.array([
            [clon, -slon, 0],
            [slon, clon, 0],
            [0, 0, 1]
        ], dtype=numpy.float)
        clat = math.cos(self.center_latitude)
        slat = math.sin(self.center_latitude)
        rot_lat = numpy.array([
            [clat, 0, -slat],
            [0, 1, 0],
            [slat, 0, clat],
        ], dtype=numpy.float)
        self.ecf_X_obq[:] = rot_lon @rot_lat

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
