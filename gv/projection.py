import abc
import enum
import inspect
from math import cos, pi, radians, sin

import numpy
from OpenGL import GL
from OpenGL.GL.shaders import compileShader, compileProgram

from gv.frame import NMCPoint, OBQPoint, FramedPoint


class Projection(enum.IntEnum):
     EQUIRECTANGULAR = 0
     ORTHOGRAPHIC = 1


class DisplayProjection(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def dobq_for_dnmc(dnmc, p_nmc: NMCPoint):
        pass

    def draw_boundary(self, context):
        pass

    @staticmethod
    @abc.abstractmethod
    def obq_for_nmc(p_nmc: NMCPoint) -> OBQPoint:
        """
        Convert from normalized map coordinates to rotated geocentric coordinates.
        """
        pass

    @property
    @classmethod
    @abc.abstractmethod
    def index(cls):
        pass


class OrthographicProjection(DisplayProjection):
    index = Projection.ORTHOGRAPHIC

    def __init__(self):
        super().__init__()
        self.boundary_vao = None
        self.boundary_vbo = None
        self.boundary_shader = None
        r = 1.0
        cverts = 100
        verts = [[r * sin(2 * i * pi / cverts), r * cos(2 * i * pi / cverts), 1] for i in range(cverts)]
        self.boundary_vertices = numpy.array(verts, dtype=numpy.float32)

    def draw_boundary(self, context):
        if self.boundary_vao is None:
            self.boundary_vao = GL.glGenVertexArrays(1)
            GL.glBindVertexArray(self.boundary_vao)
            self.boundary_vbo = GL.glGenBuffers(1)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.boundary_vbo)
            GL.glBufferData(GL.GL_ARRAY_BUFFER, self.boundary_vertices, GL.GL_STATIC_DRAW)
            GL.glEnableVertexAttribArray(0)
            GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, 0, None)
            self.boundary_shader = compileProgram(
                compileShader(inspect.cleandoc("""
                    #version 430

                    in vec3 nmc;
                    layout(location = 1) uniform mat3 ndc_X_nmc = mat3(1);

                    void main() {
                        vec3 ndc = ndc_X_nmc * nmc;
                        gl_Position = vec4(ndc.xy, 0, ndc.z);
                    }
                """), GL.GL_VERTEX_SHADER),
                compileShader(inspect.cleandoc("""
                    #version 430

                    out vec4 fragColor;

                    void main() {
                        // TODO: share line color
                        fragColor = vec4(0.03, 0.34, 0.60, 1);
                    }
                """), GL.GL_FRAGMENT_SHADER),
            )
        GL.glBindVertexArray(self.boundary_vao)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glEnable(GL.GL_BLEND)
        GL.glEnable(GL.GL_LINE_SMOOTH)
        GL.glLineWidth(2)
        GL.glUseProgram(self.boundary_shader)
        GL.glUniformMatrix3fv(1, 1, True, context.ndc_X_nmc)
        GL.glPatchParameteri(GL.GL_PATCH_VERTICES, 2)
        GL.glDrawArrays(GL.GL_LINE_LOOP, 0, len(self.boundary_vertices))
        GL.glBindVertexArray(0)

    @staticmethod
    def dobq_for_dnmc(dnmc, p_nmc: NMCPoint):
        p_prj = p_nmc  # Radians are normalized units
        x, y = p_prj[:2]
        if x**2 + y**2 > 1:
            raise RuntimeError("invalid location")
        denom = (1 - x**2 - y**2)**0.5
        obq_J_prj = numpy.array([
            [-x / denom, -y / denom],
            [1, 0],
            [0, 1]], dtype=numpy.float)
        dprj = dnmc  # Radians are normalized units
        result = obq_J_prj @ dprj
        return result

    @staticmethod
    def obq_for_nmc(p_nmc: NMCPoint) -> OBQPoint:
        p_prj = p_nmc  # Radians from normalized units
        x, y = p_prj[:2]
        result = OBQPoint((
            (1 - x**2 - y**2)**0.5,
            x,
            y,
        ))
        return result


# TODO: maybe use instanced geometry for tiled copies of the world
class WGS84Projection(DisplayProjection):
    """
    Plate caree / Equirectangular / Geographic coordinates projection
    """
    index = Projection.EQUIRECTANGULAR

    def __init__(self):
        super().__init__()
        self.boundary_vao = None
        self.boundary_vbo = None
        self.boundary_shader = None
        self.boundary_vertices = numpy.array([
            # Clockwise, like shapefiles
            # Normalized map coordinates
            [-1, 0, 0],  # left infinity
            [0, radians(90), 1],  # top
            [1, 0, 0],  # right infinity
            [0, radians(-90), 1],  # bottom
        ],
        dtype=numpy.float32)

    def draw_boundary(self, context):
        if self.boundary_vao is None:
            self.boundary_vao = GL.glGenVertexArrays(1)
            GL.glBindVertexArray(self.boundary_vao)
            self.boundary_vbo = GL.glGenBuffers(1)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.boundary_vbo)
            GL.glBufferData(GL.GL_ARRAY_BUFFER, self.boundary_vertices, GL.GL_STATIC_DRAW)
            GL.glEnableVertexAttribArray(0)
            GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, 0, None)
            self.boundary_shader = compileProgram(
                compileShader(inspect.cleandoc("""
                    #version 430
                    
                    in vec3 nmc;
                    layout(location = 1) uniform mat3 ndc_X_nmc = mat3(1);
                             
                    void main() {
                        vec3 ndc = ndc_X_nmc * nmc;
                        gl_Position = vec4(ndc.xy, 0, ndc.z);
                    }
                """), GL.GL_VERTEX_SHADER),
                compileShader(inspect.cleandoc("""
                    #version 430
                    
                    out vec4 fragColor;
                                       
                    void main() {
                        // TODO: share line color
                        fragColor = vec4(0.03, 0.34, 0.60, 1);
                    }
                """), GL.GL_FRAGMENT_SHADER),
            )
        GL.glBindVertexArray(self.boundary_vao)
        # TODO: common gl state for all?
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glEnable(GL.GL_BLEND)
        GL.glEnable(GL.GL_LINE_SMOOTH)
        GL.glLineWidth(2)
        GL.glUseProgram(self.boundary_shader)
        GL.glUniformMatrix3fv(1, 1, True, context.ndc_X_nmc)
        GL.glDrawArrays(GL.GL_LINE_LOOP, 0, len(self.boundary_vertices))
        GL.glBindVertexArray(0)

    @staticmethod
    def obq_for_nmc(p_nmc: NMCPoint) -> OBQPoint:
        p_prj = p_nmc  # Radians from normalized units
        result = OBQPoint((
            cos(p_prj[0]) * cos(p_prj[1]),
            sin(p_prj[0]) * cos(p_prj[1]),
            sin(p_prj[1]),
        ))
        return result

    @staticmethod
    def dobq_for_dnmc(dnmc, p_nmc: NMCPoint):
        p_prj = p_nmc  # Radians are normalized units
        if abs(p_prj[1]) > radians(90):
            raise RuntimeError
        c0 = cos(p_prj[0])
        s0 = sin(p_prj[0])
        c1 = cos(p_prj[1])
        s1 = sin(p_prj[1])
        obq_J_wgs84prj = numpy.array([
            [-s0 * c1, -c0 * s1],
            [c0 * c1, -s0 * s1],
            [0, c1]], dtype=numpy.float)
        dwgs84prj = dnmc  # Radians are normalized units
        result = obq_J_wgs84prj @ dwgs84prj
        return result
