from math import asin, atan2, cos, pi, radians, sin

import numpy
from PySide6 import QtCore

from gv.frame import WGS84Point, WindowPoint
from gv.projection import EquirectangularProjection
from gv.layer import ILayer


class Transform(object):
    def __init__(self, size=3):
        self.matrix = numpy.eye(size, dtype=numpy.float32)
        self.dirty = True


class ViewState(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self._projection = EquirectangularProjection()
        self._window_size = [1, 1]
        # TODO: should center be in degrees? Does the principle of best exactness apply here?
        self._center_location = [radians(0), radians(0)]
        self._zoom = 0.7  # windows per radian
        self._azimuth = 0  # "up" compass direction degrees
        self._ecf_X_obq = Transform()
        self._ndc_X_nmc = Transform()
        self._ndc_X_win = Transform()
        self._nmc_X_ndc = Transform()
        self._nmc_J_win = Transform(2)

    @property
    def azimuth(self):
        return self._azimuth

    @azimuth.setter
    def azimuth(self, azimuth):
        if self._azimuth == azimuth:
            return
        self._azimuth = azimuth
        self._ndc_X_nmc.dirty = True
        self._nmc_X_ndc.dirty = True
        self._nmc_J_win.dirty = True
        self.azimuth_changed.emit(self._azimuth)

    azimuth_changed = QtCore.Signal(float)

    @property
    def center_location(self):
        return self._center_location

    @center_location.setter
    def center_location(self, center):
        lon, lat = center
        if lat > pi / 2:
            lat = pi / 2
        if lat < -pi / 2:
            lat = -pi / 2
        if self._center_location[0] == lon and self._center_location[1] == lat:
            return  # No change
        self._center_location[:] = lon, lat
        self._ecf_X_obq.dirty = True

    @property
    def ecf_X_obq(self):
        if self._ecf_X_obq.dirty:
            clon = cos(self._center_location[0])
            slon = sin(self._center_location[0])
            rot_lon = numpy.array([
                [clon, -slon, 0],
                [slon, clon, 0],
                [0, 0, 1]
            ], dtype=numpy.float)
            clat = cos(self._center_location[1])
            slat = sin(self._center_location[1])
            rot_lat = numpy.array([
                [clat, 0, -slat],
                [0, 1, 0],
                [slat, 0, clat],
            ], dtype=numpy.float)
            self._ecf_X_obq.matrix[:] = rot_lon @ rot_lat
            # self._ecf_X_obq.matrix[:] = rot_lat
            self._ecf_X_obq.dirty = False
        return self._ecf_X_obq.matrix

    @property
    def ecf_J_obq(self):
        return self.ecf_X_obq[0:3, 0:3]

    @property
    def ndc_X_nmc(self):
        if self._ndc_X_nmc.dirty:
            z = self._zoom
            c = cos(radians(self._azimuth))
            s = sin(radians(self._azimuth))
            w, h = self._window_size
            a = (w / h) ** 0.5  # sqrt(aspect ratio)
            self._ndc_X_nmc.matrix[:] = (
                (c * z / a, -s * z / a, 0),
                (s * z * a, c * z * a, 0),
                (0, 0,  1),
            )
            self._ndc_X_nmc.dirty = False
        return self._ndc_X_nmc.matrix

    @property
    def ndc_X_win(self):
        if self._ndc_X_win.dirty:
            w, h = self._window_size
            self._ndc_X_win.matrix[:] = (
                (2 / w, 0, -1),
                (0, -2 / h, 1),
                (0, 0, 1),
            )
            self._ndc_X_win.dirty = False
        return self._ndc_X_win.matrix

    @property
    def nmc_J_win(self):
        if self._nmc_J_win.dirty:
            z = self._zoom
            c = cos(radians(self._azimuth))
            s = sin(radians(self._azimuth))
            w, h = self._window_size
            a2 = (w / h) ** 0.5  # sqrt(aspect ratio)
            self._nmc_J_win.matrix[:] = [
                    [2.0 * a2 * c / (w * z), -2.0 * s / (a2 * h * z)],
                    [-2.0 * a2 * s / (w * z), -2.0 * c / (a2 * h * z)],
            ]
            self._nmc_J_win.dirty = False
        return self._nmc_J_win.matrix

    @property
    def nmc_X_ndc(self):
        if self._nmc_X_ndc.dirty:
            z = self._zoom
            c = cos(radians(self._azimuth))
            s = sin(radians(self._azimuth))
            w, h = self._window_size
            a = (w / h) ** 0.5  # sqrt(aspect ratio)
            self._nmc_X_ndc.matrix[:] = (
                (c * a / z, s / (z * a), 0),
                (-s * a / z, c / (z * a), 0),
                (0, 0,  1),
            )
            self._nmc_X_ndc.dirty = False
        return self._nmc_X_ndc.matrix

    @property
    def projection(self):
        return self._projection

    def wgs_for_window_point(self, p_win: WindowPoint) -> WGS84Point:
        p_nmc = self.nmc_X_ndc @ self.ndc_X_win @ p_win
        p_obq = self._projection.obq_for_nmc(p_nmc)
        p_ecf = self.ecf_X_obq @ p_obq
        p_wgs = WGS84Point([
            atan2(p_ecf[1], p_ecf[0]),
            asin(p_ecf[2]),
        ])
        return p_wgs

    @property
    def window_size(self):
        return self._window_size

    @window_size.setter
    def window_size(self, size):
        if self._window_size[:] == size[:]:
            return  # No change
        self._window_size[:] = size[:]
        self._ndc_X_win.dirty = True
        self._ndc_X_nmc.dirty = True
        self._nmc_X_ndc.dirty = True
        self._nmc_J_win.dirty = True

    @property
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self, zoom):
        if zoom < 0.05:
            zoom = 0.05
        if self._zoom == zoom:
            return
        self._zoom = zoom
        self._ndc_X_nmc.dirty = True
        self._nmc_X_ndc.dirty = True
        self._nmc_J_win.dirty = True


class ProjectionOutlineLayer(ILayer):
    def __init__(self, view_state: ViewState):
        super().__init__(name="Boundary")
        self.view_state = view_state

    def paint_opengl(self, context):
        self.view_state.projection.draw_boundary(context)
