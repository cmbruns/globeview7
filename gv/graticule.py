import numpy
from OpenGL import GL
from OpenGL.GL.shaders import compileProgram

from gv.layer import ILayer
from gv import shader
from gv.vertex_buffer import VertexBuffer


class Graticule(ILayer):
    def __init__(self, name:str):
        super().__init__(name=name)
        self.shader = None
        self.vertices = None
        self.start_indices = None
        self.vertex_counts = None

    def initialize_opengl(self):
        if self.shader is not None:
            return
        polygons = []
        start_indices = []
        vertex_counts = []
        current_start_index = 0
        # Parallels
        nsegs = 100
        interval = 10  # Draw a grid line every X degrees
        assert 90 % interval == 0
        for lat in range(-90 + interval, 90, interval):  # TODO: more parallels
            start_indices.append(current_start_index)
            polygon = []
            for segment in range(nsegs):
                polygon.append([360 * segment / (nsegs - 1), lat])
            current_start_index += len(polygon)
            vertex_counts.append(len(polygon))
            polygons.extend(polygon)
        # Meridians
        for lon in range(0, 360, interval):
            start_indices.append(current_start_index)
            polygon = []
            for segment in range(nsegs):
                polygon.append([lon, -90 + interval + (180 - 2 * interval) * segment / (nsegs - 1)])
            current_start_index += len(polygon)
            vertex_counts.append(len(polygon))
            polygons.extend(polygon)
        # Draw a cross at the North pole
        dn = interval / 6  # Size of cross / 2
        n0 = 90 - dn  # starting latitude
        for lon in [0, 90, 180, 270]:  # four spokes of polar cross
            start_indices.append(current_start_index)
            polygon = []
            for seg in range(10):
                polygon.append([lon, n0 + dn * seg / 9])
            current_start_index += len(polygon)
            vertex_counts.append(len(polygon))
            polygons.extend(polygon)
        # South pole
        n0 = -90 + dn
        for lon in [0, 90, 180, 270]:
            start_indices.append(current_start_index)
            polygon = []
            for seg in range(10):
                polygon.append([lon, n0 - dn * seg / 9])
            current_start_index += len(polygon)
            vertex_counts.append(len(polygon))
            polygons.extend(polygon)
        self.start_indices = numpy.array(start_indices, dtype=numpy.int32)
        self.vertex_counts = numpy.array(vertex_counts, dtype=numpy.int32)
        self.vertices = VertexBuffer(polygons)
        self.vertices.bind()
        self.shader = compileProgram(
            shader.from_files(["coastline.vert", ], GL.GL_VERTEX_SHADER),
            shader.from_files(["projection.glsl", "coastline.geom", ], GL.GL_GEOMETRY_SHADER),
            shader.from_files(["coastline.frag", ], GL.GL_FRAGMENT_SHADER),
        )
        ub_index = GL.glGetUniformBlockIndex(self.shader, "TransformBlock")
        GL.glUniformBlockBinding(self.shader, ub_index, 2)
        GL.glBindVertexArray(0)

    def paint_opengl(self, context):
        if self.shader is None:
            self.initialize_opengl()
        self.vertices.bind()
        GL.glUseProgram(self.shader)
        GL.glLineWidth(1)
        GL.glMultiDrawArrays(GL.GL_LINE_STRIP, self.start_indices, self.vertex_counts, len(self.start_indices))
