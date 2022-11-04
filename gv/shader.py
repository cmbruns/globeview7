import pkg_resources
import re
import sys
import traceback
import types

from OpenGL import GL
from OpenGL.GL.shaders import compileShader, compileProgram, ShaderCompilationError


class Stage(object):
    def __init__(self, file_names: list, stage: int) -> None:
        self.initial_file_names = ["version.glsl", *file_names]
        self.stage = stage
        self.all_file_names = self._process_includes()
        self.full_file_names = [pkg_resources.resource_filename('gv.glsl', f) for f in self.all_file_names]
        self.strings = [Stage.string_from_file(f, i) for i, f in enumerate(self.all_file_names)]
        self.value = -1

    def __int__(self):
        return int(self.value)

    def compile(self):
        try:
            self.value = compileShader("\n".join(self.strings), self.stage)
        except ShaderCompilationError as e:
            try:
                # Try to append the glsl shader source line to the stack trace
                # ('Shader compile failure (0): b\'0(3) : error C0000: syntax error, unexpected \\\';\\\', expecting...
                msg = str(e)
                match = re.search(r"Shader compile failure \((\d+)\): b\\'(\d+)\((\d+)\)", msg)
                if match:
                    lineno = int(match.group(3))
                    filename = self.full_file_names[int(match.group(2))]
                    te = traceback.TracebackException.from_exception(e)
                    fs = traceback.FrameSummary(filename=filename, lineno=lineno, name="shader")
                    te.stack.append(fs)
                    # TODO: get this frame into the actual exception traceback
                    print(f'Traceback (most recent call last)\n{"".join(te.stack.format())}', file=sys.stderr)
            except Exception as e2:
                print(e2)
            raise e
        return self

    def _process_includes(self) -> list:
        """Parse '#pragma include ...' directives"""
        result = []
        for f in self.initial_file_names:
            s = Stage.string_from_file(f, 0)  # zero index because string not used for code here
            m = re.findall(r'^\s*#pragma include\s+"?([^"\s]+)', s, re.MULTILINE)
            if m:
                for inc in m:
                    if inc not in result:
                        result.append(inc)
            if f not in result:
                result.append(f)
        return result

    @staticmethod
    def string_from_file(file_name: str, file_index: int) -> str:
        string = pkg_resources.resource_string("gv.glsl", file_name).decode()
        if not string.startswith("#version"):
            string = f"#line 1 {file_index}\n{string}"
        return string


class Program(object):
    def __init__(self, *stages):
        self.stages = stages
        self.value = -1

    def __int__(self):
        return int(self.value)

    def compile(self, validate=True):
        self.value = compileProgram(*[s.compile().value for s in self.stages], validate=validate)
        # Uniform buffer binding needed for OpenGL 4.1
        ub_index = GL.glGetUniformBlockIndex(self.value, "TransformBlock")
        if ub_index != GL.GL_INVALID_INDEX:
            GL.glUniformBlockBinding(self.value, ub_index, 2)
        return self
