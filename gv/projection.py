import abc
import enum
from math import cos, pi, radians, sin

import numpy
from OpenGL import GL
from OpenGL.GL.shaders import compileShader, compileProgram

from gv.frame import NMCPoint, OBQPoint, FramedPoint
from gv.vertex_buffer import VertexBuffer
from gv import shader


class Projection(enum.IntEnum):
    EQUIRECTANGULAR = 0
    ORTHOGRAPHIC = 1
    STEREOGRAPHIC = 2


class DisplayProjection(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def dobq_for_dnmc(dnmc, p_nmc: NMCPoint):
        pass

    def draw_boundary(self, context):
        pass

    def fill_boundary(self, context):
        pass

    # TODO: @property + @classmethod might not work in python 3.11
    @property
    @classmethod
    @abc.abstractmethod
    def index(cls):
        pass

    @staticmethod
    @abc.abstractmethod
    def is_valid_nmc(p_nmc: NMCPoint) -> bool:
        return True

    @staticmethod
    @abc.abstractmethod
    def obq_for_nmc(p_nmc: NMCPoint) -> OBQPoint:
        """
        Convert from normalized map coordinates to rotated geocentric coordinates.
        """
        pass


# TODO: maybe use instanced geometry for tiled copies of the world
class EquirectangularProjection(DisplayProjection):
    """
    Plate caree / Equirectangular / Geographic coordinates projection
    """

    @staticmethod
    def is_valid_nmc(p_nmc: NMCPoint) -> bool:
        if abs(p_nmc.y) > radians(90):
            return False
        return True

    index = Projection.EQUIRECTANGULAR

    def __init__(self):
        super().__init__()
        self.boundary_shader = None
        self.boundary_vertices = VertexBuffer([
            # Clockwise, like shapefiles
            # Normalized map coordinates
            # For use in triangle fans, it's important for the first vertex to be non-infinite.
            [0, -radians(90), 1],  # center of southern boundary
            [-1, 0, 0],  # west infinity
            [0, radians(90), 1],  # center of northern boundary
            [1, 0, 0],  # east infinity
        ])

    def initialize_gl(self):
        if self.boundary_shader is None:
            self.boundary_vertices.initialize_opengl()
            self.boundary_shader = compileProgram(
                shader.from_files(["projection.glsl", "boundary.vert"], GL.GL_VERTEX_SHADER),
                shader.from_files(["boundary.frag"], GL.GL_FRAGMENT_SHADER),
            )

    def draw_boundary(self, context):
        if self.boundary_shader is None:
            self.initialize_gl()
        self.boundary_vertices.bind()
        GL.glLineWidth(1)
        GL.glUseProgram(self.boundary_shader)
        GL.glDrawArrays(GL.GL_LINE_LOOP, 0, len(self.boundary_vertices))

    def fill_boundary(self, context):
        if self.boundary_shader is None:
            self.initialize_gl()
        self.boundary_vertices.bind()
        GL.glDrawArrays(GL.GL_TRIANGLE_FAN, 0, len(self.boundary_vertices))

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


class OrthographicProjection(DisplayProjection):
    index = Projection.ORTHOGRAPHIC

    def __init__(self):
        super().__init__()
        self.boundary_shader = None
        r = 1.0
        cverts = 100
        verts = [[r * sin(2 * i * pi / cverts), r * cos(2 * i * pi / cverts), 1] for i in range(cverts)]
        self.boundary_vertices = VertexBuffer(verts)

    def initialize_gl(self):
        if self.boundary_shader is not None:
            return
        self.boundary_vertices.initialize_opengl()
        self.boundary_shader = compileProgram(
            shader.from_files(["projection.glsl", "boundary.vert"], GL.GL_VERTEX_SHADER),
            shader.from_files(["boundary.frag"], GL.GL_FRAGMENT_SHADER),
        )

    def draw_boundary(self, context):
        if self.boundary_shader is None:
            self.initialize_gl()
        self.boundary_vertices.bind()
        GL.glLineWidth(1)
        GL.glUseProgram(self.boundary_shader)
        # GL.glPatchParameteri(GL.GL_PATCH_VERTICES, 2)  # TODO: more tessellation
        GL.glDrawArrays(GL.GL_LINE_LOOP, 0, len(self.boundary_vertices))

    def fill_boundary(self, context):
        if self.boundary_shader is None:
            self.initialize_gl()
        self.boundary_vertices.bind()
        GL.glDrawArrays(GL.GL_TRIANGLE_FAN, 0, len(self.boundary_vertices))

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
    def is_valid_nmc(p_nmc: NMCPoint) -> bool:
        if p_nmc.x**2 + p_nmc.y**2 > 1:
            return False
        return True

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


class StereographicProjection(DisplayProjection):
    index = Projection.STEREOGRAPHIC

    def __init__(self):
        super().__init__()

    def initialize_gl(self):
        pass

    def draw_boundary(self, context):
        pass

    @staticmethod
    def dobq_for_dnmc(dnmc, p_nmc: NMCPoint):
        x, y = p_nmc[:2]
        d = x**2 + y**2 + 4
        obq_J_prj = numpy.array([
            [-2 * x / d - 2 * x * (8 - d) / (d**2), -2 * y / d - 2 * y * (8 - d) / (d**2)],
            [4 / d - 8 * x**2 / (d**2), -8 * x * y / d**2],
            [-8 * x * y / (d**2), 4 / d - 8 * y**2 / (d**2)]], dtype=numpy.float)
        return obq_J_prj @ dnmc

    @staticmethod
    def is_valid_nmc(p_nmc: NMCPoint) -> bool:
        return True

    @staticmethod
    def obq_for_nmc(p_nmc: NMCPoint) -> OBQPoint:
        x, y = p_nmc[:2]
        d = x**2 + y**2 + 4.0
        result = OBQPoint((
            (8.0 - d) / d,
            4.0 * x / d,
            4.0 * y / d,
        ))
        return result

