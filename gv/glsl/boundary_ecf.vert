layout (location = 0) in vec3 pos_ecf_in;  // vertex position
layout (location = 1) in vec3 v_inDir;  // vertex incoming direction
layout (location = 2) in vec3 v_outDir;  // vertex outgoing direction

flat out vec3 tc_inDir;
flat out vec3 tc_outDir;

void main()
{
    gl_Position = vec4(pos_ecf_in, 1);
    tc_inDir = v_inDir;
    tc_outDir = v_outDir;
}
