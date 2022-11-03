import pkg_resources
import re

from OpenGL.GL.shaders import compileShader, compileProgram


class Stage(object):
    def __init__(self, file_names: list, stage: int) -> None:
        self.initial_file_names = ["version.glsl", *file_names]
        self.stage = stage
        self.all_file_names = self._process_includes()
        self.strings = [Stage.string_from_file(f, i) for i, f in enumerate(self.all_file_names)]
        self.value = -1

    def __int__(self):
        return int(self.value)

    def compile(self):
        self.value = compileShader("\n".join(self.strings), self.stage)
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
        return self
