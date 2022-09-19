import abc
import enum
import math

import numpy
from PySide6.QtCore import QPoint  # Separation of concerns: no further Qt please


class Frame(enum.Enum):
    """
    Coordinate systems ordered from window pixel to data source spatial reference
    """
    WIN = 1  # Qt window pixel coordinate
    NDC = 2  # OpenGL normalized device coordinate
    NMC = 3  # Normalized map coordinate (applies aspect, zoom, azimuth)
    PRJ = 4  # Display projection, varies with choice of display projection
    OBQ = 5  # Rotated (oblique) auxilliary geocentric coordinates centered on lon0, lat0
    ECF = 6  # Un-rotated ECEF auxilliary geocentric coordinates
    WGS = 7  # WGS84 geographic coordinates
    DAT = 8  # Native spatial reference of a particular layer data source


class FramedPoint(abc.ABC):
    def __init__(self, vector):
        self.vector = numpy.array(vector, dtype=numpy.float32)

    def __getitem__(self, key):
        return self.vector[key]

    def __len__(self):
        return len(self.vector)

    @classmethod
    @property
    @abc.abstractmethod
    def frame(cls):
        raise NotImplementedError

    @property
    def x(self):
        return self.vector[0]

    @property
    def y(self):
        return self.vector[1]

    @property
    def z(self):
        return self.vector[2]

    @property
    def w(self):
        return self.vector[-1]


class NMCPoint(FramedPoint):
    frame = Frame.NMC


class OBQPoint(FramedPoint):
    frame = Frame.OBQ


class WGS84Point(FramedPoint):
    frame = Frame.WGS

    def __str__(self):
        lon = math.degrees(self[0])
        lat = math.degrees(self[1])
        d = ["E", "N"]
        if lon < 0:
            lon = -lon
            d[0] = "W"
        if lat < 0:
            lat = -lat
            d[1] = "S"
        deg = "\N{DEGREE SIGN}"
        return f"{lon:7.3f}{deg}{d[0]} {lat:6.3f}{deg}{d[1]}"


class WindowPoint(FramedPoint):
    frame = Frame.WIN

    @staticmethod
    def from_qpoint(qpoint: QPoint) -> "WindowPoint":
        return WindowPoint([qpoint.x(), qpoint.y(), 1])
