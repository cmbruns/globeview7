import inspect
import pkg_resources

import numpy
from OpenGL import GL
from OpenGL.GL.shaders import compileShader, compileProgram

from shapefile import read_shape_file


class Coastline(object):
    def __init__(self):
        self.start_indices = None
        self.vertex_counts = None
        self.vertices = None
        self.vao = None
        self.vbo = None
        self.shader = None

    def initialize_opengl(self):
        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)
        #
        polygons = []
        for gshhs in [
            1,  # L1: boundary between land and ocean, except Antarctica.
            2,  # L2: boundary between lake and land.
            #  3,  # L3: boundary between island-in-lake and lake.
            #  4,  # L4: boundary between pond-in-island and island.
            #  5, # L5: boundary between Antarctica ice and ocean.
            6,  # L6: boundary between Antarctica grounding-line and ocean.
        ]:
            polygons.extend(read_shape_file(f"C:/Users/cmbruns/Downloads/gshhg-shp-2.3.7/GSHHS_shp/c/GSHHS_c_L{gshhs}.shp"))
        self.populate_data(polygons)
        #
        self.vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.vertices, GL.GL_STATIC_DRAW)
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, 2, GL.GL_FLOAT, False, 0, None)
        #
        vertex_source = "\n".join([pkg_resources.resource_string("gv.glsl", f).decode() for f in [
            "version.glsl",
            "coastline.vert",
        ]])
        self.shader = compileProgram(
            compileShader(
                "\n".join([pkg_resources.resource_string("gv.glsl", f).decode() for f in [
                    "version.glsl",
                    "coastline.vert",
                ]]),
                GL.GL_VERTEX_SHADER),
            compileShader(
                "\n".join([pkg_resources.resource_string("gv.glsl", f).decode() for f in [
                    "version.glsl",
                    "coastline.geom",
                ]]),
                GL.GL_GEOMETRY_SHADER),
            compileShader(
                "\n".join([pkg_resources.resource_string("gv.glsl", f).decode() for f in [
                    "version.glsl",
                    "coastline.frag",
                ]]),
                GL.GL_FRAGMENT_SHADER),
        )
        GL.glBindVertexArray(0)

    def populate_data(self, shapefile_polygons):
        vertices = []
        start_indices = []
        vertex_counts = []
        current_start_index = 0
        for polygon in shapefile_polygons:
            for ring in polygon:
                start_indices.append(current_start_index)
                current_start_index += len(ring)
                vertex_counts.append(len(ring))
                for vertex in ring:
                    vertices.append(vertex)
        self.start_indices = numpy.array(start_indices, dtype=numpy.int32)
        self.vertex_counts = numpy.array(vertex_counts, dtype=numpy.int32)
        self.vertices = numpy.array(vertices, dtype=numpy.float32).flatten()

    def paint_opengl(self, context):
        GL.glBindVertexArray(self.vao)
        GL.glUseProgram(self.shader)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glEnable(GL.GL_BLEND)
        GL.glEnable(GL.GL_LINE_SMOOTH)
        GL.glLineWidth(2)
        GL.glUniformMatrix3fv(1, 1, True, context.ndc_X_nmc)
        GL.glUniformMatrix3fv(2, 1, False, context.ecf_X_obq)  # transpose is inverse
        GL.glMultiDrawArrays(GL.GL_LINE_LOOP, self.start_indices, self.vertex_counts, len(self.start_indices))
        GL.glBindVertexArray(0)
