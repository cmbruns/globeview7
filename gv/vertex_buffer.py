from ctypes import cast, c_void_p

import numpy
from OpenGL import GL


class VertexBuffer(object):
    def __init__(self, *args):
        self.vao = None
        self.vbo = None
        n_attributes = len(args)
        assert n_attributes > 0
        self.vertex_count = len(args[0])
        for a in args:
            assert len(a) == self.vertex_count
        self.element_counts = []
        for a in args:
            ec = 0
            if len(a) > 0:
                ec = len(a[0])
            self.element_counts.append(ec)
        zippered = []
        for i in range(self.vertex_count):
            zippered.append([a[i] for a in args])
        self.vertices = numpy.array(zippered, dtype=numpy.float32).flatten()

    def __len__(self):
        return self.vertex_count

    def bind(self):
        if self.vao is None:
            self.initialize_opengl()
        GL.glBindVertexArray(self.vao)

    def initialize_opengl(self):
        if self.vao is None:
            self.vao = GL.glGenVertexArrays(1)
            GL.glBindVertexArray(self.vao)
            self.vbo = GL.glGenBuffers(1)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
            GL.glBufferData(GL.GL_ARRAY_BUFFER, self.vertices, GL.GL_STATIC_DRAW)
            stride = 4 * sum(self.element_counts)
            offset = 0
            for i, ec in enumerate(self.element_counts):
                GL.glEnableVertexAttribArray(i)
                if ec > 0:
                    GL.glVertexAttribPointer(i, ec, GL.GL_FLOAT, False, stride, cast(offset, c_void_p))
                offset += 4 * ec
            GL.glBindVertexArray(0)
