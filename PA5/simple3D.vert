attribute vec3 a_position;
attribute vec3 a_normal;

uniform mat4 u_model_matrix;
uniform mat4 u_view_matrix;
uniform mat4 u_projection_matrix;

uniform vec4 u_eye_pos;

varying vec3 v_frag_pos;     
varying vec3 v_normal;        

void main(void)
{
    // Transform position and normal to world space
    vec4 world_position = u_model_matrix * vec4(a_position, 1.0);
    vec4 world_normal = normalize(u_model_matrix * vec4(a_normal, 0.0));

    // Pass data to the fragment shader
    v_frag_pos = world_position.xyz;
    v_normal = world_normal.xyz;

    // Compute and output the final position
    gl_Position = u_projection_matrix * u_view_matrix * world_position;
}
