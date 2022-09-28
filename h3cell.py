"""
TODO: show individual H3 cell in globeview.
"""

import inspect

import h3
from OpenGL import GL
from OpenGL.GL.shaders import compileShader, compileProgram

from gv.vertex_buffer import VertexBuffer
from gv import shader


class H3Cell(object):
    def __init__(self, address: str = "8045fffffffffff"):
        self._address = address
        # Note h3_to_geo_boundary returns coordinates in lat/lng order
        cell_boundary = h3.h3_to_geo_boundary(self._address)
        # TODO: shift to a more local origin for better numerical stability
        self.boundary = VertexBuffer(cell_boundary)
        self.program = None
        self.obq_X_ecf_loc = None
        self.ndc_X_nmc_loc = None
        self.projection_loc = None

    @property
    def address(self):
        return self._address

    def initialize_opengl(self):
        self.boundary.initialize_opengl()
        self.program = compileProgram(
            shader.from_files(["projection.glsl", "h3cell.vert"], GL.GL_VERTEX_SHADER),
            shader.from_files(["green.frag"], GL.GL_FRAGMENT_SHADER),
        )
        self.obq_X_ecf_loc = GL.glGetUniformLocation(self.program, "obq_X_ecf")
        self.ndc_X_nmc_loc = GL.glGetUniformLocation(self.program, "ndc_X_nmc")
        self.projection_loc = GL.glGetUniformLocation(self.program, "projection")

    def draw_boundary(self, context):
        if self.program is None:
            self.initialize_opengl()
        GL.glUseProgram(self.program)
        GL.glUniformMatrix3fv(self.obq_X_ecf_loc, 1, False, context.ecf_X_obq)  # transpose is inverse
        GL.glUniformMatrix3fv(self.ndc_X_nmc_loc, 1, True, context.ndc_X_nmc)
        GL.glUniform1i(self.projection_loc, context.projection.index.value)
        self.boundary.bind()
        GL.glLineWidth(3)
        GL.glDrawArrays(GL.GL_LINE_LOOP, 0, len(self.boundary))

