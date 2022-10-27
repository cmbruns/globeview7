"""
TODO: show individual H3 cell in globeview.
"""

from math import radians

import h3
from OpenGL import GL
from OpenGL.GL.shaders import compileShader, compileProgram

from gv.layer import ILayer
from gv.vertex_buffer import VertexBuffer
from gv import shader


class H3Cell(ILayer):
    def __init__(self, address: str = "8045fffffffffff"):
        super().__init__(name=f"H3 {address}")
        self._address = address
        # Note h3_to_geo_boundary returns coordinates in lat/lng order
        cell_boundary = h3.h3_to_geo_boundary(self._address)
        # swap order and convert to radians
        wgs = [(radians(lon), radians(lat)) for lat, lon in cell_boundary]
        # TODO: shift to a more local origin for better numerical stability
        self.boundary = VertexBuffer(wgs)
        self.program = None
        self.line_width = 1.0

    @property
    def address(self):
        return self._address

    def initialize_opengl(self):
        self.boundary.bind()
        self.program = compileProgram(
            shader.from_files(["projection.glsl", "h3cell.vert"], GL.GL_VERTEX_SHADER),
            shader.from_files(["projection.glsl", "h3cell.geom"], GL.GL_GEOMETRY_SHADER),
            shader.from_files(["green.frag"], GL.GL_FRAGMENT_SHADER),
        )
        ub_index = GL.glGetUniformBlockIndex(self.program, "TransformBlock")
        GL.glUniformBlockBinding(self.program, ub_index, 2)
        line_width_range = GL.glGetIntegerv(GL.GL_ALIASED_LINE_WIDTH_RANGE)
        self.line_width = min(3, line_width_range[1])
        GL.glBindVertexArray(0)

    def draw_boundary(self, context):
        if self.program is None:
            self.initialize_opengl()
        GL.glUseProgram(self.program)
        self.boundary.bind()
        GL.glLineWidth(self.line_width)
        GL.glDrawArrays(GL.GL_LINE_LOOP, 0, len(self.boundary))

    def paint_opengl(self, context):
        self.draw_boundary(context)
