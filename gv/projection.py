import abc
import enum
from math import cos, pi, radians, sin

import numpy
from OpenGL import GL

from gv.frame import NMCPoint, OBQPoint
from gv.vertex_buffer import VertexBuffer
from gv import shader


class Projection(enum.IntEnum):
    # Keep these values in sync with projection.glsl and projectionComboBox
    PERSPECTIVE = 0
    ORTHOGRAPHIC = 1
    AZIMUTHAL_EQUAL_AREA = 2
    EQUIRECTANGULAR = 3
    AZIMUTHAL_EQUIDISTANT = 4
    STEREOGRAPHIC = 5
    GNOMONIC = 6


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
    # noinspection PyPropertyDefinition
    @classmethod
    @property
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


class AzimuthalEqualAreaProjection(DisplayProjection):
    index = Projection.AZIMUTHAL_EQUAL_AREA

    def __init__(self):
        super().__init__()
        self.boundary_shader = None
        r = 2
        c_verts = 100
        verts = [[r * sin(2 * i * pi / c_verts), r * cos(2 * i * pi / c_verts), 1] for i in range(c_verts)]
        self.boundary_vertices = VertexBuffer(verts)

    def initialize_gl(self):
        if self.boundary_shader is not None:
            return
        self.boundary_vertices.bind()
        self.boundary_shader = shader.Program(
            shader.Stage(["projection.glsl", "boundary.vert"], GL.GL_VERTEX_SHADER),
            shader.Stage(["boundary.frag"], GL.GL_FRAGMENT_SHADER),
        ).compile(validate=True)
        GL.glBindVertexArray(0)

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
        x, y = p_nmc[:2]
        d = (1 - (x**2 - y**2) / 4)**0.5
        d4 = d * 4
        # noinspection PyPep8Naming
        obq_J_prj = numpy.array([
            [-x, -y],
            [d - x**2 / d4, -x * y / d4],
            [-x * y / d4, d - y**2 / d4],
        ], dtype=numpy.float)
        result = obq_J_prj @ dnmc
        return result

    @staticmethod
    def is_valid_nmc(p_nmc: NMCPoint) -> bool:
        x, y = p_nmc[0] / p_nmc[2], p_nmc[1] / p_nmc[2]
        r2 = x**2 + y**2
        return r2 < 4

    @staticmethod
    def obq_for_nmc(p_nmc: NMCPoint) -> OBQPoint:
        x, y = p_nmc[:2]
        d1 = (x**2 + y**2) / 2
        d2 = (1 - d1 / 2)**0.5
        result = OBQPoint((
            1 - d1,
            x * d2,
            y * d2,
        ))
        return result


class AzimuthalEquidistantProjection(DisplayProjection):
    index = Projection.AZIMUTHAL_EQUIDISTANT

    def __init__(self):
        super().__init__()
        self.boundary_shader = None
        r = radians(180)
        c_verts = 100
        verts = [[r * sin(2 * i * pi / c_verts), r * cos(2 * i * pi / c_verts), 1] for i in range(c_verts)]
        self.boundary_vertices = VertexBuffer(verts)

    def initialize_gl(self):
        if self.boundary_shader is not None:
            return
        self.boundary_vertices.bind()
        self.boundary_shader = shader.Program(
            shader.Stage(["projection.glsl", "boundary.vert"], GL.GL_VERTEX_SHADER),
            shader.Stage(["boundary.frag"], GL.GL_FRAGMENT_SHADER),
        ).compile(validate=True)
        GL.glBindVertexArray(0)

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
        x, y = p_nmc[0] / p_nmc[2], p_nmc[1] / p_nmc[2]
        d2 = x**2 + y**2
        d = d2**0.5
        d32 = d2 * d
        sd = sin(d)
        cd = cos(d)
        # noinspection PyPep8Naming
        obq_J_prj = numpy.array([
            [-x * sd / d, -y * sd / d],
            [x**2 * cd / d2 - x**2 * sd / d32 + sd / d, x * y * cd / d2 - x * y * sd / d32],
            [x * y * cd / d2 - x * y * sd / d32, y**2 * cd / d2 - y**2 * sd / d32 + sd / d],
        ], dtype=numpy.float)
        result = obq_J_prj @ dnmc
        return result

    @staticmethod
    def is_valid_nmc(p_nmc: NMCPoint) -> bool:
        x, y = p_nmc[0] / p_nmc[2], p_nmc[1] / p_nmc[2]
        r2 = x**2 + y**2
        return r2 < radians(180)**2

    @staticmethod
    def obq_for_nmc(p_nmc: NMCPoint) -> OBQPoint:
        x, y = p_nmc[0] / p_nmc[2], p_nmc[1] / p_nmc[2]
        d = (x**2 + y**2)**0.5
        sdd = sin(d) / d
        result = OBQPoint((
            cos(d),
            x * sdd,
            y * sdd,
        ))
        return result


