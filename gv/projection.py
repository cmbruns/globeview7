import abc
import math

from gv.frame import NMCPoint, OBQPoint


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
    @staticmethod
    def obq_for_nmc(p_nmc: NMCPoint) -> OBQPoint:
        p_prj = p_nmc * math.pi / 2  # Radians from normalized units
        result = OBQPoint((
            math.cos(p_prj[0]) * math.cos(p_prj[1]),
            math.sin(p_prj[0]) * math.cos(p_prj[1]),
            math.sin(p_prj[1]),
        ))
        return result
