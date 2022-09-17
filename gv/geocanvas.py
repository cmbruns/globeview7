import functools
import math
import pkg_resources

import numpy
from OpenGL import GL
from PIL import Image
from PIL.ImageQt import ImageQt
from PySide6 import QtCore, QtOpenGLWidgets, QtGui, QtWidgets
from PySide6.QtCore import Qt

import coastline
import frame
from gv.projection import Projection, OrthographicProjection, WGS84Projection
from view_state import ViewState


class GeoCanvas(QtOpenGLWidgets.QOpenGLWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fh = pkg_resources.resource_stream("gv", "crosshair32.png")
        img = ImageQt(Image.open(fh).convert("RGBA"))
        cursor = QtGui.QCursor(QtGui.QPixmap.fromImage(img))
        self.setCursor(cursor)
        self.setMouseTracking(True)
        self.view_state = ViewState()
        #
        self.painter = QtGui.QPainter()
        self.font = self.painter.font()
        # self.font.setPointSize(self.font.pointSize() * 4)
        self.coastline = coastline.Coastline()
        self.previous_mouse = None

    def center_on_window_pixel(self, pos: QtCore.QPoint):
        wgs = self.view_state.wgs_for_window_point(frame.WindowPoint.from_qpoint(pos))
        self.view_state.center_location = wgs
        self.update()

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        center_action = QtGui.QAction(text="Center on this location", parent=self)
        center_action.triggered.connect(functools.partial(self.center_on_window_pixel, event.pos()))
        menu = QtWidgets.QMenu(self)
        menu.addAction(center_action)
        menu.addAction(QtGui.QAction(text="Cancel [ESC]", parent=self))
        menu.exec(event.globalPos())

    def initializeGL(self) -> None:
        self.coastline.initialize_opengl()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        # TODO: refactor dragging to use ViewState jacobian methods
        xyw_win = numpy.array((event.x(), event.y(), 1), dtype=numpy.float)
        p_ndc = self.view_state.ndc_X_win @ xyw_win
        p_nmc = self.view_state.nmc_X_ndc @ p_ndc
        p_prj = p_nmc
        p_obq = numpy.array([
            math.cos(p_prj[0]) * math.cos(p_prj[1]),
            math.sin(p_prj[0]) * math.cos(p_prj[1]),
            math.sin(p_prj[1])
        ], dtype=numpy.float)
        p_ecf = self.view_state.ecf_X_obq @ p_obq  # Adjust for center longitude
        if event.buttons() & Qt.LeftButton:  # dragging
            if self.previous_mouse is not None:
                dwin = xyw_win[:2] - self.previous_mouse[:2]
                dnmc = self.view_state.nmc_J_win @ dwin
                try:
                    dobq = self.view_state._projection.dobq_for_dnmc(dnmc, p_nmc)
                except RuntimeError:
                    return  # TODO: handle outside cases in projection
                print(f"dobq: {dobq}")
                # Compute center latitude shift from obq shift
                px, py, pz = p_obq
                xy2 = px**2 + py**2
                sxy2 = xy2 ** 0.5
                dlat = numpy.dot(dobq, [-px * pz / sxy2, -py * pz / sxy2, sxy2])
                #
                decf = self.view_state.ecf_J_obq @ dobq
                print(f"decf: {decf}")
                px, py, pz = p_ecf
                xy2 = px**2 + py**2
                sxy2 = xy2 ** 0.5
                # https://en.wikipedia.org/wiki/List_of_common_coordinate_transformations#From_Cartesian_coordinates
                wgs_J_ecf = numpy.array([
                    [-py / xy2, px / xy2, 0],
                    [-px * pz / sxy2, -py * pz / sxy2, sxy2],
                ], dtype=numpy.float)
                dwgs = wgs_J_ecf @ decf
                self.view_state.center_location -= numpy.array([dwgs[0], dlat])  # TODO: simplify dlon
                self.update()
            self.previous_mouse = xyw_win
            return
        # Back to wgs84
        p_wgs = numpy.array([
            math.atan2(p_ecf[1], p_ecf[0]),
            math.asin(p_ecf[2]),
            1
        ], dtype=numpy.float)
        # self.statusMessageRequested.emit(f"{xyw_win} [win]", 2000)
        # self.statusMessageRequested.emit(f"({xyw_ndc[0]:.4f}, {xyw_ndc[1]:.4f}) [ndc]", 2000)
        # self.statusMessageRequested.emit(f"({p_nmc[0]:.4f}, {p_nmc[1]:.4f}) [nmc]", 2000)
        # self.statusMessageRequested.emit(f"({p_deg[0]:.4f}, {p_deg[1]:.4f}) [wgs84]", 2000)
        # self.statusMessageRequested.emit(f"({p_obq[0]:.4f}, {p_obq[1]:.4f}, {p_obq[2]:.4f}) [ecef]", 2000)
        # self.statusMessageRequested.emit(f"({p_ecf[0]:.4f}, {p_ecf[1]:.4f}, {p_ecf[2]:.4f}) [ecef]", 2000)
        wgs2 = frame.WGS84Point(p_wgs)
        self.statusMessageRequested.emit(f"{wgs2}", 2000)

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
        self.coastline.paint_opengl(context=self.view_state)

    def paint_qt(self, painter):
        # Experimental label sketch
        painter.setFont(self.font)
        painter.setPen(QtGui.QColor("#07495f"))  # Dark blue
        painter.drawText(50, 50, "Some Text")

    def resizeGL(self, width: int, height: int) -> None:
        self.view_state.window_size = width, height
        self.update()

    def set_azimuth(self, azimuth_degrees):
        self.view_state.azimuth = math.radians(azimuth_degrees)
        self.update()

    def set_projection(self, projection: Projection):
        if projection == self.view_state._projection.index:
            return  # No Change
        if projection == Projection.EQUIRECTANGULAR:
            self.view_state._projection = WGS84Projection()
        elif projection == Projection.ORTHOGRAPHIC:
            self.view_state._projection = OrthographicProjection()
        else:
            raise NotImplementedError
        self.update()

    statusMessageRequested = QtCore.Signal(str, int)

    def wheelEvent(self, event: QtGui.QWheelEvent):
        d_scale = event.angleDelta().y() / 120.0
        if d_scale == 0:
            return
        d_scale = 1.10 ** d_scale
        self.view_state.zoom *= d_scale
        self.update()
