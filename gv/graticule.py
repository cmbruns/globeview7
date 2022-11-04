import numpy
from OpenGL import GL

import gv.layer
from gv.layer import ILayer
from gv import shader
from gv.vertex_buffer import VertexBuffer


class Graticule(gv.layer.ILayerGL):
    def __init__(self, name: str):
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
        n_segs = 100
        interval = 10  # Draw a grid line every X degrees
        assert 90 % interval == 0
        for lat in range(-90 + interval, 90, interval):  # TODO: more parallels
            start_indices.append(current_start_index)
            polygon = []
            for segment in range(n_segs):
                polygon.append([360 * segment / (n_segs - 1), lat])
            current_start_index += len(polygon)
            vertex_counts.append(len(polygon))
            polygons.extend(polygon)
        # Meridians
        for lon in range(0, 360, interval):
            start_indices.append(current_start_index)
            polygon = []
            for segment in range(n_segs):
                polygon.append([lon, -90 + interval + (180 - 2 * interval) * segment / (n_segs - 1)])
            current_start_index += len(polygon)
            vertex_counts.append(len(polygon))
            polygons.extend(polygon)
        # Draw a cross at the North Pole
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
        # South Pole
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
        self.shader = shader.Program(
            shader.Stage(["coastline.vert", ], GL.GL_VERTEX_SHADER),
            shader.Stage(["coastline.geom", ], GL.GL_GEOMETRY_SHADER),
            shader.Stage(["coastline.frag", ], GL.GL_FRAGMENT_SHADER),
        ).compile()
        GL.glBindVertexArray(0)

    def paint_opengl(self, context):
        if self.shader is None:
            self.initialize_opengl()
        self.vertices.bind()
        GL.glUseProgram(self.shader)
        GL.glLineWidth(1)
        GL.glMultiDrawArrays(GL.GL_LINE_STRIP, self.start_indices, self.vertex_counts, len(self.start_indices))
