import abc
import math

from view_state import NMCPoint, OBQPoint


class DisplayProjection(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def obq_for_nmc(p_nmc: NMCPoint) -> OBQPoint:
        pass


class WGS84Projection(DisplayProjection):
    @staticmethod
    def obq_for_nmc(p_nmc: NMCPoint) -> OBQPoint:
        return OBQPoint(p_nmc.vector * math.pi / 2.0)
