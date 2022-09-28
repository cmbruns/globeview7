"""
TODO: show individual H3 cell in globeview.
"""

import h3
import numpy


class H3Cell(object):
    def __init__(self, address: str = "8045fffffffffff"):
        self._address = address
        # Note h3_to_geo_boundary returns coordinates in lat/lng order
        cell_boundary = h3.h3_to_geo_boundary(self._address)
        # TODO: shift to a more local origin for better numerical stability
        self.boundary = numpy.radians(cell_boundary, dtype=numpy.float32)

    @property
    def address(self):
        return self._address

    def initialize_opengl(self):
        pass

    def paint_opengl(self, context):
        pass
