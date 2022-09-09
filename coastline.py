import inspect

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
        self.shader = compileProgram(
            compileShader(
                inspect.cleandoc("""
                    #version 430
                    
                    in vec2 in_pos;

                    layout(location = 1) uniform mat3 ndc_X_nmc = mat3(1);
                    layout(location = 2) uniform mat3 ecef_X_ecef1 = mat3(1);

                    void main() {
                        vec2 wgs = radians(in_pos);
                        vec3 gcs = vec3(
                            cos(wgs.x) * cos(wgs.y),
                            sin(wgs.x) * cos(wgs.y),
                            sin(wgs.y)
                        );
                        vec3 gcs2 = ecef_X_ecef1 * gcs;
                        vec2 wgs2 = vec2(
                            atan(gcs2.y, gcs2.x),
                            asin(gcs2.z)
                        );
                        
                        vec3 nmc = vec3(wgs2 / radians(90), 1);
                        vec3 ndc = ndc_X_nmc * nmc;
                        gl_Position = vec4(ndc.xy, 0, 1);
                    }
                """),
                GL.GL_VERTEX_SHADER),
            compileShader(
                inspect.cleandoc("""
                    #version 430

                    out vec4 fragColor;
                    
                    void main() {
                        // fragColor = vec4(0.012, 0.325, 0.517, 1);
                        fragColor = vec4(0.03, 0.34, 0.60, 1);
                    }
                """),
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
        print(self.start_indices, self.vertex_counts)

    def paint_opengl(self, context):
        GL.glBindVertexArray(self.vao)
        GL.glUseProgram(self.shader)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glEnable(GL.GL_BLEND)
        GL.glEnable(GL.GL_LINE_SMOOTH)
        GL.glLineWidth(2)
        GL.glUniformMatrix3fv(1, 1, True, context.ndc_X_nmc)
        GL.glUniformMatrix3fv(2, 1, False, context.ecef1_X_ecef)  # transpose is inverse
        GL.glMultiDrawArrays(GL.GL_LINE_LOOP, self.start_indices, self.vertex_counts, len(self.start_indices))
        GL.glBindVertexArray(0)
