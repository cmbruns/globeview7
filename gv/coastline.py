import pathlib

import numpy
from OpenGL import GL

from gv.vertex_buffer import VertexBuffer
from gv import shader
from shapefile import read_shape_file
from gv.layer import ILayer


class Coastline(ILayer):
    def __init__(self, name: str):
        super().__init__(name=name)
        self.start_indices = None
        self.vertex_counts = None
        self.vertices = None
        self.shader = None
        self.line_width = 1.0

    def initialize_opengl(self):
        polygons = []
        for gshhs in [
            1,  # L1: boundary between land and ocean, except Antarctica.
            2,  # L2: boundary between lake and land.
            #  3,  # L3: boundary between island-in-lake and lake.
            #  4,  # L4: boundary between pond-in-island and island.
            #  5, # L5: boundary between Antarctica ice and ocean.
            6,  # L6: boundary between Antarctica grounding-line and ocean.
        ]:
            polygons.extend(read_shape_file(f"{pathlib.Path.home()}/Downloads/gshhg-shp-2.3.7/GSHHS_shp/c/GSHHS_c_L{gshhs}.shp"))
        self.populate_data(polygons)
        self.vertices.bind()
        self.shader = shader.Program(
            shader.Stage(["coastline.vert", ], GL.GL_VERTEX_SHADER),
            shader.Stage(["coastline.geom", ], GL.GL_GEOMETRY_SHADER),
            shader.Stage(["coastline.frag", ], GL.GL_FRAGMENT_SHADER),
        ).compile()
        line_width_range = GL.glGetIntegerv(GL.GL_SMOOTH_LINE_WIDTH_RANGE)
        self.line_width = min(2, line_width_range[1])
        GL.glBindVertexArray(0)

    def populate_data(self, shapefile_polygons):
        vertices = []
        start_indices = []
        vertex_counts = []
        current_start_index = 0
        for polygon in shapefile_polygons:
            for ring in polygon:
                start_indices.append(current_start_index)
                nv = 0
                for vertex in ring:
                    # Hack to remove antarctica lines
                    if vertex[1] == -90:
                        # End this ring, start another
                        start_indices.append(current_start_index)
                        vertex_counts.append(nv)
                        current_start_index += nv
                        nv = 0
                        continue  # Discard all points exactly at the South Pole
                    vertices.append(vertex)
                    nv += 1
                current_start_index += nv
                vertex_counts.append(nv)
        self.start_indices = numpy.array(start_indices, dtype=numpy.int32)
        self.vertex_counts = numpy.array(vertex_counts, dtype=numpy.int32)
        self.vertices = VertexBuffer(vertices)

    def paint_opengl(self, context):
        if self.shader is None:
            self.initialize_opengl()
        self.vertices.bind()
        GL.glUseProgram(self.shader)
        GL.glLineWidth(self.line_width)  # Limited to 1.0 on Mac OS X
        GL.glMultiDrawArrays(GL.GL_LINE_STRIP, self.start_indices, self.vertex_counts, len(self.start_indices))
        # TODO: drive multiple equirect instances from CPU side
        # GL.glMultiDrawArraysIndirect(GL.GL_LINE_LOOP, indirect, draw_count, stride)
