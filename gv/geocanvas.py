import functools
import math
import pkg_resources

from PIL import Image
from PIL.ImageQt import ImageQt
from PySide6 import QtCore, QtOpenGLWidgets, QtGui, QtWidgets
from PySide6.QtCore import Qt

from gv import basemap, h3cell
from gv import coastline
from gv import frame
from gv import graticule
from gv import planet
from gv.projection import *
from gv.view_state import ProjectionOutlineLayer, ViewState


class GeoCanvas(QtOpenGLWidgets.QOpenGLWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fh = pkg_resources.resource_stream("gv", "crosshair32.png")
        img = ImageQt(Image.open(fh).convert("RGBA"))
        cursor = QtGui.QCursor(QtGui.QPixmap.fromImage(img))
        self.setCursor(cursor)
        self.setMouseTracking(True)
        self.view_state = ViewState()
        self.planet = planet.Earth()
        #
        self.painter = QtGui.QPainter()
        self.font = self.painter.font()
        # self.font.setPointSize(self.font.pointSize() * 4)
        self.layers = []
        self.layers.append(ProjectionOutlineLayer(self.view_state))
        self.layers.append(h3cell.H3Cell())
        self.layers.append(coastline.Coastline("Coast Lines"))
        self.layers.append(graticule.Graticule("Graticule"))
        self.layers.append(basemap.RootRasterTile("Satellite"))
        for layer in self.layers:
            layer.visibility_changed.connect(self.update)
        # self.coastline = coastline.Coastline()
        # self.basemap = basemap.RootRasterTile()
        # self.h3 = h3cell.H3Cell()
        #
        self.previous_mouse = None
        self.actionReset_View = None
        self.view_state.azimuth_changed.connect(self.azimuth_changed)
        self.view_state.center_location_changed.connect(self.center_location_changed)
        self.ubo = None

    azimuth_changed = QtCore.Signal(float)

    def center_location_changed(self, center):
        lon, lat = center
        self.center_longitude_changed.emit(lon)
        self.center_latitude_changed.emit(lat)

    center_latitude_changed = QtCore.Signal(float)
    center_longitude_changed = QtCore.Signal(float)

    def center_on_window_pixel(self, pos: QtCore.QPoint):
        wgs = self.view_state.wgs_for_window_point(frame.WindowPoint.from_qpoint(pos))
        self.view_state.center_location = [math.degrees(a) for a in wgs]
        self.update()

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        center_action = QtGui.QAction(text="Center on this location", parent=self)
        center_action.triggered.connect(functools.partial(self.center_on_window_pixel, event.pos()))
        menu = QtWidgets.QMenu(self)
        menu.addAction(center_action)
        menu.addAction(self.actionReset_View)
        menu.addAction(QtGui.QAction(text="Cancel [ESC]", parent=self))
        menu.exec(event.globalPos())

    def initializeGL(self) -> None:
        self.ubo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_UNIFORM_BUFFER, self.ubo)
        GL.glBindBufferBase(GL.GL_UNIFORM_BUFFER, 2, self.ubo)  # Assign binding point "2" to TransformBlock
        GL.glBufferData(GL.GL_UNIFORM_BUFFER, 16 + 4*64, None, GL.GL_DYNAMIC_DRAW)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        # TODO: refactor dragging to use ViewState jacobian methods
        xyw_win = numpy.array((event.x(), event.y(), 1), dtype=numpy.float)
        p_ndc = self.view_state.ndc_X_win @ xyw_win
        p_nmc = self.view_state.nmc_X_ndc @ p_ndc
        if not self.view_state.projection.is_valid_nmc(NMCPoint(p_nmc)):
            self.previous_mouse = None
            return
        p_prj = p_nmc

        p_obq = self.view_state.projection.obq_for_nmc(p_nmc)
        p_ecf = self.view_state.ecf_X_obq @ p_obq  # Adjust for center longitude
        # Back to wgs84
        p_wgs = numpy.array([
            math.atan2(p_ecf[1], p_ecf[0]),
            math.asin(p_ecf[2]),
            1
        ], dtype=numpy.float)
        if event.buttons() & Qt.LeftButton:  # dragging
            if self.previous_mouse is not None:
                dwin = xyw_win[:2] - self.previous_mouse[:2]
                dnmc = self.view_state.nmc_J_win @ dwin
                try:
                    dobq = self.view_state._projection.dobq_for_dnmc(dnmc, p_nmc)
                except RuntimeError:
                    self.previous_mouse = None
                    return  # TODO: handle outside cases in projection
                # Compute center latitude shift from obq shift
                # TODO: this might not be the perfect solution.
                px, py, pz = p_obq
                xy2 = px**2 + py**2
                sxy2 = xy2 ** 0.5
                dlat = numpy.dot(dobq, [-px * pz / sxy2, -py * pz / sxy2, sxy2])
                #
                decf = self.view_state.ecf_J_obq @ dobq
                px, py, pz = p_ecf
                xy2 = px**2 + py**2
                sxy2 = xy2 ** 0.5
                # https://en.wikipedia.org/wiki/List_of_common_coordinate_transformations#From_Cartesian_coordinates
                wgs_J_ecf = numpy.array([
                    [-py / xy2, px / xy2, 0],
                    [-px * pz / sxy2, -py * pz / sxy2, sxy2],
                ], dtype=numpy.float)
                dwgs = wgs_J_ecf @ decf
                # Latitude angle has a discontinuity; below seems like the right correction.
                # TODO: dragging north-south at lon-lon0==90 does nothing. should it?
                dlat0_factor = math.cos(p_wgs[0] - radians(self.view_state.center_location[0]))
                dlat2 = math.degrees(dwgs[1] * dlat0_factor)
                dlon = math.degrees(dwgs[0])
                # limit size of longitude movement when dragging near poles
                if abs(p_wgs[1]) > radians(80):
                    max_dlon = 5
                    dlon = min(dlon, max_dlon)
                    dlon = max(dlon, -max_dlon)
                self.view_state.center_location -= numpy.array([dlon, dlat2])  # TODO: simplify dlon
                self.update()
            self.previous_mouse = xyw_win
            return
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
        if self.painter is None:
            self.painter = QtGui.QPainter()
            self.painter.begin(self)
            self.font = self.painter.font()
        else:
            self.painter.begin(self)
        self.painter.beginNativePainting()
        self.paint_opengl()
        self.painter.endNativePainting()
        self.paint_qt(self.painter)
        self.painter.end()

    def paint_opengl(self):
        GL.glClearColor(254/255, 247/255, 228/255, 1)  # Ivory
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Fill TransformBlock uniform block
        GL.glBindBuffer(GL.GL_UNIFORM_BUFFER, self.ubo)
        vs = self.view_state
        GL.glBufferSubData(GL.GL_UNIFORM_BUFFER, 0, 4,  # Projection
                           numpy.array([vs.projection.index.value], dtype=numpy.int32))
        GL.glBufferSubData(GL.GL_UNIFORM_BUFFER, 8, 4,  # Altitude
                           numpy.array([vs.altitude], dtype=numpy.float32))
        # Create 4x4 versions of transform matrices - because std140
        m4 = numpy.eye(4, dtype=numpy.float32)
        m4[:3, :3] = vs.ndc_X_nmc.T  # transpose to convert to OpenGL expectations
        GL.glBufferSubData(GL.GL_UNIFORM_BUFFER, 16, 64, m4)
        m4[:3, :3] = vs.ecf_X_obq  # Not-transpose to get rotation inverse
        GL.glBufferSubData(GL.GL_UNIFORM_BUFFER, 80, 64, m4)
        m4[:3, :3] = vs.ecf_X_obq.T
        GL.glBufferSubData(GL.GL_UNIFORM_BUFFER, 144, 64, m4)
        m4[:3, :3] = vs.nmc_X_ndc.T
        GL.glBufferSubData(GL.GL_UNIFORM_BUFFER, 208, 64, m4)

        # Shared OpenGL state - in initialize?
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glEnable(GL.GL_BLEND)
        GL.glEnable(GL.GL_LINE_SMOOTH)

        # TODO: more separate generic layer classes
        for layer in reversed(self.layers):  # top layer last
            if not layer.is_visible:
                continue
            layer.paint_opengl(context=self.view_state)
        # self.coastline.paint_opengl(context=self.view_state)
        # self.h3.draw_boundary(self.view_state)
        # self.view_state.projection.draw_boundary(context=self.view_state)
        # Clean up; Avoid borking later Qt text
        GL.glBindVertexArray(0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

    def paint_qt(self, painter):
        # TODO: layer for qt stuff
        # Experimental label sketch
        painter.setFont(self.font)
        painter.setPen(QtGui.QColor("#07495f"))  # Dark blue
        painter.drawText(50, 50, "Some Text")
        for layer in self.layers:
            if not layer.is_visible:
                continue
            if not hasattr(layer, "attribution"):
                continue
            attribution = layer.attribution
            # Attribution : TODO
            # TODO: only when esri basemap is shown
            font = QtGui.QFont(["Avenir Next W00", "Helvetica Neue", "Helvetica", "Ariel"], 8)
            painter.setFont(font)
            fm = QtGui.QFontMetrics(font)
            th = fm.height()  # text box height
            bh = th + 6
            w, h = self.width(), self.height()
            # 65% transparent white background
            painter.fillRect(0, h - bh, w, bh, QtGui.QColor("#a6ffffff"))
            # painter.setClipRect(0, h - bh, w - tw, bh)
            painter.setPen(QtGui.QColor("#323232"))  # default esri style
            t = "Powered by Esri"
            tw = fm.horizontalAdvance(t)
            painter.drawText(w - tw - 4, h - 6, t)
            painter.setClipRect(0, h - bh, w - tw - 10, bh)
            painter.drawText(4, h - 6, attribution)
            # painter.setClipRect(None)

    def reset_view(self):
        self.view_state.center_location = [0, 0]
        self.view_state.azimuth = 0
        self.view_state.zoom = 0.7
        self.view_state.altitude = 6378
        self.update()

    def resizeGL(self, width: int, height: int) -> None:
        self.view_state.window_size = width, height
        self.update()

    def set_altitude(self, altitude_km):
        self.view_state.altitude = altitude_km / self.planet.radius_km
        self.update()

    def set_azimuth(self, azimuth_degrees):
        self.view_state.azimuth = azimuth_degrees
        self.update()

    def set_center_latitude(self, lat_degrees):
        lon, lat = self.view_state.center_location
        if lat == lat_degrees:
            return
        self.view_state.center_location = lon, lat_degrees
        self.update()

    def set_center_longitude(self, lon_degrees):
        lon, lat = self.view_state.center_location
        if lon == lon_degrees:
            return
        self.view_state.center_location = lon_degrees, lat
        self.update()

    def set_projection(self, projection: Projection):
        if projection == self.view_state.projection.index:
            return  # No Change
        if projection == Projection.PERSPECTIVE:
            self.view_state._projection = projection_for_enum(projection)(self.view_state)
        else:
            self.view_state._projection = projection_for_enum(projection)()
        self.update()

    statusMessageRequested = QtCore.Signal(str, int)

    def wheelEvent(self, event: QtGui.QWheelEvent):
        d_scale = event.angleDelta().y() / 120.0
        if d_scale == 0:
            return
        d_scale = 1.10 ** d_scale
        self.view_state.zoom *= d_scale
        self.update()
