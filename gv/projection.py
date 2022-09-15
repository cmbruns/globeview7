import abc
import enum
import math

import numpy

from gv.frame import NMCPoint, OBQPoint, FramedPoint


class Projection(enum.IntEnum):
     EQUIRECTANGULAR = 1
     ORTHOGRAPHIC = 2


class DisplayProjection(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def obq_for_nmc(p_nmc: NMCPoint) -> OBQPoint:
        """
        Convert from normalized map coordinates to rotated geocentric coordinates.
        """
        pass


class WGS84Projection(DisplayProjection):
    """
    Plate caree / Equirectangular / Geographic coordinates projection
    """
    index = Projection.EQUIRECTANGULAR

    @staticmethod
    def obq_for_nmc(p_nmc: NMCPoint) -> OBQPoint:
        p_prj = p_nmc  # Radians from normalized units
        result = OBQPoint((
            math.cos(p_prj[0]) * math.cos(p_prj[1]),
            math.sin(p_prj[0]) * math.cos(p_prj[1]),
            math.sin(p_prj[1]),
        ))
        return result

    @staticmethod
    def dobq_for_dnmc(dnmc, p_nmc: NMCPoint):
        p_prj = p_nmc  # Radians are normalized units
        c0 = math.cos(p_prj[0])
        s0 = math.sin(p_prj[0])
        c1 = math.cos(p_prj[1])
        s1 = math.sin(p_prj[1])
        obq_J_wgs84prj = numpy.array([
            [-s0 * c1, -c0 * s1],
            [c0 * c1, -s0 * s1],
            [0, c1]], dtype=numpy.float)
        dwgs84prj = dnmc  # Radians are normalized units
        result = obq_J_wgs84prj @ dwgs84prj
        return result