# TODO: maybe use instanced geometry for tiled copies of the world
class EquirectangularProjection(DisplayProjection):
    """
    Plate Carrée / Equirectangular / Geographic coordinates projection
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
        self.boundary_vertices.bind()
        self.boundary_shader = shader.Program(
            shader.Stage(["projection.glsl", "boundary.vert"], GL.GL_VERTEX_SHADER),
            shader.Stage(["boundary.frag"], GL.GL_FRAGMENT_SHADER),
        ).compile(validate=True)
        GL.glBindVertexArray(0)

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
        # noinspection PyPep8Naming
        obq_J_wgs84prj = numpy.array([
            [-s0 * c1, -c0 * s1],
            [c0 * c1, -s0 * s1],
            [0, c1]], dtype=numpy.float)
        dwgs84prj = dnmc  # Radians are normalized units
        result = obq_J_wgs84prj @ dwgs84prj
        return result


class GnomonicProjection(DisplayProjection):
    index = Projection.GNOMONIC

    def __init__(self):
        super().__init__()
        self.boundary_vertices = VertexBuffer([
            # Infinity NMC (clips to full screen quad)
            [0, 0, 1],  # center of screen
            [-1, +1, 0],  # upper left infinity
            [+1, +1, 0],  # upper right infinity
            [+1, -1, 0],  # lower right infinity
            [-1, -1, 0],  # lower left infinity
            [-1, +1, 0],  # upper left infinity
        ])

    def initialize_gl(self):
        self.boundary_vertices.initialize_opengl()

    def draw_boundary(self, context):
        pass

    def fill_boundary(self, context):
        self.boundary_vertices.bind()
        GL.glDrawArrays(GL.GL_TRIANGLE_FAN, 0, len(self.boundary_vertices))

    @staticmethod
    def dobq_for_dnmc(dnmc, p_nmc: NMCPoint):
        x, y = p_nmc[:2]
        d = (x**2 + y**2 + 1.0) ** 0.5
        d3 = d**3
        # noinspection PyPep8Naming
        obq_J_prj = numpy.array([
            [-x / d3, -y / d3],
            [-x**2 / d3 + 1 / d, -x * y / d3],
            [-x * y / d3, -y**2 / d3 + 1 / d]], dtype=numpy.float)
        result = obq_J_prj @ dnmc
        return result

    @staticmethod
    def is_valid_nmc(p_nmc: NMCPoint) -> bool:
        return True

    @staticmethod
    def obq_for_nmc(p_nmc: NMCPoint) -> OBQPoint:
        x, y = p_nmc[:2]
        oy = 1.0 / ((x**2 + y**2 + 1.0) ** 0.5)
        result = OBQPoint((
            oy,
            x * oy,
            y * oy,
        ))
        return result


class OrthographicProjection(DisplayProjection):
    index = Projection.ORTHOGRAPHIC

    def __init__(self):
        super().__init__()
        self.boundary_shader = None
        r = 1.0
        c_verts = 100
        verts = [[r * sin(2 * i * pi / c_verts), r * cos(2 * i * pi / c_verts), 1] for i in range(c_verts)]
        self.boundary_vertices = VertexBuffer(verts)

    def initialize_gl(self):
        if self.boundary_shader is not None:
            return
        self.boundary_vertices.bind()
        self.boundary_shader = shader.Program(
            shader.Stage(["projection.glsl", "boundary.vert"], GL.GL_VERTEX_SHADER),
            shader.Stage(["boundary.frag"], GL.GL_FRAGMENT_SHADER),
        ).compile(validate=True)
        GL.glBindVertexArray(0)

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
        # noinspection PyPep8Naming
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


class PerspectiveProjection(DisplayProjection):
    index = Projection.PERSPECTIVE

    def __init__(self, view_state: "ViewState"):
        super().__init__()
        self.view_state = view_state
        self.boundary_shader = None
        c_verts = 100
        # Use unit radius, then scale the boundary in the shader
        verts = [[sin(2 * i * pi / c_verts), cos(2 * i * pi / c_verts), 1] for i in range(c_verts)]
        self.boundary_vertices = VertexBuffer(verts)

    def initialize_gl(self):
        if self.boundary_shader is not None:
            return
        self.boundary_vertices.bind()
        self.boundary_shader = shader.Program(
            shader.Stage(["projection.glsl", "boundary_psp.vert"], GL.GL_VERTEX_SHADER),
            shader.Stage(["boundary.frag"], GL.GL_FRAGMENT_SHADER),
        ).compile(validate=True)
        GL.glBindVertexArray(0)

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

    def dobq_for_dnmc(self, dnmc, p_nmc: NMCPoint):
        # TODO: this is wrong, it's copied from orthographic
        p_prj = p_nmc  # Radians are normalized units
        x, y = p_prj[:2]

        v = self.view_state.altitude
        max_r2 = v / (2 + v)
        r2 = x**2 + y**2  # screen space radius squared
        if r2 > max_r2:
            raise RuntimeError("invalid location")

        # This Jacobian is very complex, so we are assigning variables to repeated terms here,
        # to keep each source line shorter
        rt2 = r2 + v**2  # r2 and orthogonal view distance
        sr = (v * (v - (v + 2) * r2))**0.5  # frequent term involving square root
        dn1 = rt2 ** 2 * sr  # denominator in many Jacobian terms
        k1 = sr * (v * sr + v * r2 + r2)  # another recurring term
        xc = (-2 * k1 + (-v ** 2 * (v + 2) + 2 * sr * (v + 1)) * rt2) / dn1  # coefficient for dobq_x terms
        dn2 = v * dn1
        d20 = x * y * (2 * k1 + (v ** 2 * (v + 2) - 2 * sr * (v + 1)) * rt2) / dn2
        yzc1 = 2 * k1 + (v ** 2 * (v + 2) - 2 * sr * (v + 1)) * (v ** 2 + r2)  # coefficient for x**2 or y**2
        yzc2 = sr * rt2 * (-v * sr - v * r2 - r2 + (v + 1) * rt2)
        d10 = (x**2 * yzc1 + yzc2) / dn2
        d21 = (y**2 * yzc1 + yzc2) / dn2

        # noinspection PyPep8Naming
        obq_J_prj = numpy.array([
            [x * xc, y * xc],
            [d10, d20],
            [d20, d21]], dtype=numpy.float)
        dprj = dnmc  # Radians are normalized units
        result = obq_J_prj @ dprj
        return result

    def is_valid_nmc(self, p_nmc: NMCPoint) -> bool:
        v = self.view_state.altitude
        r2 = v / (2 + v)
        if p_nmc.x**2 + p_nmc.y**2 >= r2:
            return False
        return True

    def obq_for_nmc(self, p_nmc: NMCPoint) -> OBQPoint:
        x, y = p_nmc[:2]
        v = self.view_state.altitude
        r2 = x**2 + y**2
        ox = (v * (v**2 - v * (v + 2) * r2)**0.5 + v * r2 + r2) / (v**2 + r2)
        result = OBQPoint((
            ox,
            x * (v + 1 - ox) / v,
            y * (v + 1 - ox) / v,
        ))
        return result


class StereographicProjection(DisplayProjection):
    index = Projection.STEREOGRAPHIC

    def __init__(self):
        super().__init__()
        self.boundary_vertices = VertexBuffer([
            # Infinity NMC (clips to full screen quad)
            [0, 0, 1],  # center of screen
            [-1, +1, 0],  # upper left infinity
            [+1, +1, 0],  # upper right infinity
            [+1, -1, 0],  # lower right infinity
            [-1, -1, 0],  # lower left infinity
            [-1, +1, 0],  # upper left infinity
        ])

    def initialize_gl(self):
        self.boundary_vertices.initialize_opengl()

    def draw_boundary(self, context):
        pass

    def fill_boundary(self, context):
        self.boundary_vertices.bind()
        GL.glDrawArrays(GL.GL_TRIANGLE_FAN, 0, len(self.boundary_vertices))

    @staticmethod
    def dobq_for_dnmc(dnmc, p_nmc: NMCPoint):
        x, y = p_nmc[:2]
        d = x**2 + y**2 + 4
        # noinspection PyPep8Naming
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


_projection_for_index = {
    Projection.AZIMUTHAL_EQUAL_AREA: AzimuthalEqualAreaProjection,
    Projection.AZIMUTHAL_EQUIDISTANT: AzimuthalEquidistantProjection,
    Projection.EQUIRECTANGULAR: EquirectangularProjection,
    Projection.GNOMONIC: GnomonicProjection,
    Projection.ORTHOGRAPHIC: OrthographicProjection,
    Projection.PERSPECTIVE: PerspectiveProjection,
    Projection.STEREOGRAPHIC: StereographicProjection,
}


def projection_for_enum(projection: Projection) -> type:
    return _projection_for_index[projection]
