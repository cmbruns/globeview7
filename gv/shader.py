import inspect
import pkg_resources
import re

from OpenGL.GL.shaders import compileShader, compileProgram


class Shader(object):
    pass


def string_from_file(file_name) -> str:
    string = pkg_resources.resource_string("gv.glsl", file_name).decode()
    return string


def _process_includes(file_names: list) -> list:
    """Parse '#pragma include ...' directives"""
    result = []
    for f in file_names:
        s = string_from_file(f)
        m = re.findall(r'^\s*#pragma include\s+"?([^"\s]+)', s, re.MULTILINE)
        if m:
            for inc in m:
                if inc not in result:
                    result.append(inc)
        if f not in result:
            result.append(f)
    return result


def from_files(file_names, stage):
    files = ["version.glsl"]
    file_names = _process_includes(file_names)
    files.extend(file_names)
    return compileShader(
        "\n".join([string_from_file(f) for f in files]),
        stage)


def from_string(string, stage):
    return compileShader(inspect.cleandoc(string), stage)
