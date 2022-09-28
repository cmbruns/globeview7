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
            shader.from_string("""
                #version 410
                
                const int WGS84_PROJECTION = 0;
                const int ORTHOGRAPHIC_PROJECTION = 1;
                
                in vec2 corner;
                uniform mat3 obq_X_ecf = mat3(1);
                uniform mat3 ndc_X_nmc = mat3(1);
                uniform int projection = WGS84_PROJECTION;
                
                void main() {
                    vec2 wgs = radians(corner.yx);
                    vec3 ecf = vec3(
                        cos(wgs.x) * cos(wgs.y),
                        sin(wgs.x) * cos(wgs.y),
                        sin(wgs.y));
                    vec3 obq = obq_X_ecf * ecf;
                    // TODO: gnomonic edge direction
                    vec3 nmc;
                    if (projection == WGS84_PROJECTION) {
                        nmc = vec3(atan(obq.y, obq.x), asin(obq.z), 1);
                    }
                    else {
                        // orthographic
                        nmc = vec3(obq.y, obq.z, 1);
                    }
                    // TODO: other projection
                    vec3 ndc = ndc_X_nmc * nmc;
                    gl_Position = vec4(ndc.xy, 0, ndc.z);
                }
            """, GL.GL_VERTEX_SHADER),
            shader.from_string("""
                #version 410
                
                out vec4 fragColor;
                
                void main() {
                    fragColor = vec4(0, 1, 0, 1);  // green
                }
            """, GL.GL_FRAGMENT_SHADER),
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

